import json
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Deque, List, Optional, Set, Union

from cachetools import TTLCache
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session
from starlette.responses import RedirectResponse

from contaxy import config
from contaxy.config import settings
from contaxy.operations import (
    AuthOperations,
    JsonDocumentOperations,
    ProjectOperations,
    ServiceOperations,
)
from contaxy.operations.components import ComponentOperations
from contaxy.schema import AuthorizedAccess, TokenType, User, UserInput, UserRead
from contaxy.schema.auth import (
    AccessLevel,
    AccessToken,
    ApiToken,
    OAuth2Error,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    OAuthToken,
    OAuthTokenIntrospection,
    TokenPurpose,
    UserPermission,
    UserRegistration,
)
from contaxy.schema.exceptions import (
    ClientValueError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ResourceUpdateFailedError,
    UnauthenticatedError,
)
from contaxy.utils import auth_utils, id_utils
from contaxy.utils.id_utils import extract_ids_from_service_resource_name

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserPassword(BaseModel):
    hashed_password: str


class LoginIdMapping(BaseModel):
    user_id: str


class ResourcePermissions(BaseModel):
    permissions: List[str] = []


class AuthManager(AuthOperations):
    _USER_PASSWORD_COLLECTION = "passwords"
    _PERMISSION_COLLECTION = "permission"
    _API_TOKEN_COLLECTION = "tokens"
    _USER_COLLECTION = "users"
    _LOGIN_ID_MAPPING_COLLECTION = "login-id-mapping"
    _PROJECT_COLLECTION = "projects"

    def __init__(
        self,
        component_manager: ComponentOperations,
    ):
        """Initializes the Auth Manager.

        Args:
            component_manager: Instance of the component manager that grants access to the other managers.
        """
        self._global_state = component_manager.global_state
        self._request_state = component_manager.request_state
        self._component_manager = component_manager
        # TODO: move down?
        self._lock = threading.Lock()

    @property
    def _json_db_manager(self) -> JsonDocumentOperations:
        return self._component_manager.get_json_db_manager()

    @property
    def _service_manager(self) -> ServiceOperations:
        return self._component_manager.get_service_manager()

    def _get_verify_access_cache(self) -> TTLCache:
        """Returns a TTL (time to live) cache used by the access verification."""
        state_namespace = self._global_state[AuthManager]
        cache = state_namespace.verify_access_cache
        if cache is not None:
            return cache
        else:
            with self._lock:
                state_namespace.verify_access_cache = TTLCache(
                    maxsize=self._global_state.settings.VERIFY_ACCESS_CACHE_SIZE,
                    ttl=self._global_state.settings.VERIFY_ACCESS_CACHE_EXPIRY,
                )
                return state_namespace.verify_access_cache

    def _get_api_token_cache(self) -> TTLCache:
        """Returns a TTL (time to live) cache used for caching API token metadata."""
        state_namespace = self._global_state[AuthManager]
        cache = state_namespace.api_token_cache
        if cache is not None:
            return cache
        else:
            with self._lock:
                state_namespace.api_token_cache = TTLCache(
                    maxsize=self._global_state.settings.API_TOKEN_CACHE_SIZE,
                    ttl=self._global_state.settings.API_TOKEN_CACHE_EXPIRY,
                )
                return state_namespace.api_token_cache

    def _get_resource_permissions_cache(self) -> TTLCache:
        """Returns a TTL (time to live) cache used for caching permissions associated with resources."""
        state_namespace = self._global_state[AuthManager]
        cache = state_namespace.resource_permissions_cache
        if cache is not None:
            return cache
        else:
            with self._lock:
                state_namespace.resource_permissions_cache = TTLCache(
                    maxsize=self._global_state.settings.RESOURCE_PERMISSIONS_CACHE_SIZE,
                    ttl=self._global_state.settings.RESOURCE_PERMISSIONS_CACHE_EXPIRY,
                )
                return state_namespace.resource_permissions_cache

    def login_page(self) -> Optional[RedirectResponse]:
        return None

    def logout_session(self) -> RedirectResponse:
        # Remove login token of user from DB
        if (
            self._request_state.authorized_access
            and self._request_state.authorized_access.access_token
        ):
            self._json_db_manager.delete_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                self._API_TOKEN_COLLECTION,
                self._request_state.authorized_access.access_token.token,
            )
        # TODO: where to redirect to
        rr = RedirectResponse("/welcome", status_code=307)
        rr.delete_cookie(config.API_TOKEN_NAME)
        rr.delete_cookie(config.AUTHORIZED_USER_COOKIE)
        return rr

    def _create_session_token(
        self,
        token_subject: str,
        scopes: List[str],
        expiry_minutes: Optional[timedelta] = None,
    ) -> str:

        if expiry_minutes:
            expire = datetime.now(timezone.utc) + expiry_minutes
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.settings.JWT_TOKEN_EXPIRY_MINUTES
            )

        return jwt.encode(
            claims={
                "sub": token_subject,
                # TODO: "iss"
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "scope": scopes,
            },
            key=config.settings.JWT_TOKEN_SECRET,
            algorithm=config.settings.JWT_ALGORITHM,
        )

    def create_token(
        self,
        scopes: List[str],
        token_type: TokenType,
        description: Optional[str] = None,
        token_purpose: Optional[str] = None,
        token_subject: Optional[str] = None,
    ) -> str:
        if not token_subject:
            if (
                self._request_state.authorized_access
                and self._request_state.authorized_access.authorized_subject
            ):
                # Get token subject from authorized subject info
                token_subject = self._request_state.authorized_access.authorized_subject
            else:
                raise UnauthenticatedError("No token subject found for token creation.")

        if token_type is token_type.SESSION_TOKEN:
            # Check if token for service is requested and update service last access time
            for scope in scopes:
                try:
                    resource, _ = auth_utils.parse_permission(scope)
                    project_id, service_id = extract_ids_from_service_resource_name(
                        resource
                    )
                    self._service_manager.update_service_access(project_id, service_id)
                except ValueError:
                    pass

            # Create session token if selected
            return self._create_session_token(token_subject, scopes)

        token = id_utils.generate_token(config.settings.API_TOKEN_LENGTH)
        api_token = ApiToken(
            token=token,
            token_type=token_type,
            subject=token_subject,
            scopes=scopes,
            created_at=datetime.now(timezone.utc),
            description=description,
            token_purpose=token_purpose,
            # TODO: created_by
            # TODO: expires_at
        )

        self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._API_TOKEN_COLLECTION,
            key=token,
            json_document=api_token.json(),
        )
        return token

    def list_api_tokens(self, token_subject: Optional[str] = None) -> List[ApiToken]:
        # Filter all resources for the provided permission
        filtered_token_docs = self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT,
            self._API_TOKEN_COLLECTION,
            filter=f'$.subject ==  "{token_subject}"',
            # TODO: $.subject ==  "{token_subject}"  inmemory: $[? (@.subject ==  "{token_subject}")]'
        )

        api_tokens: List[ApiToken] = []
        for token_doc in filtered_token_docs:
            api_token = ApiToken.parse_raw(token_doc.json_value)
            # Check here again for subject
            if api_token.subject == token_subject:
                api_tokens.append(api_token)

        return api_tokens

    def _get_api_token_from_db(self, token: str) -> ApiToken:
        """Returns the API token metadata from the database.

        Args:
            token: The API token.

        Raises:
            ResourceNotFoundError: If the token does not exist in the DB.
        """
        token_doc = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._API_TOKEN_COLLECTION,
            token,
        )
        return ApiToken.parse_raw(token_doc.json_value)

    def _resolve_token(self, token: str, use_cache: bool) -> AccessToken:
        """Resolves the provided token to its metadata.

        Args:
            token: An API or session token.
            use_cache: If `False`, the token resolving will not use any cache.

        Raises:
            UnauthenticatedError: If the token is not valid
        """
        if auth_utils.is_jwt_token(token):
            try:
                payload = jwt.decode(
                    token,
                    config.settings.JWT_TOKEN_SECRET,
                    algorithms=[config.settings.JWT_ALGORITHM],
                )
                return AccessToken(
                    token=token,
                    token_type=TokenType.SESSION_TOKEN,
                    subject=payload.get("sub"),
                    scopes=payload.get("scope"),
                    expires_at=datetime.fromtimestamp(
                        payload.get("exp"), tz=timezone.utc
                    ),
                    created_at=datetime.fromtimestamp(
                        payload.get("iat"), tz=timezone.utc
                    ),
                )

            except JWTError as ex:
                raise UnauthenticatedError("Session token is not valid.") from ex

        if not use_cache or not self._global_state.settings.API_TOKEN_CACHE_ENABLED:
            # Do not use cache
            try:
                return self._get_api_token_from_db(token)
            except ResourceNotFoundError as ex:
                raise UnauthenticatedError(
                    message="The provided API token does not exist in the database."
                ) from ex

        cache = self._get_api_token_cache()
        cache_key = token
        token_metadata: Optional[AccessToken] = None
        if cache_key in cache:
            token_metadata = cache[cache_key]
        else:
            # lock thread if item is updated
            with self._lock:
                try:
                    # Add the verification result to the cache
                    token_metadata = self._get_api_token_from_db(token)
                except ResourceNotFoundError:
                    token_metadata = None
                # Store token in cache, even if None
                cache[cache_key] = token_metadata

        if not token_metadata:
            raise UnauthenticatedError(
                message="The provided API token does not exist in the database."
            )

        return token_metadata

    def _verify_access_via_db(
        self, token: AccessToken, permission: str, use_cache: bool
    ) -> AuthorizedAccess:
        scope_grants_access = False
        for scope in token.scopes:

            if not auth_utils.is_valid_permission(scope):
                logger.warning(f"The token scope ({scope}) is not valid.")
                continue

            # Check if the token scope grants access to the requested permission
            if auth_utils.is_permission_granted(scope, permission):
                scope_grants_access = True
                break

        if not scope_grants_access:
            raise PermissionDeniedError(
                "The authorized token does not have the required scope."
            )

        # Check if the token subject has the required permission
        token_subject_permissions = self.list_permissions(
            token.subject, resolve_roles=True, use_cache=use_cache
        )
        for token_subject_permission in token_subject_permissions:
            if auth_utils.is_permission_granted(token_subject_permission, permission):
                # The token subject (= usually user) is granted the requested permission
                resource_name, access_level = auth_utils.parse_permission(permission)
                return AuthorizedAccess(
                    authorized_subject=token.subject,
                    resource_name=resource_name,
                    access_level=access_level,
                    access_token=token,
                )

        raise PermissionDeniedError(
            "The token subject does not have the required permission."
        )

    def verify_access(
        self, token: str, permission: Optional[str] = None, use_cache: bool = True
    ) -> AuthorizedAccess:
        # This will throw an UnauthenticatedError if the token is not valid or does not exist
        resolved_token = self._resolve_token(token, use_cache=use_cache)
        if not permission or settings.DEBUG_DEACTIVATE_VERIFICATION:
            # no permissions to check -> return granted permission
            return AuthorizedAccess(
                authorized_subject=resolved_token.subject,
                access_token=resolved_token,
            )
        if not use_cache or not self._global_state.settings.VERIFY_ACCESS_CACHE_ENABLED:
            # Do not use cache
            return self._verify_access_via_db(
                resolved_token, permission, use_cache=use_cache
            )

        cache = self._get_verify_access_cache()
        cache_key = token + "-perm-" + str(permission)
        if cache_key in cache:
            return cache[cache_key]
        else:
            # lock thread if item is updated
            with self._lock:
                # Add the verification result to the cache
                verification_result = self._verify_access_via_db(
                    resolved_token, permission, use_cache=use_cache
                )
                cache[cache_key] = verification_result
                return verification_result

    def change_password(
        self,
        user_id: str,
        password: str,
    ) -> None:
        user_password = UserPassword(hashed_password=PWD_CONTEXT.hash(password))

        # TODO: salt and hash the user id to make it more complicated to link the password to a user

        # This method creteas or overwrites the
        self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._USER_PASSWORD_COLLECTION,
            user_id,
            user_password.json(),
        )

    def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool:
        """Verifies a password of a specified user.

        The password is stored as a hash

        Args:
            user_id: The ID of the user.
            password: The password to check. This can also be specified as a hash.

        Returns:
            bool: `True` if the password matches the stored password.
        """
        password_document = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._USER_PASSWORD_COLLECTION, user_id
        )

        user_password = UserPassword.parse_raw(password_document.json_value)
        return PWD_CONTEXT.verify(password, user_password.hashed_password)

    # Permission Operations

    def _get_resource_permissions_from_db(
        self, resource_name: str
    ) -> ResourcePermissions:
        permission_doc = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._PERMISSION_COLLECTION,
            resource_name,
        )
        return ResourcePermissions.parse_raw(permission_doc.json_value)

    def add_permission(
        self,
        resource_name: str,
        permission: str,
    ) -> None:
        resource_permission = ResourcePermissions()
        try:
            # Try to get the permission document
            resource_permission = self._get_resource_permissions_from_db(resource_name)
        except ResourceNotFoundError:
            # Ignore error, create a new resource
            pass

        # Add permissions to the document
        resource_permission.permissions.append(permission)
        # TODO: at this point there - theoretically - could be a data inconsitency if the same item is updated at the exact same time
        # Create/or update document
        self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._PERMISSION_COLLECTION,
            resource_name,
            resource_permission.json(),
            upsert=True,
        )

        # Test if permission was applied with short timeout (to wait for conflicting updates)
        # It is very unlikely that the resource update fails
        time.sleep(0.005)
        try:
            resource_permissions = self._get_resource_permissions_from_db(resource_name)

            if permission not in resource_permissions.permissions:
                raise ResourceUpdateFailedError(
                    message=f"Unable to add permission ({permission}) for {resource_name}. Try again.",
                    explanation="The permission was not added to the resource.",
                    resource=resource_name,
                )
        except ResourceNotFoundError as ex:
            raise ResourceUpdateFailedError(
                message=f"Unable to add permission ({permission}) for {resource_name}. Try again. 2",
                explanation="The resource did not exist anymore after the update.",
                resource=resource_name,
            ) from ex
        logger.debug(
            f"Successfully added new permission {permission} to resource {resource_name}."
        )

    def remove_permission(
        self, resource_name: str, permission: str, remove_sub_permissions: bool = False
    ) -> None:
        try:
            # Try to get the permission document
            resource_permission = self._get_resource_permissions_from_db(resource_name)
            updated_permissions = []
            removed_permissions = []
            # Iterate all permissions granted to the resource
            for granted_permission in resource_permission.permissions:
                if permission == granted_permission:
                    # Permission matched granted permission -> Ignore/remove this permission
                    removed_permissions.append(permission)
                    continue

                if (
                    remove_sub_permissions
                    and auth_utils.is_valid_permission(
                        granted_permission
                    )  # Only if it is a valid permission and not a role
                    and auth_utils.is_permission_granted(permission, granted_permission)
                ):
                    # Ignore/remove this permission since it is a subpermission
                    removed_permissions.append(permission)
                    continue
                updated_permissions.append(granted_permission)

            # Create/or update document
            self._json_db_manager.create_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                self._PERMISSION_COLLECTION,
                resource_name,
                ResourcePermissions(permissions=updated_permissions).json(),
                upsert=True,
            )

            # Test if permission was applied with short timeout (to wait for conflicting updates)
            # It is very unlikely that the resource update fails
            time.sleep(0.001)
            try:
                resource_permissions = self._get_resource_permissions_from_db(
                    resource_name
                )
                for removed_permission in removed_permissions:
                    if removed_permission in resource_permissions.permissions:
                        raise ResourceUpdateFailedError(
                            message=f"Unable to remove permission ({permission}) for {resource_name}. Try again.",
                            explanation=f"The permission {removed_permission} was not removed during the update.",
                            resource=resource_name,
                        )
            except ResourceNotFoundError:
                # Ignore this
                pass

        except ResourceNotFoundError as ex:
            # Ignore error, create a new resource
            raise ResourceUpdateFailedError(
                message=f"Unable to remove permission ({permission}) for {resource_name}. Try again.",
                explanation="The resource does not have any permissions.",
                resource=resource_name,
            ) from ex

    def _list_permissions_from_db(
        self, resource_name: str, resolve_roles: bool = True
    ) -> List[str]:
        try:
            resource_permissions = self._get_resource_permissions_from_db(resource_name)
            permissions = resource_permissions.permissions

            if not permissions:
                return []

            if not resolve_roles:
                return permissions

            # resolve roles: Permissions can have a hierachy based on roles which needs to be resolved
            checked_permissions: Set[str] = set()  # used to prevent recursive loops
            permissions_to_resolve: Deque[str] = deque()  # queu of permissions to check
            resolved_permissions: Set[str] = set()  # all resolved base permissions

            permissions_to_resolve.extend(permissions)
            while permissions_to_resolve:
                permission = permissions_to_resolve.popleft()
                if permission in checked_permissions:
                    continue

                checked_permissions.add(permission)
                if auth_utils.is_valid_permission(permission):
                    resolved_permissions.add(permission)
                else:
                    try:
                        # Probably a role / permission collection -> resolve permissions and add to list
                        permissions_to_resolve.extend(
                            self._get_resource_permissions_from_db(
                                permission
                            ).permissions
                        )
                    except ResourceNotFoundError:
                        logger.warning(
                            f"Failed to resolve permission {permission}",
                        )
            return list(resolved_permissions)

        except ResourceNotFoundError:
            # TODO raise error?
            return []

    def list_permissions(
        self, resource_name: str, resolve_roles: bool = True, use_cache: bool = False
    ) -> List[str]:
        if not use_cache or not config.settings.RESOURCE_PERMISSIONS_CACHE_ENABLED:
            return self._list_permissions_from_db(resource_name, resolve_roles)

        # Load via cache
        cache = self._get_resource_permissions_cache()
        cache_key = resource_name
        if cache_key in cache:
            return cache[cache_key]
        else:
            # lock thread if item is updated
            with self._lock:
                # Add the verification result to the cache
                resource_permissions = self._list_permissions_from_db(
                    resource_name, resolve_roles
                )
                cache[cache_key] = resource_permissions
                return resource_permissions

    def list_resources_with_permission(
        self, permission: str, resource_name_prefix: Optional[str] = None
    ) -> List[str]:
        # Filter all resources for the provided permission
        filtered_resource_docs = self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT,
            self._PERMISSION_COLLECTION,
            filter=f'$.permissions[*] ? (@=="{permission}")',
            # TODO: - inmemory: $[*].permissions[?(@=="{permission}")]
        )

        resource_names: Set[str] = set()
        for resource_doc in filtered_resource_docs:
            # The key of the resource doc is supposed to be the resource name
            resource_name = resource_doc.key
            if (
                permission
                not in ResourcePermissions.parse_raw(
                    resource_doc.json_value
                ).permissions
            ):
                continue
            if (not resource_name_prefix) or resource_name.startswith(
                resource_name_prefix
            ):
                resource_names.add(resource_name)
        return list(resource_names)

    # OAuth Opertions
    def request_token(
        self, token_request_form: OAuth2TokenRequestFormNew
    ) -> OAuthToken:
        if token_request_form.grant_type != OAuth2TokenGrantTypes.PASSWORD:
            # Only the password grant type is currently implemented.
            raise OAuth2Error(error="invalid_grant")

        if not token_request_form.username or not token_request_form.password:
            raise OAuth2Error("invalid_request")
        try:
            user_id = self._get_user_id_by_login_id(token_request_form.username)
            if not self.verify_password(user_id, token_request_form.password):
                raise OAuth2Error("unauthorized_client")

            return self._generate_token(user_id, token_request_form.scope)

        except ResourceNotFoundError as ex:
            # The user was not found in the system
            raise OAuth2Error("unauthorized_client") from ex

    def _generate_token(
        self, user_id: str, scopes: Union[str, List[str], None] = None
    ) -> OAuthToken:
        if not scopes:
            # Default user token is allowed to do everything
            scopes = [auth_utils.construct_permission("*", AccessLevel.ADMIN)]
        elif isinstance(scopes, str):
            scopes = scopes.split()
        token = self.create_token(
            token_subject="users/" + user_id,
            scopes=scopes,
            token_type=TokenType.API_TOKEN,
            token_purpose=TokenPurpose.LOGIN_TOKEN,
            description=f"Login token for user {user_id}.",
        )

        # TODO: change this here if we validated token scopes
        granted_scopes = " ".join(scopes)

        return OAuthToken(token_type="bearer", access_token=token, scope=granted_scopes)

    def revoke_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> None:
        if auth_utils.is_jwt_token(token):
            raise OAuth2Error(error="unsupported_token_type")

        try:
            self._json_db_manager.delete_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=self._API_TOKEN_COLLECTION,
                key=token,
            )
            return
        except ResourceNotFoundError:
            # Based on the Oauth standard, nothing needs to be done here.
            logger.warning("The token does not exist in the database.")
        return

    def introspect_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> OAuthTokenIntrospection:
        try:
            resolved_token = self._resolve_token(token, use_cache=False)
            iat = None
            if resolved_token.created_at:
                iat = int(resolved_token.created_at.timestamp())  # TODO: check timezone

            exp = None
            if resolved_token.expires_at:
                exp = int(resolved_token.expires_at.timestamp())  # TODO: check timezone

            return OAuthTokenIntrospection(
                active=True,
                scope=" ".join(resolved_token.scopes),
                sub=resolved_token.subject,
                iat=iat,
                exp=exp,
                # TODO: fill other fields
            )
        except UnauthenticatedError:
            # Based on the standard, return the introspection object as inactive
            return OAuthTokenIntrospection(active=False)

    def login_callback(
        self,
        code: str,
        redirect_uri: str,
        project_manager: ProjectOperations,
        state: Optional[str] = None,
    ) -> OAuthToken:
        """Implements the OAuth2 / OICD callback to finish the login process.

        The authorization `code` is exchanged for an access and ID token.
        The ID token contains all relevant user information and is used to login the user.
        If the user does not exist, a new user will be created with the information from the ID token.

        This operation implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.

        Args:
            code: The authorization code generated by the authorization server.
            redirect_uri: The redirect uri used for the OICD authorization flow.
            project_manager: Project manager required for creating new users
            state (optional): An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery.

        Raises:
            UnauthenticatedError: If the `code` could not be used to get an ID token.

        Returns:
            RedirectResponse: A redirect to the webapp that has valid access tokens attached.
        """
        session = OAuth2Session(
            config.settings.OIDC_CLIENT_ID,
            state=state,
            redirect_uri=redirect_uri,
        )

        token = session.fetch_token(
            config.settings.OIDC_TOKEN_URL,
            code,
            client_secret=config.settings.OIDC_CLIENT_SECRET,
        )

        token_payload = jwt.get_unverified_claims(token.get("id_token"))
        email = token_payload.get("email")
        assert email  # TODO
        if not token_payload.get("email_verified"):
            # ? Prevent
            logger.warning(f"The email {email} is not verified")
        try:
            user_id = self._get_user_id_by_login_id(email)
        except ResourceNotFoundError:
            if config.settings.USER_REGISTRATION_ENABLED:
                user = auth_utils.create_and_setup_user(
                    user_input=UserRegistration(email=email),
                    auth_manager=self,
                    project_manager=project_manager,
                )
                user_id = user.id
            else:
                raise PermissionDeniedError(
                    f"No existing account for {email} found! Please contact an administrator."
                )

        return self._generate_token(user_id)

    # User Operations

    def list_users(
        self,
        access_level: Optional[AccessLevel] = None,
    ) -> List[Union[User, UserRead]]:
        """Lists all users.

        TODO: Filter based on authenticated user?

        Returns:
            List[User]: List of users.
        """
        user_list: List[Union[User, UserRead]] = []
        for json_document in self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT, self._USER_COLLECTION
        ):
            if access_level == AccessLevel.ADMIN:
                user_list.append(User.parse_raw(json_document.json_value))
            elif access_level == AccessLevel.READ:
                user_list.append(UserRead.parse_raw(json_document.json_value))
        return user_list

    def _create_login_id_mapping(self, login_id: str, user_id: str) -> None:
        if self._login_id_exists(login_id):
            raise ResourceAlreadyExistsError(
                f"A login id mapping with {login_id} already exists."
            )
        processed_login_id = login_id.lower().strip()
        try:
            self._json_db_manager.create_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=self._LOGIN_ID_MAPPING_COLLECTION,
                key=processed_login_id,
                json_document=LoginIdMapping(user_id=user_id).json(),
                upsert=False,  # Only create, no updates
            )
        except ResourceAlreadyExistsError:
            pass

    def _get_user_id_by_login_id(self, login_id: str) -> str:
        processed_login_id = login_id.lower().strip()
        login_id_mapping_doc = self._json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._LOGIN_ID_MAPPING_COLLECTION,
            key=processed_login_id,
        )

        return LoginIdMapping.parse_raw(login_id_mapping_doc.json_value).user_id

    def _login_id_exists(self, login_id: str) -> bool:
        try:
            self._get_user_id_by_login_id(login_id)
            return True
        except ResourceNotFoundError:
            return False

    def create_user(
        self, user_input: UserRegistration, technical_user: bool = False
    ) -> User:
        """Creates a user.

        If only the email is given then a username will be derived based on the email address.

        Args:
            user_input: The user data to create the new user.
            technical_user: If `True`, the created user will be marked as technical user. Defaults to `False`.

        Raises:
            ResourceAlreadyExistsError: If a user with the same username or email already exists.

        Returns:
            User: The created user information.
        """
        logger.debug(f"User creation request for UserRegistration({user_input}).")
        user_id = id_utils.generate_short_uuid()
        has_password = bool(user_input.password)

        if user_input.password:
            self.change_password(user_id, user_input.password)  # .get_secret_value()
            del user_input.password

        if user_input.username and id_utils.is_email(user_input.username):
            raise ClientValueError(
                f"The username ({user_input.username}) is not allowed to contain an email address."
            )

        if user_input.email and id_utils.is_email(user_input.email) is False:
            raise ClientValueError(
                f"The email ({user_input.email}) MUST contain a valid email address."
            )

        user = User(
            id=user_id,
            technical_user=technical_user,
            has_password=has_password,
            **user_input.dict(exclude_unset=True),
        )

        # Check if username already exists
        if user.username and self._login_id_exists(user.username):
            raise ResourceAlreadyExistsError(
                f"The user with username {user.username} already exists."
            )

        # Check if email already exists
        if user.email and self._login_id_exists(user.email):
            raise ResourceAlreadyExistsError(
                f"The user with email {user.email} already exists."
            )

        if user.email and not user.username:
            user.username = self._propose_username(user.email)

        # TODO: roll back mappings if user creation fails?
        if user.username:
            self._create_login_id_mapping(user.username, user_id)

        if user.email:
            self._create_login_id_mapping(user.email, user_id)

        created_document = self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
            json_document=user.json(),
        )
        user = User.parse_raw(created_document.json_value)
        logger.debug(f"Successfully created User({user}).")
        return user

    def get_user(self, user_id: str) -> User:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information.
        """
        json_document = self._json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
        )
        return User.parse_raw(json_document.json_value)

    def get_user_with_permission(self, user_id: str) -> UserPermission:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information.
        """
        json_document = self._json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
        )
        return UserPermission.parse_raw(json_document.json_value)

    def update_user(self, user_id: str, user_input: UserInput) -> User:
        """Updates the user metadata.

        This will update only the properties that are explicitly set in the `user_input`.
        The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).

        Args:
            user_id (str): The ID of the user.
            user_input (UserInput): The user data used to update the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The updated user information.
        """
        # TODO: Ensure username and email don't exist and update login-id-mapping
        updated_document = self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
            json_document=user_input.json(exclude_unset=True),
        )
        return User.parse_raw(updated_document.json_value)

    def update_user_last_activity_time(self, user_id: str) -> None:
        self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=AuthManager._USER_COLLECTION,
            key=user_id,
            json_document=json.dumps(
                {"last_activity": str(datetime.now(timezone.utc))}
            ),
        )

    def delete_user(self, user_id: str) -> None:
        """Deletes a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.
        """
        try:
            self._json_db_manager.delete_json_document(
                config.SYSTEM_INTERNAL_PROJECT, self._USER_COLLECTION, user_id
            )
        except ResourceNotFoundError:
            logger.warning(
                f"ResourceNotFoundError: No JSON document was found in the users table with the given key: {user_id}."
            )

        try:
            self._json_db_manager.delete_json_document(
                config.SYSTEM_INTERNAL_PROJECT, self._USER_PASSWORD_COLLECTION, user_id
            )
        except ResourceNotFoundError:
            logger.warning(
                f"ResourceNotFoundError: No JSON document was found in the password table with the given key: {user_id}."
            )

        user_resource_name = "users/" + user_id
        try:
            self._json_db_manager.delete_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                self._PERMISSION_COLLECTION,
                user_resource_name,
            )
        except ResourceNotFoundError:
            logger.warning(
                f"ResourceNotFoundError: No JSON document was found in the permissions table with the given key: {user_id}."
            )

        try:
            for token_doc in self._json_db_manager.list_json_documents(
                config.SYSTEM_INTERNAL_PROJECT, self._API_TOKEN_COLLECTION
            ):
                token_subject = ApiToken.parse_raw(token_doc.json_value).subject
                if token_subject == user_resource_name:
                    self._json_db_manager.delete_json_document(
                        config.SYSTEM_INTERNAL_PROJECT,
                        self._API_TOKEN_COLLECTION,
                        token_doc.key,
                    )
        except ResourceNotFoundError:
            logger.warning(
                f"ResourceNotFoundError: No JSON document was found in the token table with the given key: {user_id}."
            )

        try:
            for login_mapping_doc in self._json_db_manager.list_json_documents(
                config.SYSTEM_INTERNAL_PROJECT, self._LOGIN_ID_MAPPING_COLLECTION
            ):
                mapped_user_id = LoginIdMapping.parse_raw(
                    login_mapping_doc.json_value
                ).user_id
                if mapped_user_id == user_id:
                    self._json_db_manager.delete_json_document(
                        config.SYSTEM_INTERNAL_PROJECT,
                        self._LOGIN_ID_MAPPING_COLLECTION,
                        login_mapping_doc.key,
                    )
        except ResourceNotFoundError:
            logger.warning(
                f"ResourceNotFoundError: No JSON document was found in the loginID table with the given key: {user_id}."
            )

    def _propose_username(self, email: str) -> str:
        MAX_RETRIES = 10000
        username = email.split("@")[0]
        if not self._login_id_exists(username):
            return username

        for i in range(1, MAX_RETRIES):
            username = f"{username}-{i}"
            if not self._login_id_exists(username):
                return username

        logger.critical(
            f"Damn! Username cannot be inferred from email {email}. {MAX_RETRIES} combinations tried."
        )
        return ""

    def get_user_token(
        self, user_id: str, access_level: AccessLevel = AccessLevel.WRITE
    ) -> str:
        # Provide access to all resources from the user
        user_token_scope = auth_utils.construct_permission("*", access_level)

        # Check if a user token for this user was already created
        user_resource = f"users/{user_id}"
        tokens = self.list_api_tokens(token_subject=user_resource)
        try:
            return next(
                (
                    token
                    for token in tokens
                    if token.token_purpose == TokenPurpose.USER_API_TOKEN
                    if token.scopes == [user_token_scope]
                )
            ).token
        except StopIteration:
            return self.create_token(
                scopes=[user_token_scope],
                token_type=TokenType.API_TOKEN,
                token_subject=user_resource,
                token_purpose=TokenPurpose.USER_API_TOKEN,
                description=f"{access_level} token for user {user_id}.",
            )

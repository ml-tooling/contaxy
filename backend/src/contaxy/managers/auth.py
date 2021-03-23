import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Deque, List, Optional, Set

from cachetools import TTLCache
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from contaxy import config
from contaxy.operations import AuthOperations, JsonDocumentOperations
from contaxy.schema import AuthorizedAccess, TokenType, User, UserInput
from contaxy.schema.auth import (
    AccessToken,
    ApiToken,
    OAuth2Error,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestForm,
    OAuthToken,
    OAuthTokenIntrospection,
    OpenIDUserInfo,
    TokenPurpose,
    UserRegistration,
)
from contaxy.schema.exceptions import (
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ResourceUpdateFailedError,
    ServerBaseError,
    UnauthenticatedError,
)
from contaxy.utils import auth_utils, id_utils
from contaxy.utils.state_utils import GlobalState, RequestState

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserPassword(BaseModel):
    hashed_password: str


class UsernameIdMapping(BaseModel):
    user_id: str


class ResourcePermissions(BaseModel):
    permissions: List[str] = []


class AuthManager(AuthOperations):

    _USER_PASSWORD_COLLECTION = "passwords"
    _PERMISSION_COLLECTION = "permission"
    _API_TOKEN_COLLECTION = "tokens"
    _USER_COLLECTION = "users"
    _USERNAME_ID_MAPPING_COLLECTION = "username-id-mapping"

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the Auth Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self._global_state = global_state
        self._request_state = request_state
        self._json_db_manager = json_db_manager
        # TODO: move down?
        self._lock = threading.Lock()

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

    def login_page(self) -> RedirectResponse:
        pass

    def logout_session(self) -> RedirectResponse:
        pass

    def _create_session_token(
        self,
        token_subject: str,
        scopes: List[str],
        expiry_minutes: Optional[timedelta] = None,
    ) -> str:

        if expiry_minutes:
            expire = datetime.utcnow() + expiry_minutes
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=config.settings.JWT_TOKEN_EXPIRY_MINUTES
            )

        return jwt.encode(
            claims={
                "sub": token_subject,
                # TODO: "iss"
                "exp": expire,
                "iat": datetime.utcnow(),
                "scope": scopes,
            },
            key=config.settings.JWT_TOKEN_SECRET,
            algorithm=config.settings.JWT_ALGORITHM,
        )

    def create_token(
        self,
        token_subject: str,
        scopes: List[str],
        token_type: TokenType,
        description: Optional[str] = None,
        token_purpose: Optional[TokenPurpose] = None,
    ) -> str:
        if token_type is token_type.SESSION_TOKEN:
            # Create session token if selected
            return self._create_session_token(token_subject, scopes)

        token = id_utils.generate_token(config.settings.API_TOKEN_LENGTH)
        api_token = ApiToken(
            token=token,
            token_type=token_type,
            subject=token_subject,
            scopes=scopes,
            created_at=datetime.today(),
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

    def list_api_tokens(self, token_subject: str) -> List[ApiToken]:
        # Filter all resources for the provided permission
        filtered_token_docs = self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT,
            self._API_TOKEN_COLLECTION,
            filter=f'$[? (@.subject ==  "{token_subject}")]',  # TODO: $.subject ==  "{token_subject}"
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
                    expires_at=datetime.utcfromtimestamp(
                        payload.get("exp")
                    ),  # TODO: check
                    created_at=datetime.utcfromtimestamp(
                        payload.get("iat")
                    ),  # TODO: check
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
        # This will thows UnauthenticatedError if the token is not valid or does not existx
        resolved_token = self._resolve_token(token, use_cache=use_cache)
        if not permission:
            # no permissions to check -> return granted permission
            return AuthorizedAccess(
                authorized_subject=resolved_token.subject, access_token=resolved_token
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
        )

        # Test if permission was applied with short timeout (to wait for conflicting updates)
        # It is very unlikely that the resource update fails
        time.sleep(0.01)
        try:
            resource_permissions = self._get_resource_permissions_from_db(resource_name)

            if permission not in resource_permissions.permissions:
                raise ResourceUpdateFailedError(
                    message=f"Unable to update the permissions for {resource_name}. Try again.",
                    explanation="The permission was not added to the resource.",
                    resource=resource_name,
                )
        except ResourceNotFoundError as ex:
            raise ResourceUpdateFailedError(
                message=f"Unable to update the permissions for {resource_name}. Try again.",
                explanation="The resource did not exist anymore after the update.",
                resource=resource_name,
            ) from ex

    def remove_permission(
        self, resource_name: str, permission: str, apply_as_prefix: bool = False
    ) -> None:
        # TODO: Remove all sub permissions
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
                if apply_as_prefix and auth_utils.is_permission_granted(
                    permission, granted_permission
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
            )

            # Test if permission was applied with short timeout (to wait for conflicting updates)
            # It is very unlikely that the resource update fails
            time.sleep(0.01)
            try:
                resource_permissions = self._get_resource_permissions_from_db(
                    resource_name
                )
                for removed_permission in removed_permissions:
                    if removed_permission in resource_permissions.permissions:
                        raise ResourceUpdateFailedError(
                            message=f"Unable to update the permissions for {resource_name}. Try again.",
                            explanation=f"The permission {removed_permission} was not removed during the update.",
                            resource=resource_name,
                        )
            except ResourceNotFoundError:
                # Ignore this
                pass

        except ResourceNotFoundError as ex:
            # Ignore error, create a new resource
            raise ResourceUpdateFailedError(
                message=f"Unable to update the permissions for {resource_name}.",
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

        # TODO: check json path expression
        # Filter all resources for the provided permission
        filtered_resource_docs = self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT,
            self._PERMISSION_COLLECTION,
            filter=f'$[*].permissions[?(@=="{permission}")]',  # TODO: $.permissions[*] ? (@=="{permission}")
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
            if resource_name_prefix and resource_name.startswith(resource_name_prefix):
                resource_names.add(resource_name)
            else:
                resource_names.add(resource_name)
        return list(resource_names)

    # OAuth Opertions
    def request_token(self, token_request_form: OAuth2TokenRequestForm) -> OAuthToken:
        """Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters.

        The token endpoint is used by the client to obtain an access token by
        presenting its authorization grant or refresh token.

        The token endpoint supports the following grant types:
        - [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token.
            - `grant_type` must be set to `password`
            - `username` (required): The user’s username.
            - `password` (required): The user’s password.
            - `scope` (optional): Optional requested scope values for the access token.
        - [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens.
            - `grant_type` must be set to `refresh_token`
            - `refresh_token` (required): The refresh token previously issued to the client.
            - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope.
        - [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client
        credentials.
            - `grant_type` must be set to `client_credentials`
            - `scope` (optional): Optional requested scope values for the access token.
            - Client Authentication required (e.g. via client_id and client_secret or auth header)
        - [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint.
            - `grant_type` must be set to `authorization_code`
            - `code` (required): The authorization code that the client previously received from the authorization server.
            - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request.
            - Client Authentication required (e.g. via client_id and client_secret or auth header)

        For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow.
        For the authorization code flow, calling this endpoint is the second step of the flow.

        This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2).

        Args:
            token_request_form: The request instructions.

        Returns:
            OAuthToken: The access token and additonal metadata (depending on the grant type).
        """
        if token_request_form.grant_type != OAuth2TokenGrantTypes.PASSWORD:
            # Only the password grant type is currently implemented.
            raise OAuth2Error(error="invalid_grant")

        if not token_request_form.username or not token_request_form.password:
            raise OAuth2Error("invalid_request")
        try:
            user_id = self._get_id_by_username(token_request_form.username)
            if not self.verify_password(user_id, token_request_form.password):
                raise OAuth2Error("unauthorized_client")

            token = self.create_token(
                "users/" + user_id,
                scopes=token_request_form.scopes,
                token_type=TokenType.API_TOKEN,
                description="Login Token.",
            )

            # TODO: change this here if we validated token scopes
            granted_scopes = " ".join(token_request_form.scopes)

            return OAuthToken(
                token_type="bearer", access_token=token, scope=granted_scopes
            )
        except ResourceNotFoundError as ex:
            # The user was not found in the system
            raise OAuth2Error("invalid_request") from ex

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

    def get_userinfo(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> OpenIDUserInfo:
        raise ServerBaseError("Not Implemented!")

    def login_callback(
        self,
        code: str,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        rr = RedirectResponse("/webapp", status_code=307)
        rr.set_cookie(key="session_token", value="test-token")
        rr.set_cookie(key="refresh-token", value="test-refresh-token")
        return rr

    # User Operations

    def list_users(self) -> List[User]:
        """Lists all users.

        TODO: Filter based on authenticated user?

        Returns:
            List[User]: List of users.
        """
        user_list: List[User] = []
        for json_document in self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT, self._USER_COLLECTION
        ):
            user_list.append(User.parse_raw(json_document.json_value))
        return user_list

    def _create_username_mapping(self, username: str, user_id: str) -> None:
        if self._username_exists(username=username):
            raise ResourceAlreadyExistsError(
                f"A username mapping with username {username} already exists."
            )
        processed_username = username.lower().strip()
        self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USERNAME_ID_MAPPING_COLLECTION,
            key=processed_username,
            json_document=UsernameIdMapping(user_id=user_id).json(),
        )

    def _get_id_by_username(self, username: str) -> str:
        processed_username = username.lower().strip()
        username_id_mapping_doc = self._json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USERNAME_ID_MAPPING_COLLECTION,
            key=processed_username,
        )

        return UsernameIdMapping.parse_raw(username_id_mapping_doc.json_value).user_id

    def _username_exists(self, username: str) -> bool:
        try:
            self._get_id_by_username(username)
            return True
        except ResourceNotFoundError:
            return False

    def create_user(
        self, user_input: UserRegistration, technical_user: bool = False
    ) -> User:
        """Creates a user.

        Args:
            user_input: The user data to create the new user.
            technical_user: If `True`, the created user will be marked as technical user. Defaults to `False`.

        Raises:
            ResourceAlreadyExistsError: If a user with the same username or email already exists.

        Returns:
            User: The created user information.
        """
        user_id = id_utils.generate_short_uuid()

        if user_input.password:
            self.change_password(user_id, user_input.password.get_secret_value())
            del user_input.password

        user = User(
            id=user_id,
            technical_user=technical_user,
            created_at=datetime.now(),
            **user_input.dict(exclude_unset=True),
        )

        # Check if username already exists
        if user.username and self._username_exists(user.username):
            raise ResourceAlreadyExistsError(
                f"The user with username {user.username} already exists."
            )

        # Check if email already exists
        if user.email and self._username_exists(user.email):
            raise ResourceAlreadyExistsError(
                f"The user with email {user.email} already exists."
            )

        # TODO: roll back mappings if user creation fails?
        if user.username:
            self._create_username_mapping(user.username, user_id)

        if user.email:
            self._create_username_mapping(user.email, user_id)

        created_document = self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
            json_document=user.json(),
        )

        return User.parse_raw(created_document.json_value)

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
        updated_document = self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._USER_COLLECTION,
            key=user_id,
            json_document=user_input.json(exclude_unset=True),
        )
        return User.parse_raw(updated_document.json_value)

    def delete_user(self, user_id: str) -> None:
        """Deletes a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.
        """
        self._json_db_manager.delete_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._USER_COLLECTION, user_id
        )

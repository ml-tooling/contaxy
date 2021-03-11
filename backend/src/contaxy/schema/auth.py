from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel, Field

from contaxy.schema.shared import MAX_DESCRIPTION_LENGTH


class AccessLevel(str, Enum):
    # Map to: select, insert, update, delete
    READ = "read"  # Viewer, view: Allows admin access , Can only view existing resources. Permissions for read-only actions that do not affect state, such as viewing (but not modifying) existing resources or data.
    WRITE = "write"  # Editor, edit, Contributor : Allows read/write access , Can create and manage all types of resources but can’t grant access to others.  All viewer permissions, plus permissions for actions that modify state, such as changing existing resources.
    ADMIN = "admin"  # Owner : Allows read-only access. Has full access to all resources including the right to edit IAM, invite users, edit roles. All editor permissions and permissions for the following actions:
    # none


class TokenPurpose(str, Enum):
    USER_GENERATED = "user-generated"
    REFRESH_TOKEN = "refresh-token"  # For user sessions
    DEPLOYMENT_TOKEN = "deployment-token"


class TokenType(str, Enum):
    SESSION_TOKEN = "session-token"
    API_TOKEN = "api-token"


class ApiToken(BaseModel):
    token: str = Field(
        ...,
        example="f4528e540a133dd53ba6809e74e16774ebe4777a",
        description="API Token.",
    )
    scopes: List[str] = Field(
        ...,
        example=["projects#read"],
        description="List of scopes associated with the token.",
    )
    description: Optional[str] = Field(
        None,
        example="Token used for accesing project resources on my local machine.",
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Short description about the context and usage of the token.",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Creation date of the token.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this token.",
    )
    expires_at: Optional[datetime] = Field(
        None,
        example="2021-04-25T10:20:30.400+02:30",
        description="Date at which the token expires and, thereby, gets revoked.",
    )
    token_purpose: Optional[TokenPurpose] = Field(
        None,
        example=TokenPurpose.REFRESH_TOKEN,
        description="The purpose of the token.",
    )


class GrantedPermission(BaseModel):
    authorized_user: str
    resource_name: Optional[str] = None
    access_level: Optional[AccessLevel] = None


# Oauth Specific Code
class OAuth2TokenGrantTypes(str, Enum):
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"


class OAuth2TokenRequestForm:
    """OAuth2 Token Endpoint Request Form."""

    def __init__(
        self,
        grant_type: OAuth2TokenGrantTypes = Form(
            ...,
            description="Grant type. Determines the mechanism used to authorize the creation of the tokens.",
        ),
        username: Optional[str] = Form(
            None, description="Required for `password` grant type. The user’s username."
        ),
        password: Optional[str] = Form(
            None, description="Required for `password` grant type. The user’s password."
        ),
        scope: Optional[str] = Form(
            None,
            description="Scopes that the client wants to be included in the access token. List of space-delimited, case-sensitive strings",
        ),
        client_id: Optional[str] = Form(
            None,
            description="The client identifier issued to the client during the registration process",
        ),
        client_secret: Optional[str] = Form(
            None,
            description=" The client secret. The client MAY omit the parameter if the client secret is an empty string.",
        ),
        code: Optional[str] = Form(
            None,
            description="Required for `authorization_code` grant type. The value is what was returned from the authorization endpoint.",
        ),
        redirect_uri: Optional[str] = Form(
            None,
            description="Required for `authorization_code` grant type. Specifies the callback location where the authorization was sent. This value must match the `redirect_uri` used to generate the original authorization_code.",
        ),
        refresh_token: Optional[str] = Form(
            None,
            description="Required for `refresh_token` grant type. The refresh token previously issued to the client.",
        ),
        state: Optional[str] = Form(
            None,
            description="An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery.",
        ),
        set_as_cookie: Optional[bool] = Form(
            False,
            description="If `true`, the access (and refresh) token will be set as cookie instead of the response body.",
        ),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = []
        if scope:
            self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.state = state
        self.set_as_cookie = set_as_cookie


class OAuthToken(BaseModel):
    token_type: str = Field(
        ..., description="The type of token this is, typically just the string `bearer`"
    )
    access_token: str = Field(..., description="The access token string.")
    expires_in: Optional[int] = Field(
        None,
        description="The expiration time of the access token in seconds.",
    )
    refresh_token: Optional[str] = Field(
        None, description="API token to refresh the sesion token (if it expires)."
    )
    scope: Optional[str] = Field(
        None, description="The scopes contained in the access token."
    )
    id_token: Optional[str] = Field(
        None,
        description="OpenID Connect ID Token that encodes the user’s authentication information.",
    )


class OpenIDUserInfo(BaseModel):
    # Based on: https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
    sub: str = Field(
        ..., description="Subject - Identifier for the End-User at the Issuer."
    )
    name: Optional[str] = Field(
        None,
        description="End-User's full name in displayable form including all name parts, possibly including titles and suffixes, ordered according to the End-User's locale and preferences.",
    )
    # TODO: this is actually
    preferred_username: Optional[str] = Field(
        None,
        description="Shorthand name by which the End-User wishes to be referred to.",
    )
    email: Optional[str] = Field(
        None,
        description="End-User's preferred e-mail address",
    )
    updated_at: Optional[int] = Field(
        None,
        description="Time the End-User's information was last updated. Number of seconds from 1970-01-01T0:0:0Z as measured in UTC until the date/time.",
    )


class OAuthTokenIntrospection(BaseModel):
    active: bool = Field(
        ...,
        description="Indicator of whether or not the presented token is currently active.",
    )
    scope: Optional[str] = Field(
        None,
        description="A space-delimited list of scopes.",
    )
    client_id: Optional[str] = Field(
        None,
        description="Client identifier for the OAuth 2.0 client that requested this token.",
    )
    username: Optional[str] = Field(
        None,
        description="Human-readable identifier for the resource owner who authorized this token.",
    )
    token_type: Optional[str] = Field(
        None,
        description="Type of the token as defined in Section 5.1 of OAuth 2.0 [RFC6749].",
    )
    exp: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token will expire, as defined in JWT [RFC7519].",
    )
    iat: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token was originally issued, as defined in JWT [RFC7519].",
    )
    nbf: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token is not to be used before, as defined in JWT [RFC7519].",
    )
    sub: Optional[str] = Field(
        None,
        description="Subject of the token, as defined in JWT [RFC7519]. Usually a machine-readable identifier of the resource owner who authorized this token.",
    )
    aud: Optional[str] = Field(
        None,
        description="Service-specific string identifier or list of string identifiers representing the intended audience for this token, as defined in JWT [RFC7519].",
    )
    iss: Optional[str] = Field(
        None,
        description="String representing the issuer of this token, as defined in JWT [RFC7519].",
    )
    jti: Optional[str] = Field(
        None,
        description="String identifier for the token, as defined in JWT [RFC7519].",
    )
    uid: Optional[str] = Field(
        None,
        description="The user ID. This parameter is returned only if the token is an access token and the subject is an end user.",
    )


class AuthorizeResponseType(str, Enum):
    TOKEN = "token"
    CODE = "code"


class OAuth2AuthorizeRequestForm:
    """OAuth2 Authorize Endpoint Request Form."""

    def __init__(
        self,
        response_type: AuthorizeResponseType = Form(
            ...,
            description="Either code for requesting an authorization code or token for requesting an access token (implicit grant).",
        ),
        client_id: Optional[str] = Form(
            None, description="The public identifier of the client."
        ),
        redirect_uri: Optional[str] = Form(None, description="Redirection URL."),
        scope: Optional[str] = Form(
            None, description="The scope of the access request."
        ),
        state: Optional[str] = Form(
            None,
            description="An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery",
        ),
        nonce: Optional[str] = Form(None),
    ):
        self.response_type = response_type
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self.nonce = nonce

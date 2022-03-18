/**
 * Contaxy API
 * Functionality to create and manage projects, services, jobs, and files.
 *
 * The version of the OpenAPI document: 0.0.13
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 *
 */

import ApiClient from '../ApiClient';
import ApiToken from '../model/ApiToken';
import AuthorizedAccess from '../model/AuthorizedAccess';
import OAuth2ErrorDetails from '../model/OAuth2ErrorDetails';
import OAuthToken from '../model/OAuthToken';
import OAuthTokenIntrospection from '../model/OAuthTokenIntrospection';
import ProblemDetails from '../model/ProblemDetails';
import TokenType from '../model/TokenType';

/**
 * Auth service.
 * @module api/AuthApi
 * @version 0.0.13
 */
export default class AuthApi {
  /**
   * Constructs a new AuthApi.
   * @alias module:api/AuthApi
   * @class
   * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
   * default to {@link module:ApiClient#instance} if unspecified.
   */
  constructor(apiClient) {
    this.apiClient = apiClient || ApiClient.instance;
  }

  /**
   * Create API or session token.
   * Returns a session or API token with the specified scopes.  If no scopes are specified, the token will be generated with the same scopes as the authorized token.  The API token can be deleted (revoked) at any time. In comparison, the session token cannot be revoked but expires after a short time (a few minutes).  This operation can only be called with API tokens (or refresh tokens) due to security aspects. Session tokens are not allowed to create other tokens. Furthermore, tokens can only be created if the API token used for authorization is granted at least the same access level on the given resource. For example, a token with `write` access level on a given resource allows to create new tokens with `write` or `read` granted level on that resource.
   * @param {Object} opts Optional parameters
   * @param {Array.<String>} opts.scope Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token.
   * @param {module:model/TokenType} opts.tokenType Type of the token. (default to 'session-token')
   * @param {String} opts.description Attach a short description to the generated token.
   * @param {String} opts.tokenPurpose Purpose of this token. (default to 'custom-token-purpose')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link String} and HTTP response
   */
  createTokenWithHttpInfo(opts) {
    opts = opts || {};
    let postBody = null;

    let pathParams = {};
    let queryParams = {
      scope: this.apiClient.buildCollectionParam(opts['scope'], 'multi'),
      token_type: opts['tokenType'],
      description: opts['description'],
      token_purpose: opts['tokenPurpose'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = 'String';
    return this.apiClient.callApi(
      '/auth/tokens',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Create API or session token.
   * Returns a session or API token with the specified scopes.  If no scopes are specified, the token will be generated with the same scopes as the authorized token.  The API token can be deleted (revoked) at any time. In comparison, the session token cannot be revoked but expires after a short time (a few minutes).  This operation can only be called with API tokens (or refresh tokens) due to security aspects. Session tokens are not allowed to create other tokens. Furthermore, tokens can only be created if the API token used for authorization is granted at least the same access level on the given resource. For example, a token with `write` access level on a given resource allows to create new tokens with `write` or `read` granted level on that resource.
   * @param {Object} opts Optional parameters
   * @param {Array.<String>} opts.scope Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token.
   * @param {module:model/TokenType} opts.tokenType Type of the token. (default to 'session-token')
   * @param {String} opts.description Attach a short description to the generated token.
   * @param {String} opts.tokenPurpose Purpose of this token. (default to 'custom-token-purpose')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link String}
   */
  createToken(opts) {
    return this.createTokenWithHttpInfo(opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Deletes permission of specified resource.
   * Deletes permission of specified resource, admin access to the /auth/permissions resource is required.
   * @param {String} resourceName
   * @param {String} permission
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.removeSubPermissions  (default to false)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  deleteResourcePermissionsWithHttpInfo(resourceName, permission, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'resourceName' is set
    if (resourceName === undefined || resourceName === null) {
      throw new Error(
        "Missing the required parameter 'resourceName' when calling deleteResourcePermissions"
      );
    }
    // verify the required parameter 'permission' is set
    if (permission === undefined || permission === null) {
      throw new Error(
        "Missing the required parameter 'permission' when calling deleteResourcePermissions"
      );
    }

    let pathParams = {};
    let queryParams = {
      resource_name: resourceName,
      permission: permission,
      remove_sub_permissions: opts['removeSubPermissions'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = null;
    return this.apiClient.callApi(
      '/auth/permissions',
      'DELETE',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Deletes permission of specified resource.
   * Deletes permission of specified resource, admin access to the /auth/permissions resource is required.
   * @param {String} resourceName
   * @param {String} permission
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.removeSubPermissions  (default to false)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  deleteResourcePermissions(resourceName, permission, opts) {
    return this.deleteResourcePermissionsWithHttpInfo(
      resourceName,
      permission,
      opts
    ).then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * List all resources that have a certain permission.
   * List all resources that have a certain permission, admin access to the /auth/resources resource is required.
   * @param {String} permission
   * @param {Object} opts Optional parameters
   * @param {String} opts.resourceNamePrefix
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<String>} and HTTP response
   */
  getResourcesWithPermissionWithHttpInfo(permission, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'permission' is set
    if (permission === undefined || permission === null) {
      throw new Error(
        "Missing the required parameter 'permission' when calling getResourcesWithPermission"
      );
    }

    let pathParams = {};
    let queryParams = {
      permission: permission,
      resource_name_prefix: opts['resourceNamePrefix'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = ['String'];
    return this.apiClient.callApi(
      '/auth/resources',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * List all resources that have a certain permission.
   * List all resources that have a certain permission, admin access to the /auth/resources resource is required.
   * @param {String} permission
   * @param {Object} opts Optional parameters
   * @param {String} opts.resourceNamePrefix
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<String>}
   */
  getResourcesWithPermission(permission, opts) {
    return this.getResourcesWithPermissionWithHttpInfo(permission, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * Introspect a token (OAuth2 Endpoint).
   * Introspects a given token.  Returns a boolean that indicates whether it is active or not. If the token is active, additional data about the token is also returned. If the token is invalid, expired, or revoked, it is considered inactive.  This endpoint implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)).
   * @param {String} token The token that should be instrospected.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenTypeHint A hint about the type of the token submitted for introspection (e.g. `access_token`, `id_token` and `refresh_token`).
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/OAuthTokenIntrospection} and HTTP response
   */
  introspectTokenWithHttpInfo(token, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'token' is set
    if (token === undefined || token === null) {
      throw new Error(
        "Missing the required parameter 'token' when calling introspectToken"
      );
    }

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {
      token: token,
      token_type_hint: opts['tokenTypeHint'],
    };

    let authNames = [];
    let contentTypes = ['application/x-www-form-urlencoded'];
    let accepts = ['application/json'];
    let returnType = OAuthTokenIntrospection;
    return this.apiClient.callApi(
      '/auth/oauth/introspect',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Introspect a token (OAuth2 Endpoint).
   * Introspects a given token.  Returns a boolean that indicates whether it is active or not. If the token is active, additional data about the token is also returned. If the token is invalid, expired, or revoked, it is considered inactive.  This endpoint implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)).
   * @param {String} token The token that should be instrospected.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenTypeHint A hint about the type of the token submitted for introspection (e.g. `access_token`, `id_token` and `refresh_token`).
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/OAuthTokenIntrospection}
   */
  introspectToken(token, opts) {
    return this.introspectTokenWithHttpInfo(token, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * List API tokens.
   * Returns list of created API tokens associated with the authenticated user.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenSubject Subject for which the tokens should be listed.If it is not provided, the tokens of the authorized user are returned.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/ApiToken>} and HTTP response
   */
  listApiTokensWithHttpInfo(opts) {
    opts = opts || {};
    let postBody = null;

    let pathParams = {};
    let queryParams = {
      token_subject: opts['tokenSubject'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = [ApiToken];
    return this.apiClient.callApi(
      '/auth/tokens',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * List API tokens.
   * Returns list of created API tokens associated with the authenticated user.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenSubject Subject for which the tokens should be listed.If it is not provided, the tokens of the authorized user are returned.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/ApiToken>}
   */
  listApiTokens(opts) {
    return this.listApiTokensWithHttpInfo(opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Lists permissions for given resource.
   * Lists the permissions for a given resource, admin access for that resource is required.
   * @param {String} resourceName
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.resolveRoles  (default to true)
   * @param {Boolean} opts.useCache  (default to true)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<String>} and HTTP response
   */
  listResourcePermissionsWithHttpInfo(resourceName, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'resourceName' is set
    if (resourceName === undefined || resourceName === null) {
      throw new Error(
        "Missing the required parameter 'resourceName' when calling listResourcePermissions"
      );
    }

    let pathParams = {};
    let queryParams = {
      resource_name: resourceName,
      resolve_roles: opts['resolveRoles'],
      use_cache: opts['useCache'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = ['String'];
    return this.apiClient.callApi(
      '/auth/permissions',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Lists permissions for given resource.
   * Lists the permissions for a given resource, admin access for that resource is required.
   * @param {String} resourceName
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.resolveRoles  (default to true)
   * @param {Boolean} opts.useCache  (default to true)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<String>}
   */
  listResourcePermissions(resourceName, opts) {
    return this.listResourcePermissionsWithHttpInfo(resourceName, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * Open the login page (OAuth2 Client Endpoint).
   * Callback to finish the login process (OAuth2 Client Endpoint).  The authorization `code` is exchanged for an access and ID token. The ID token contains all relevant user information and is used to login the user. If the user does not exist, a new user will be created with the information from the ID token.  Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies.  This endpoint implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.
   * @param {String} code The authorization code generated by the authorization server.
   * @param {Object} opts Optional parameters
   * @param {String} opts.state
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Object} and HTTP response
   */
  loginCallbackWithHttpInfo(code, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'code' is set
    if (code === undefined || code === null) {
      throw new Error(
        "Missing the required parameter 'code' when calling loginCallback"
      );
    }

    let pathParams = {};
    let queryParams = {
      code: code,
      state: opts['state'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = Object;
    return this.apiClient.callApi(
      '/auth/oauth/callback',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Open the login page (OAuth2 Client Endpoint).
   * Callback to finish the login process (OAuth2 Client Endpoint).  The authorization `code` is exchanged for an access and ID token. The ID token contains all relevant user information and is used to login the user. If the user does not exist, a new user will be created with the information from the ID token.  Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies.  This endpoint implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.
   * @param {String} code The authorization code generated by the authorization server.
   * @param {Object} opts Optional parameters
   * @param {String} opts.state
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Object}
   */
  loginCallback(code, opts) {
    return this.loginCallbackWithHttpInfo(code, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Login a user session.
   * Signs in the user based on username and password credentials.  This will set http-only cookies containg tokens with full user access.
   * @param {String} username The user’s username or email used for login.
   * @param {String} password The user’s password.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  loginUserSessionWithHttpInfo(username, password) {
    let postBody = null;
    // verify the required parameter 'username' is set
    if (username === undefined || username === null) {
      throw new Error(
        "Missing the required parameter 'username' when calling loginUserSession"
      );
    }
    // verify the required parameter 'password' is set
    if (password === undefined || password === null) {
      throw new Error(
        "Missing the required parameter 'password' when calling loginUserSession"
      );
    }

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {
      username: username,
      password: password,
    };

    let authNames = [];
    let contentTypes = ['application/x-www-form-urlencoded'];
    let accepts = ['application/json'];
    let returnType = null;
    return this.apiClient.callApi(
      '/auth/login',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Login a user session.
   * Signs in the user based on username and password credentials.  This will set http-only cookies containg tokens with full user access.
   * @param {String} username The user’s username or email used for login.
   * @param {String} password The user’s password.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  loginUserSession(username, password) {
    return this.loginUserSessionWithHttpInfo(username, password).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Logout a user session.
   * Removes all session token cookies and redirects to the login page.  When making requests to the this endpoint, the browser should be redirected to this endpoint.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  logoutUserSessionWithHttpInfo() {
    let postBody = null;

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = null;
    return this.apiClient.callApi(
      '/auth/logout',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Logout a user session.
   * Removes all session token cookies and redirects to the login page.  When making requests to the this endpoint, the browser should be redirected to this endpoint.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  logoutUserSession() {
    return this.logoutUserSessionWithHttpInfo().then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Check if external OAuth2 (OIDC) IDP is enabled.
   * Returns the value of `OIDC_AUTH_ENABLED`.  Returns \"0\" if it is not set, \"1\" if it is set.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link String} and HTTP response
   */
  oauthEnabledWithHttpInfo() {
    let postBody = null;

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {};

    let authNames = [];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = 'String';
    return this.apiClient.callApi(
      '/auth/oauth/enabled',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Check if external OAuth2 (OIDC) IDP is enabled.
   * Returns the value of `OIDC_AUTH_ENABLED`.  Returns \"0\" if it is not set, \"1\" if it is set.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link String}
   */
  oauthEnabled() {
    return this.oauthEnabledWithHttpInfo().then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Open the login page.
   * Returns or redirect to the login-page.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  openLoginPageWithHttpInfo() {
    let postBody = null;

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {};

    let authNames = [];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = null;
    return this.apiClient.callApi(
      '/auth/login-page',
      'GET',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Open the login page.
   * Returns or redirect to the login-page.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  openLoginPage() {
    return this.openLoginPageWithHttpInfo().then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Request a token (OAuth2 Endpoint).
   * Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters.   The token endpoint is used by the client to obtain an access token by  presenting its authorization grant or refresh token.   The token endpoint supports the following grant types:  - [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token.      - `grant_type` must be set to `password`      - `username` (required): The user’s username.      - `password` (required): The user’s password.      - `scope` (optional): Optional requested scope values for the access token.  - [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens.      - `grant_type` must be set to `refresh_token`      - `refresh_token` (required): The refresh token previously issued to the client.      - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope.  - [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client credentials.      - `grant_type` must be set to `client_credentials`      - `scope` (optional): Optional requested scope values for the access token.      - Client Authentication required (e.g. via client_id and client_secret or auth header)  - [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint.      - `grant_type` must be set to `authorization_code`      - `code` (required): The authorization code that the client previously received from the authorization server.      - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request.      - Client Authentication required (e.g. via client_id and client_secret or auth header)  For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow. For the authorization code flow, calling this endpoint is the second step of the flow.  This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2).
   * @param {Object} grantType
   * @param {Object} opts Optional parameters
   * @param {Object} opts.username
   * @param {Object} opts.password
   * @param {Object} opts.scope
   * @param {Object} opts.clientId
   * @param {Object} opts.clientSecret
   * @param {Object} opts.code
   * @param {Object} opts.redirectUri
   * @param {Object} opts.refreshToken
   * @param {Object} opts.state
   * @param {Object} opts.setAsCookie
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/OAuthToken} and HTTP response
   */
  requestTokenWithHttpInfo(grantType, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'grantType' is set
    if (grantType === undefined || grantType === null) {
      throw new Error(
        "Missing the required parameter 'grantType' when calling requestToken"
      );
    }

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {
      grant_type: grantType,
      username: opts['username'],
      password: opts['password'],
      scope: opts['scope'],
      client_id: opts['clientId'],
      client_secret: opts['clientSecret'],
      code: opts['code'],
      redirect_uri: opts['redirectUri'],
      refresh_token: opts['refreshToken'],
      state: opts['state'],
      set_as_cookie: opts['setAsCookie'],
    };

    let authNames = [];
    let contentTypes = ['application/x-www-form-urlencoded'];
    let accepts = ['application/json'];
    let returnType = OAuthToken;
    return this.apiClient.callApi(
      '/auth/oauth/token',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Request a token (OAuth2 Endpoint).
   * Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters.   The token endpoint is used by the client to obtain an access token by  presenting its authorization grant or refresh token.   The token endpoint supports the following grant types:  - [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token.      - `grant_type` must be set to `password`      - `username` (required): The user’s username.      - `password` (required): The user’s password.      - `scope` (optional): Optional requested scope values for the access token.  - [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens.      - `grant_type` must be set to `refresh_token`      - `refresh_token` (required): The refresh token previously issued to the client.      - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope.  - [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client credentials.      - `grant_type` must be set to `client_credentials`      - `scope` (optional): Optional requested scope values for the access token.      - Client Authentication required (e.g. via client_id and client_secret or auth header)  - [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint.      - `grant_type` must be set to `authorization_code`      - `code` (required): The authorization code that the client previously received from the authorization server.      - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request.      - Client Authentication required (e.g. via client_id and client_secret or auth header)  For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow. For the authorization code flow, calling this endpoint is the second step of the flow.  This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2).
   * @param {Object} grantType
   * @param {Object} opts Optional parameters
   * @param {Object} opts.username
   * @param {Object} opts.password
   * @param {Object} opts.scope
   * @param {Object} opts.clientId
   * @param {Object} opts.clientSecret
   * @param {Object} opts.code
   * @param {Object} opts.redirectUri
   * @param {Object} opts.refreshToken
   * @param {Object} opts.state
   * @param {Object} opts.setAsCookie
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/OAuthToken}
   */
  requestToken(grantType, opts) {
    return this.requestTokenWithHttpInfo(grantType, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Revoke a token (OAuth2 Endpoint).
   * Revokes a given token.  This will delete the API token, preventing further requests with the given token. Because of caching, the API token might still be usable under certain conditions for some operations for a maximum of 15 minutes after deletion.  This endpoint implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)).
   * @param {String} token The token that should be revoked.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenTypeHint A hint about the type of the token submitted for revokation.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Object} and HTTP response
   */
  revokeTokenWithHttpInfo(token, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'token' is set
    if (token === undefined || token === null) {
      throw new Error(
        "Missing the required parameter 'token' when calling revokeToken"
      );
    }

    let pathParams = {};
    let queryParams = {};
    let headerParams = {};
    let formParams = {
      token: token,
      token_type_hint: opts['tokenTypeHint'],
    };

    let authNames = [];
    let contentTypes = ['application/x-www-form-urlencoded'];
    let accepts = ['application/json'];
    let returnType = Object;
    return this.apiClient.callApi(
      '/auth/oauth/revoke',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Revoke a token (OAuth2 Endpoint).
   * Revokes a given token.  This will delete the API token, preventing further requests with the given token. Because of caching, the API token might still be usable under certain conditions for some operations for a maximum of 15 minutes after deletion.  This endpoint implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)).
   * @param {String} token The token that should be revoked.
   * @param {Object} opts Optional parameters
   * @param {String} opts.tokenTypeHint A hint about the type of the token submitted for revokation.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Object}
   */
  revokeToken(token, opts) {
    return this.revokeTokenWithHttpInfo(token, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Add permission to specified resource.
   * Adds permission to specified resource, admin access to the /auth/permissions resource is required.
   * @param {String} resourceName
   * @param {String} permission
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  setResourcePermissionsWithHttpInfo(resourceName, permission) {
    let postBody = null;
    // verify the required parameter 'resourceName' is set
    if (resourceName === undefined || resourceName === null) {
      throw new Error(
        "Missing the required parameter 'resourceName' when calling setResourcePermissions"
      );
    }
    // verify the required parameter 'permission' is set
    if (permission === undefined || permission === null) {
      throw new Error(
        "Missing the required parameter 'permission' when calling setResourcePermissions"
      );
    }

    let pathParams = {};
    let queryParams = {
      resource_name: resourceName,
      permission: permission,
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = [];
    let accepts = ['application/json'];
    let returnType = null;
    return this.apiClient.callApi(
      '/auth/permissions',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Add permission to specified resource.
   * Adds permission to specified resource, admin access to the /auth/permissions resource is required.
   * @param {String} resourceName
   * @param {String} permission
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  setResourcePermissions(resourceName, permission) {
    return this.setResourcePermissionsWithHttpInfo(
      resourceName,
      permission
    ).then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Verify a Session or API Token.
   * Verifies a session or API token for its validity and - if provided - if it has the specified permission.  Returns an successful HTTP Status code if verification was successful, otherwise an error is returned.
   * @param {Object} opts Optional parameters
   * @param {String} opts.permission The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked.
   * @param {Boolean} opts.useCache If false, no cache will be used for verifying the token. (default to true)
   * @param {String} opts.body
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/AuthorizedAccess} and HTTP response
   */
  verifyAccessWithHttpInfo(opts) {
    opts = opts || {};
    let postBody = opts['body'];

    let pathParams = {};
    let queryParams = {
      permission: opts['permission'],
      use_cache: opts['useCache'],
    };
    let headerParams = {};
    let formParams = {};

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = ['application/json'];
    let accepts = ['application/json'];
    let returnType = AuthorizedAccess;
    return this.apiClient.callApi(
      '/auth/tokens/verify',
      'POST',
      pathParams,
      queryParams,
      headerParams,
      formParams,
      postBody,
      authNames,
      contentTypes,
      accepts,
      returnType,
      null
    );
  }

  /**
   * Verify a Session or API Token.
   * Verifies a session or API token for its validity and - if provided - if it has the specified permission.  Returns an successful HTTP Status code if verification was successful, otherwise an error is returned.
   * @param {Object} opts Optional parameters
   * @param {String} opts.permission The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked.
   * @param {Boolean} opts.useCache If false, no cache will be used for verifying the token. (default to true)
   * @param {String} opts.body
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/AuthorizedAccess}
   */
  verifyAccess(opts) {
    return this.verifyAccessWithHttpInfo(opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }
}

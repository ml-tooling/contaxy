from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from fastapi import Body, Cookie, Depends, FastAPI, Form, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse, RedirectResponse, Response

from contaxy import __version__, data_model
from contaxy.utils.fastapi_utils import patch_fastapi

app = FastAPI()

# Initialize API
app = FastAPI(
    title="Contaxy API",
    description="Functionality to create and manage projects, services, jobs, and files.",
    version=__version__,
)

# TEMP: for debugging purpose
@app.get("/welcome", include_in_schema=False)
def welcome() -> Any:
    return {"Hello": "World"}


# Redirect to docs
@app.get("/", include_in_schema=False)
def root() -> Any:
    return RedirectResponse("./docs")


# TEMP: Graphql test

import graphene
from starlette.graphql import GraphQLApp

graphql_voyager = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        height: 100%;
        margin: 0;
        width: 100%;
        overflow: hidden;
      }
      #voyager {
        height: 100vh;
      }
    </style>

    <!--
      This GraphQL Voyager example depends on Promise and fetch, which are available in
      modern browsers, but can be "polyfilled" for older browsers.
      GraphQL Voyager itself depends on React DOM.
      If you do not want to rely on a CDN, you can host these files locally or
      include them directly in your favored resource bunder.
    -->
    <script src="https://cdn.jsdelivr.net/es6-promise/4.0.5/es6-promise.auto.min.js"></script>
    <script src="https://cdn.jsdelivr.net/fetch/0.9.0/fetch.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react@16/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@16/umd/react-dom.production.min.js"></script>

    <!--
      These two files are served from jsDelivr CDN, however you may wish to
      copy them directly into your environment, or perhaps include them in your
      favored resource bundler.
     -->
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.css"
    />
    <script src="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.min.js"></script>
  </head>
  <body>
    <div id="voyager">Loading...</div>
    <script>
      // Defines a GraphQL introspection fetcher using the fetch API. You're not required to
      // use fetch, and could instead implement introspectionProvider however you like,
      // as long as it returns a Promise
      // Voyager passes introspectionQuery as an argument for this function
      function introspectionProvider(introspectionQuery) {
        // This example expects a GraphQL server at the path /graphql.
        // Change this to point wherever you host your GraphQL server.
        return fetch('./test-graphql', {
          method: 'post',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: introspectionQuery }),
          credentials: 'include',
        })
          .then(function (response) {
            return response.text();
          })
          .then(function (responseBody) {
            try {
              return JSON.parse(responseBody);
            } catch (error) {
              return responseBody;
            }
          });
      }

      // Render <Voyager /> into the body.
      GraphQLVoyager.init(document.getElementById('voyager'), {
        introspection: introspectionProvider,
      });
    </script>
  </body>
</html>
"""


class GraphQlQuery(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name) -> str:  # type: ignore
        return "Hello " + name


app.add_route("/test-graphql", GraphQLApp(schema=graphene.Schema(query=GraphQlQuery)))


@app.get(
    "/graphql-voyager",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    include_in_schema=False,
)
def open_graphql_voyager() -> Any:
    return HTMLResponse(
        content=graphql_voyager,
        status_code=status.HTTP_200_OK,
    )


@app.get(
    "/search",
    operation_id="search_resources",
    response_model=data_model.Resource,
    summary="Search resources.",
    # tags=,
    status_code=status.HTTP_200_OK,
)
def search_resources(
    q: str = Query(..., description="Search query."),
    type: Optional[str] = Query(
        None, description="Resource type to use for filtering search results."
    ),
) -> Any:
    raise NotImplementedError


# System Endpoints


# Auth Endpoints
@app.post(
    "/auth/oauth/authorize",
    operation_id=data_model.CoreOperations.AUTHORIZE_CLIENT.value,
    summary="Authorize a client (OAuth2 Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_302_FOUND,
)
def authorize_client(form_data: OAuth2AuthorizeRequestForm = Depends()) -> Any:
    """Authorizes a client.

    The authorization endpoint is used by the client to obtain authorization from the resource owner via user-agent redirection.

    The authorization server redirects the user-agent to the client's redirection endpoint previously established with the
    authorization server during the client registration process or when making the authorization request.

    This endpoint implements the [OAuth2 Authorization Endpoint](https://tools.ietf.org/html/rfc6749#section-3.1).
    """
    pass


# Project Endpoints


# Service Endpoints


# Extension Endpoints


@router.put(
    "/projects/{project_id}/extensions:defaults",
    operation_id=CoreOperations.SET_EXTENSION_DEFAULTS.value,
    summary="Set extension defaults.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def set_extension_defaults(
    extension_id: str = Query(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
    operation_id: List[ExtensibleOperations] = Query(
        ...,
        title="Operation IDs",
        description="Set extension as default for those operation IDs.",
    ),
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Configures the extension to be used as default for a set of operation IDs.

    This operation can only be executed by project administrators (for setting project defaults) or system administrators.
    """
    raise NotImplementedError


@router.get(
    "/projects/{project_id}/extensions:defaults",
    operation_id=CoreOperations.GET_EXTENSION_DEFAULTS.value,
    summary="Get extensions defaults.",
    response_model=List[Dict[TechnicalProject, str]],
    status_code=status.HTTP_200_OK,
)
def get_extension_defaults(
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Returns the list of extensible operation IDs with the configured default extension.

    This operation can only be called by project administrators (to get project defaults) or system administrators.
    """
    raise NotImplementedError


# File Endpoints


# Secrets Endpoints


@app.get(
    "/projects/{project_id}/secrets",
    operation_id=data_model.CoreOperations.LIST_SECRETS.value,
    response_model=List[data_model.Secret],
    summary="List project secrets.",
    tags=["secrets"],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_secrets(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Lists all the secrets associated with the project."""
    raise NotImplementedError


@app.put(
    "/projects/{project_id}/secrets/{secret_name}",
    operation_id=data_model.CoreOperations.CREATE_SECRET.value,
    summary="Create or updated a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
def create_secret(
    secret: data_model.SecretInput,
    secret_name: str = Path(
        ..., description="Name of the secret."
    ),  # TODO add regex pattern
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Creates or updates (overwrites) a secret.

    The secret value will be stored in an encrypted format
    and hidden or removed in certain parts of the application (such as job or service logs).

    However, all project members with atleast `read` permission on the project will be able to access and read the secret value.
    Therefore, we cannot prevent any misuse with the secret caused by mishandling from a project member.
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/secrets/{secret_name}",
    operation_id=data_model.CoreOperations.DELETE_SECRET.value,
    summary="Delete a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
def delete_secret(
    secret_name: str = Path(
        ..., description="Name of the secret."
    ),  # TODO add regex pattern
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Deletes a secret."""
    raise NotImplementedError


# Configuration Endpoints


@app.put(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.CREATE_CONFIGURATION.value,
    summary="Create a configuration.",
    tags=["configurations"],
    response_model=data_model.Configuration,
    status_code=status.HTTP_200_OK,
)
def create_configuration(
    configuration: data_model.ConfigurationInput,
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Creates a configuration.

    If a configuration already exists for the given id, the configuration will be overwritten.
    """
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.UPDATE_CONFIGURATION.value,
    summary="Update a configuration.",
    tags=["configurations"],
    response_model=data_model.Configuration,
    status_code=status.HTTP_200_OK,
)
def update_configuration(
    configuration: data_model.ConfigurationInput,
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Updates a configuration.

    The update is applied on the existing configuration based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.LIST_CONFIGURATIONS.value,
    response_model=List[data_model.Configuration],
    summary="List configuration.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def list_configurations(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Lists all configuration associated with the project.

    If extensions are registered for this operation and no extension is selected via the `extension_id`
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.GET_CONFIGURATION.value,
    response_model=data_model.Configuration,
    summary="Get a configuration.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def get_configuration(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Returns a single configuration."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}/{parameter_key}",
    operation_id=data_model.CoreOperations.GET_CONFIGURATION_PARAMETER.value,
    response_model=str,
    summary="Get a configuration parameter.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def get_configuration_parameter(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
    paramter_key: str = Path(..., description="Key of the paramter."),
) -> Any:
    """Returns a the value of a single parameter from a configuration."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.DELETE_CONFIGURATION.value,
    summary="Delete a configuration.",
    tags=["configurations"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_configuration(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Deletes a single configuration."""
    raise NotImplementedError


#############


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    # TODO: Run with: Run with: PYTHONASYNCIODEBUG=1
    uvicorn.run(
        "contaxy.base_api:app", host="0.0.0.0", port=8082, log_level="info", reload=True
    )

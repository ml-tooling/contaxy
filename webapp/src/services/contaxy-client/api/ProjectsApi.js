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
import AccessLevel from '../model/AccessLevel';
import ProblemDetails from '../model/ProblemDetails';
import Project from '../model/Project';
import ProjectCreation from '../model/ProjectCreation';
import ProjectInput from '../model/ProjectInput';
import User from '../model/User';

/**
 * Projects service.
 * @module api/ProjectsApi
 * @version 0.0.13
 */
export default class ProjectsApi {
  /**
   * Constructs a new ProjectsApi.
   * @alias module:api/ProjectsApi
   * @class
   * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
   * default to {@link module:ApiClient#instance} if unspecified.
   */
  constructor(apiClient) {
    this.apiClient = apiClient || ApiClient.instance;
  }

  /**
   * Add user to project.
   * Adds a user to the project.  This will add the permission for this project to the user item. The `access_level` defines what the user can do:  - The `read` permission level allows read-only access on all resources. - The `write` permission level allows to create and delete project resources. - The `admin` permission level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {String} userId A valid user ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel The permission level. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/User>} and HTTP response
   */
  addProjectMemberWithHttpInfo(projectId, userId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling addProjectMember"
      );
    }
    // verify the required parameter 'userId' is set
    if (userId === undefined || userId === null) {
      throw new Error(
        "Missing the required parameter 'userId' when calling addProjectMember"
      );
    }

    let pathParams = {
      project_id: projectId,
      user_id: userId,
    };
    let queryParams = {
      access_level: opts['accessLevel'],
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
    let returnType = [User];
    return this.apiClient.callApi(
      '/projects/{project_id}/users/{user_id}',
      'PUT',
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
   * Add user to project.
   * Adds a user to the project.  This will add the permission for this project to the user item. The `access_level` defines what the user can do:  - The `read` permission level allows read-only access on all resources. - The `write` permission level allows to create and delete project resources. - The `admin` permission level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {String} userId A valid user ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel The permission level. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/User>}
   */
  addProjectMember(projectId, userId, opts) {
    return this.addProjectMemberWithHttpInfo(projectId, userId, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * Create a new project.
   * Creates a new project.  We suggest to use the `suggest_project_id` endpoint to get a valid and available ID. The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used.
   * @param {module:model/ProjectCreation} projectCreation
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/Project} and HTTP response
   */
  createProjectWithHttpInfo(projectCreation) {
    let postBody = projectCreation;
    // verify the required parameter 'projectCreation' is set
    if (projectCreation === undefined || projectCreation === null) {
      throw new Error(
        "Missing the required parameter 'projectCreation' when calling createProject"
      );
    }

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
    let contentTypes = ['application/json'];
    let accepts = ['application/json'];
    let returnType = Project;
    return this.apiClient.callApi(
      '/projects',
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
   * Create a new project.
   * Creates a new project.  We suggest to use the `suggest_project_id` endpoint to get a valid and available ID. The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used.
   * @param {module:model/ProjectCreation} projectCreation
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/Project}
   */
  createProject(projectCreation) {
    return this.createProjectWithHttpInfo(projectCreation).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Delete a project.
   * Deletes a project and all its associated resources including deployments and files.  A project can only be delete by a user with `admin` permission on the project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  deleteProjectWithHttpInfo(projectId) {
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling deleteProject"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
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
      '/projects/{project_id}',
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
   * Delete a project.
   * Deletes a project and all its associated resources including deployments and files.  A project can only be delete by a user with `admin` permission on the project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  deleteProject(projectId) {
    return this.deleteProjectWithHttpInfo(projectId).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Get details for a project.
   * Returns the metadata of a single project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/Project} and HTTP response
   */
  getProjectWithHttpInfo(projectId) {
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling getProject"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
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
    let returnType = Project;
    return this.apiClient.callApi(
      '/projects/{project_id}',
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
   * Get details for a project.
   * Returns the metadata of a single project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/Project}
   */
  getProject(projectId) {
    return this.getProjectWithHttpInfo(projectId).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Get project token.
   * Returns an API token with permission (`read`, `write`, or `admin`) to access all project resources.  The `read` access level allows read-only access on all resources. The `write` access level allows to create and delete project resources. The `admin` access level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel Access level of the token. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link String} and HTTP response
   */
  getProjectTokenWithHttpInfo(projectId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling getProjectToken"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
    let queryParams = {
      access_level: opts['accessLevel'],
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
      '/projects/{project_id}/token',
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
   * Get project token.
   * Returns an API token with permission (`read`, `write`, or `admin`) to access all project resources.  The `read` access level allows read-only access on all resources. The `write` access level allows to create and delete project resources. The `admin` access level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel Access level of the token. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link String}
   */
  getProjectToken(projectId, opts) {
    return this.getProjectTokenWithHttpInfo(projectId, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Get project token.
   * Returns an API token with permission (`read`, `write`, or `admin`) to access all project resources.  The `read` access level allows read-only access on all resources. The `write` access level allows to create and delete project resources. The `admin` access level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel Access level of the token. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link String} and HTTP response
   */
  getProjectToken_0WithHttpInfo(projectId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling getProjectToken_0"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
    let queryParams = {
      access_level: opts['accessLevel'],
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
      '/projects/{project_id}/token',
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
   * Get project token.
   * Returns an API token with permission (`read`, `write`, or `admin`) to access all project resources.  The `read` access level allows read-only access on all resources. The `write` access level allows to create and delete project resources. The `admin` access level allows to delete the project or add/remove other users.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {module:model/AccessLevel} opts.accessLevel Access level of the token. (default to 'write')
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link String}
   */
  getProjectToken_0(projectId, opts) {
    return this.getProjectToken_0WithHttpInfo(projectId, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * List project members.
   * Lists all project members.  This include all users that have atlease a `read` permission on the given project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/User>} and HTTP response
   */
  listProjectMembersWithHttpInfo(projectId) {
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling listProjectMembers"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
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
    let returnType = [User];
    return this.apiClient.callApi(
      '/projects/{project_id}/users',
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
   * List project members.
   * Lists all project members.  This include all users that have atlease a `read` permission on the given project.
   * @param {String} projectId A valid project ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/User>}
   */
  listProjectMembers(projectId) {
    return this.listProjectMembersWithHttpInfo(projectId).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * List all projects.
   * Lists all projects visible to the authenticated user.  A project is visible to a user, if the user has the atleast a `read` permission for the project. System adminstrators will also see technical projects, such as `system-internal` and `system-global`.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/Project>} and HTTP response
   */
  listProjectsWithHttpInfo() {
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
    let returnType = [Project];
    return this.apiClient.callApi(
      '/projects',
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
   * List all projects.
   * Lists all projects visible to the authenticated user.  A project is visible to a user, if the user has the atleast a `read` permission for the project. System adminstrators will also see technical projects, such as `system-internal` and `system-global`.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/Project>}
   */
  listProjects() {
    return this.listProjectsWithHttpInfo().then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Remove user from project.
   * Removes a user from a project.  This will remove the permission for this project from the user item.
   * @param {String} projectId A valid project ID.
   * @param {String} userId A valid user ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/User>} and HTTP response
   */
  removeProjectMemberWithHttpInfo(projectId, userId) {
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling removeProjectMember"
      );
    }
    // verify the required parameter 'userId' is set
    if (userId === undefined || userId === null) {
      throw new Error(
        "Missing the required parameter 'userId' when calling removeProjectMember"
      );
    }

    let pathParams = {
      project_id: projectId,
      user_id: userId,
    };
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
    let returnType = [User];
    return this.apiClient.callApi(
      '/projects/{project_id}/users/{user_id}',
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
   * Remove user from project.
   * Removes a user from a project.  This will remove the permission for this project from the user item.
   * @param {String} projectId A valid project ID.
   * @param {String} userId A valid user ID.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/User>}
   */
  removeProjectMember(projectId, userId) {
    return this.removeProjectMemberWithHttpInfo(projectId, userId).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * Suggest project ID.
   * Suggests a valid and unique project ID for the given display name.  The project ID will be human-readable and resemble the provided display name, but might be cut off or have an attached counter prefix.
   * @param {String} displayName
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link String} and HTTP response
   */
  suggestProjectIdWithHttpInfo(displayName) {
    let postBody = null;
    // verify the required parameter 'displayName' is set
    if (displayName === undefined || displayName === null) {
      throw new Error(
        "Missing the required parameter 'displayName' when calling suggestProjectId"
      );
    }

    let pathParams = {};
    let queryParams = {
      display_name: displayName,
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
      '/projects:suggest-id',
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
   * Suggest project ID.
   * Suggests a valid and unique project ID for the given display name.  The project ID will be human-readable and resemble the provided display name, but might be cut off or have an attached counter prefix.
   * @param {String} displayName
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link String}
   */
  suggestProjectId(displayName) {
    return this.suggestProjectIdWithHttpInfo(displayName).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Update project metadata.
   * Updates the metadata of the given project.  This will update only the properties that are explicitly set in the patch request. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
   * @param {String} projectId A valid project ID.
   * @param {module:model/ProjectInput} projectInput
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link module:model/Project} and HTTP response
   */
  updateProjectWithHttpInfo(projectId, projectInput) {
    let postBody = projectInput;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling updateProject"
      );
    }
    // verify the required parameter 'projectInput' is set
    if (projectInput === undefined || projectInput === null) {
      throw new Error(
        "Missing the required parameter 'projectInput' when calling updateProject"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
    let queryParams = {};
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
    let returnType = Project;
    return this.apiClient.callApi(
      '/projects/{project_id}',
      'PATCH',
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
   * Update project metadata.
   * Updates the metadata of the given project.  This will update only the properties that are explicitly set in the patch request. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
   * @param {String} projectId A valid project ID.
   * @param {module:model/ProjectInput} projectInput
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link module:model/Project}
   */
  updateProject(projectId, projectInput) {
    return this.updateProjectWithHttpInfo(projectId, projectInput).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }
}

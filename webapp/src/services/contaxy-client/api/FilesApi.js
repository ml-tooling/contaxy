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
import FileInput from '../model/FileInput';
import ProblemDetails from '../model/ProblemDetails';
import ResourceAction from '../model/ResourceAction';

/**
 * Files service.
 * @module api/FilesApi
 * @version 0.0.13
 */
export default class FilesApi {
  /**
   * Constructs a new FilesApi.
   * @alias module:api/FilesApi
   * @class
   * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
   * default to {@link module:ApiClient#instance} if unspecified.
   */
  constructor(apiClient) {
    this.apiClient = apiClient || ApiClient.instance;
  }

  /**
   * Delete a file.
   * Deletes the specified file.  If the file storage supports versioning and no `version` is specified, all versions of the file will be deleted.  The parameter `keep_latest_version` is useful if you want to delete all older versions of a file.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, all versions of the file will be deleted.
   * @param {Boolean} opts.keepLatestVersion Keep the latest version of the file. (default to false)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  deleteFileWithHttpInfo(projectId, fileKey, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling deleteFile"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling deleteFile"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {
      version: opts['version'],
      keep_latest_version: opts['keepLatestVersion'],
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
      '/projects/{project_id}/files/{file_key}',
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
   * Delete a file.
   * Deletes the specified file.  If the file storage supports versioning and no `version` is specified, all versions of the file will be deleted.  The parameter `keep_latest_version` is useful if you want to delete all older versions of a file.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, all versions of the file will be deleted.
   * @param {Boolean} opts.keepLatestVersion Keep the latest version of the file. (default to false)
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  deleteFile(projectId, fileKey, opts) {
    return this.deleteFileWithHttpInfo(projectId, fileKey, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Delete all files.
   * Deletes all files associated with a project.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing HTTP response
   */
  deleteFilesWithHttpInfo(projectId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling deleteFiles"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
    let queryParams = {
      extension_id: opts['extensionId'],
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
      '/projects/{project_id}/files',
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
   * Delete all files.
   * Deletes all files associated with a project.
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}
   */
  deleteFiles(projectId, opts) {
    return this.deleteFilesWithHttpInfo(projectId, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Download a file.
   * Downloads the selected file.  If the file storage supports versioning and no `version` is specified, the latest version will be downloaded.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Object} and HTTP response
   */
  downloadFileWithHttpInfo(projectId, fileKey, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling downloadFile"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling downloadFile"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {
      version: opts['version'],
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
    let returnType = Object;
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}:download',
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
   * Download a file.
   * Downloads the selected file.  If the file storage supports versioning and no `version` is specified, the latest version will be downloaded.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Object}
   */
  downloadFile(projectId, fileKey, opts) {
    return this.downloadFileWithHttpInfo(projectId, fileKey, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * Execute a file action.
   * Executes the selected action.  The actions need to be first requested from the [list_file_actions](#files/list_file_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.  The action mechanism is further explained in the description of the [list_file_actions](#files/list_file_actions).
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {String} actionId The action ID from the file actions operation.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Object} and HTTP response
   */
  executeFileActionWithHttpInfo(projectId, fileKey, actionId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling executeFileAction"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling executeFileAction"
      );
    }
    // verify the required parameter 'actionId' is set
    if (actionId === undefined || actionId === null) {
      throw new Error(
        "Missing the required parameter 'actionId' when calling executeFileAction"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
      action_id: actionId,
    };
    let queryParams = {
      version: opts['version'],
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
    let returnType = Object;
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}/actions/{action_id}',
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
   * Execute a file action.
   * Executes the selected action.  The actions need to be first requested from the [list_file_actions](#files/list_file_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.  The action mechanism is further explained in the description of the [list_file_actions](#files/list_file_actions).
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {String} actionId The action ID from the file actions operation.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Object}
   */
  executeFileAction(projectId, fileKey, actionId, opts) {
    return this.executeFileActionWithHttpInfo(
      projectId,
      fileKey,
      actionId,
      opts
    ).then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Get file metadata.
   * Returns metadata about the specified file.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link File} and HTTP response
   */
  getFileMetadataWithHttpInfo(projectId, fileKey, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling getFileMetadata"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling getFileMetadata"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {
      version: opts['version'],
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
    let returnType = File;
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}:metadata',
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
   * Get file metadata.
   * Returns metadata about the specified file.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link File}
   */
  getFileMetadata(projectId, fileKey, opts) {
    return this.getFileMetadataWithHttpInfo(projectId, fileKey, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * List file actions.
   * Lists all actions available for the specified file.  The returned action IDs should be used when calling the [execute_file_action](#files/execute_file_action) operation.  The action mechanism allows extensions to provide additional functionality on files. It works the following way:  1. The user requests all available actions via the [list_file_actions](#files/list_file_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_file_actions](#files/list_file_actions) operation. 3. Extensions can run arbitrary code - e.g., request and check the file metadata for compatibility - and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [execute_file_action](#files/execute_file_action) operation by providing the selected action- and extension-ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action. 6. The return value of the operation can be either a simple message  (shown to the user) or a redirect to another URL (e.g., to show a web UI).  The same action mechanism is also used for other resources (e.g., services, jobs). It can support a very broad set of use-cases, for example: CSV Viewer, Tensorflow Model Deployment, ZIP Archive Explorer ...
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<module:model/ResourceAction>} and HTTP response
   */
  listFileActionsWithHttpInfo(projectId, fileKey, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling listFileActions"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling listFileActions"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {
      version: opts['version'],
      extension_id: opts['extensionId'],
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
    let returnType = [ResourceAction];
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}/actions',
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
   * List file actions.
   * Lists all actions available for the specified file.  The returned action IDs should be used when calling the [execute_file_action](#files/execute_file_action) operation.  The action mechanism allows extensions to provide additional functionality on files. It works the following way:  1. The user requests all available actions via the [list_file_actions](#files/list_file_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_file_actions](#files/list_file_actions) operation. 3. Extensions can run arbitrary code - e.g., request and check the file metadata for compatibility - and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [execute_file_action](#files/execute_file_action) operation by providing the selected action- and extension-ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action. 6. The return value of the operation can be either a simple message  (shown to the user) or a redirect to another URL (e.g., to show a web UI).  The same action mechanism is also used for other resources (e.g., services, jobs). It can support a very broad set of use-cases, for example: CSV Viewer, Tensorflow Model Deployment, ZIP Archive Explorer ...
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<module:model/ResourceAction>}
   */
  listFileActions(projectId, fileKey, opts) {
    return this.listFileActionsWithHttpInfo(projectId, fileKey, opts).then(
      function (response_and_data) {
        return response_and_data.data;
      }
    );
  }

  /**
   * List project files.
   * Lists all available files for the project.  The files can be filtered by using a `prefix`. The prefix is applied on the full path (directory path + filename).  All versions of the files can be included by setting `versions` to `true` (default is `false`).  Set `recursive` to `false` to only show files and folders (prefixes) of the current folder. The current folder is either the root folder (`/`) or the folder selected by the `prefix` parameter (has to end with `/`).
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.recursive Include all content of subfolders. (default to true)
   * @param {Boolean} opts.includeVersions Include all versions of all files. (default to false)
   * @param {String} opts.prefix Filter results to include only files whose names begin with this prefix.
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link Array.<File>} and HTTP response
   */
  listFilesWithHttpInfo(projectId, opts) {
    opts = opts || {};
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling listFiles"
      );
    }

    let pathParams = {
      project_id: projectId,
    };
    let queryParams = {
      recursive: opts['recursive'],
      include_versions: opts['includeVersions'],
      prefix: opts['prefix'],
      extension_id: opts['extensionId'],
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
    let returnType = [File];
    return this.apiClient.callApi(
      '/projects/{project_id}/files',
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
   * List project files.
   * Lists all available files for the project.  The files can be filtered by using a `prefix`. The prefix is applied on the full path (directory path + filename).  All versions of the files can be included by setting `versions` to `true` (default is `false`).  Set `recursive` to `false` to only show files and folders (prefixes) of the current folder. The current folder is either the root folder (`/`) or the folder selected by the `prefix` parameter (has to end with `/`).
   * @param {String} projectId A valid project ID.
   * @param {Object} opts Optional parameters
   * @param {Boolean} opts.recursive Include all content of subfolders. (default to true)
   * @param {Boolean} opts.includeVersions Include all versions of all files. (default to false)
   * @param {String} opts.prefix Filter results to include only files whose names begin with this prefix.
   * @param {String} opts.extensionId Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link Array.<File>}
   */
  listFiles(projectId, opts) {
    return this.listFilesWithHttpInfo(projectId, opts).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }

  /**
   * Update file metadata.
   * Updates the file metadata.  This will not change the actual content or the key of the file.  The update is applied on the existing metadata based on the JSON Merge Patch Standard ([RFC7396](https://tools.ietf.org/html/rfc7396)). Thereby, only the specified properties will be updated.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {module:model/FileInput} fileInput
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link File} and HTTP response
   */
  updateFileMetadataWithHttpInfo(projectId, fileKey, fileInput, opts) {
    opts = opts || {};
    let postBody = fileInput;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling updateFileMetadata"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling updateFileMetadata"
      );
    }
    // verify the required parameter 'fileInput' is set
    if (fileInput === undefined || fileInput === null) {
      throw new Error(
        "Missing the required parameter 'fileInput' when calling updateFileMetadata"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {
      version: opts['version'],
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
    let returnType = File;
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}',
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
   * Update file metadata.
   * Updates the file metadata.  This will not change the actual content or the key of the file.  The update is applied on the existing metadata based on the JSON Merge Patch Standard ([RFC7396](https://tools.ietf.org/html/rfc7396)). Thereby, only the specified properties will be updated.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {module:model/FileInput} fileInput
   * @param {Object} opts Optional parameters
   * @param {String} opts.version File version tag. If not specified, the latest version will be used.
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link File}
   */
  updateFileMetadata(projectId, fileKey, fileInput, opts) {
    return this.updateFileMetadataWithHttpInfo(
      projectId,
      fileKey,
      fileInput,
      opts
    ).then(function (response_and_data) {
      return response_and_data.data;
    });
  }

  /**
   * Upload a file.
   * Uploads a file to a file storage.  The file will be streamed to the selected file storage (core platform or extension).  This upload operation only supports to attach a limited set of file metadata. Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata) to add or update the metadata of the files.  The `file_key` allows to categorize the uploaded file under a virtual file structure managed by the core platform. This allows to create a directory-like structure for files from different extensions and file-storage types.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {File} file
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with an object containing data of type {@link File} and HTTP response
   */
  uploadFileWithHttpInfo(projectId, fileKey, file) {
    let postBody = null;
    // verify the required parameter 'projectId' is set
    if (projectId === undefined || projectId === null) {
      throw new Error(
        "Missing the required parameter 'projectId' when calling uploadFile"
      );
    }
    // verify the required parameter 'fileKey' is set
    if (fileKey === undefined || fileKey === null) {
      throw new Error(
        "Missing the required parameter 'fileKey' when calling uploadFile"
      );
    }
    // verify the required parameter 'file' is set
    if (file === undefined || file === null) {
      throw new Error(
        "Missing the required parameter 'file' when calling uploadFile"
      );
    }

    let pathParams = {
      project_id: projectId,
      file_key: fileKey,
    };
    let queryParams = {};
    let headerParams = {};
    let formParams = {
      file: file,
    };

    let authNames = [
      'APIKeyCookie',
      'APIKeyHeader',
      'APIKeyQuery',
      'OAuth2PasswordBearer',
    ];
    let contentTypes = ['multipart/form-data'];
    let accepts = ['application/json'];
    let returnType = File;
    return this.apiClient.callApi(
      '/projects/{project_id}/files/{file_key}',
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
   * Upload a file.
   * Uploads a file to a file storage.  The file will be streamed to the selected file storage (core platform or extension).  This upload operation only supports to attach a limited set of file metadata. Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata) to add or update the metadata of the files.  The `file_key` allows to categorize the uploaded file under a virtual file structure managed by the core platform. This allows to create a directory-like structure for files from different extensions and file-storage types.
   * @param {String} projectId A valid project ID.
   * @param {String} fileKey A valid file key.
   * @param {File} file
   * @return {Promise} a {@link https://www.promisejs.org/|Promise}, with data of type {@link File}
   */
  uploadFile(projectId, fileKey, file) {
    return this.uploadFileWithHttpInfo(projectId, fileKey, file).then(function (
      response_and_data
    ) {
      return response_and_data.data;
    });
  }
}

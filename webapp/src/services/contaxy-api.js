/* eslint-disable import/prefer-default-export */
import { ENDPOINT } from '../utils/config';
import * as Api from './contaxy-client';

export const ENDPOINT_PROJECTS = `${ENDPOINT}/projects/{project_id}`;
export const ENDPOINT_FILES = `${ENDPOINT_PROJECTS}/files/{file_key:path}:download'`;

export function fetchAPIToken(resource) {
  // TODO: fetch API token of resource
  return new Promise((resolve) => {
    resolve(resource);
  });
}

export function getFileDownloadUrl(projectId, fileKey) {
  return ENDPOINT_FILES.replace('{project_id}', projectId).replace(
    '{file_key:path}',
    fileKey
  );
}

const apiClient = new Api.ApiClient();
apiClient.basePath = ENDPOINT;
apiClient.enableCookies = true;
// the generated client includes an User-Agent header which is not allowed to set as it is controlled by the browser
delete apiClient.defaultHeaders['User-Agent'];

export const authApi = new Api.AuthApi(apiClient);
export const extensionsApi = new Api.ExtensionsApi(apiClient);
export const filesApi = new Api.FilesApi(apiClient);
export const jobsApi = new Api.JobsApi(apiClient);
export const jsonApi = new Api.JsonApi(apiClient);
export const projectsApi = new Api.ProjectsApi(apiClient);
export const servicesApi = new Api.ServicesApi(apiClient);
export const systemApi = new Api.SystemApi(apiClient);
export const usersApi = new Api.UsersApi(apiClient);

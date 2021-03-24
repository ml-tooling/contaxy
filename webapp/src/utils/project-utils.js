/* eslint-disable import/prefer-default-export */
import GlobalStateContainer from '../app/store';
import showStandardSnackbar from '../app/showStandardSnackbar';
import { projectsApi } from '../services/contaxy-api';

export const useProjectSelector = () => {
  const { setActiveProject } = GlobalStateContainer.useContainer();

  const onProjectSelect = (project) => {
    const newProject = { ...project };
    // try {
    //   const projectMetadata = await projectsApi.getProject(project.id);
    //   newProject.metadata = projectMetadata;
    // } catch (ignore) {} // eslint-disable-line no-empty

    showStandardSnackbar(`Change to project '${project.id}'`);
    setActiveProject(newProject);
  };

  return onProjectSelect;
};

export const loadProjects = async () => {
  return projectsApi
    .listProjects()
    .then((result) => result)
    .catch((err) => showStandardSnackbar(JSON.stringify(err.response.body)));
};

/* eslint-disable import/prefer-default-export */
import GlobalStateContainer from '../app/store';
import showStandardSnackbar from '../app/showStandardSnackbar';

export const getProjectPermissionId = (project, permissionLevel) => {
  const level = permissionLevel ? `#${permissionLevel}` : '';
  return `projects/${project.id}${level}`;
};

export const getUserPemissionId = (user, permissionLevel) => {
  const level = permissionLevel ? `#${permissionLevel}` : '';
  return `users/${user.id}${level}`;
};

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

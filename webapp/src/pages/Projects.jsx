import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@material-ui/core/Grid';

import ProjectCard from '../components/ProjectCard';
import Widget from '../components/Widget';
import WidgetsGrid from '../components/WidgetsGrid';
import GlobalStateContainer from '../app/store';
import showStandardSnackbar from '../app/showStandardSnackbar';
import { fetchAPIToken, projectsApi } from '../services/contaxy-api';
import ManageProjectDialog from '../components/Dialogs/ManageProjectDialog';
import { useShowAppDialog } from '../app/AppDialogServiceProvider';
import ApiTokenDialog from '../components/Dialogs/ApiTokenDialog';
import { loadProjects, useProjectSelector } from '../utils/project-utils';

function Projects() {
  const { t } = useTranslation();
  const showAppDialog = useShowAppDialog();
  const {
    activeProject,
    projects,
    setProjects,
  } = GlobalStateContainer.useContainer();
  const onProjectSelect = useProjectSelector();

  const onClickManageMembers = (project) => {
    showAppDialog(ManageProjectDialog, { project });
  };

  const onApiTokenClick = async (project) => {
    // TODO: pass correct resource for which the API Token should be generated
    const fetchedToken = await fetchAPIToken(project.id);
    showAppDialog(ApiTokenDialog, { token: fetchedToken });
  };

  const onDeleteProject = async (project) => {
    try {
      await projectsApi.deleteProject(project.id);
      showStandardSnackbar(`Delete project '${project.id}'`);
      setProjects(await loadProjects());
    } catch (err) {
      // ignore
    }
  };

  const projectElements = projects.map((project) => {
    return (
      <ProjectCard
        key={project.id}
        project={project}
        onApiTokenClick={onApiTokenClick}
        onClickManageMembers={onClickManageMembers}
        onDeleteProject={onDeleteProject}
        onSelect={onProjectSelect}
      />
    );
  });

  const fileNumber = activeProject.metadata
    ? activeProject.metadata.fileNumber
    : 0;
  const serviceNumber = activeProject.metadata
    ? activeProject.metadata.serviceNumber
    : 0;

  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget
          name={t('file_plural')}
          icon="folder"
          value={fileNumber}
          color="light-green"
        />
        <Widget
          name="Services"
          icon="apps"
          value={serviceNumber}
          color="orange"
        />
      </WidgetsGrid>
      <Grid container spacing={3}>
        {projectElements}
      </Grid>
    </div>
  );
}

export default Projects;

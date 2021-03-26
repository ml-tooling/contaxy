import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import { useTranslation } from 'react-i18next';

import Button from '@material-ui/core/Button';
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
import { useProjectSelector } from '../utils/project-utils';
import AddProjectDialog from '../components/Dialogs/AddProjectDialog';

function Projects(props) {
  const { className } = props;
  const { t } = useTranslation();
  const showAppDialog = useShowAppDialog();
  const {
    activeProject,
    projects,
    loadProjects,
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

  const onAddProject = () => {
    showAppDialog(AddProjectDialog, {
      onAdd: async ({ id, name, description }, onClose) => {
        const projectInput = {
          id,
          display_name: name,
          description,
        };
        try {
          await projectsApi.createProject(projectInput);
          showStandardSnackbar(`Created project '${id}'`);
          onClose();
          loadProjects();
        } catch (err) {
          showStandardSnackbar(
            `Could not create project. Error: ${err.statusText}`
          );
        }
      },
    });
  };

  const onDeleteProject = async (project) => {
    try {
      await projectsApi.deleteProject(project.id);
      showStandardSnackbar(`Delete project '${project.id}'`);
      loadProjects();
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
      <Button
        variant="contained"
        color="primary"
        onClick={onAddProject}
        className={`${className} button`}
      >
        {`${t('add')} ${t('project')}`}
      </Button>
      <Grid container spacing={3}>
        {projectElements}
      </Grid>
    </div>
  );
}

Projects.propTypes = {
  className: PropTypes.string,
};

Projects.defaultProps = {
  className: '',
};

const StyledProjects = styled(Projects)`
  &.button {
    margin: 8px 0px;
  }
`;

export default StyledProjects;

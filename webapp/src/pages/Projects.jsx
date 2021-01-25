import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@material-ui/core/Grid';

import ProjectCard from '../components/ProjectCard';
import Widget from '../components/Widget';
import WidgetsGrid from '../components/WidgetsGrid';
import GlobalStateContainer from '../app/store';

function Projects() {
  const { t } = useTranslation();
  const { projects, setActiveProject } = GlobalStateContainer.useContainer();

  const projectElements = projects.map((project) => {
    return (
      <ProjectCard
        key={project.id}
        project={project}
        onSelect={setActiveProject}
      />
    );
  });

  // TODO: add correct value to widget
  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget
          name={t('file_plural')}
          icon="folder"
          value="2"
          color="light-green"
        />
        <Widget name="Services" icon="apps" value="2" color="orange" />
      </WidgetsGrid>
      <Grid container spacing={3}>
        {projectElements}
      </Grid>
    </div>
  );
}

export default Projects;

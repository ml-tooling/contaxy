import React from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';

import Grid from '@material-ui/core/Grid';

import ProjectCard from '../components/ProjectCard';
import Widget from '../components/Widget';
import WidgetsGrid from '../components/WidgetsGrid';

function Projects(props) {
  const { t } = useTranslation();
  const { projects } = props;

  const projectElements = projects.map((project) => {
    return <ProjectCard key={project.id} project={project} />;
  });

  // TODO: add correct value to widget
  return (
    <>
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
    </>
  );
}

Projects.propTypes = {
  projects: PropTypes.arrayOf(Object),
};

Projects.defaultProps = {
  projects: [
    {
      id: 'foobar',
      name: 'foobar',
      description: '',
      creator: 'admin',
      visibility: 'private',
      createdAt: 1606470094642,
    },
    {
      id: 'ml-lab-demo',
      name: 'ml-lab-demo',
      description: '',
      creator: 'admin',
      visibility: 'private',
      createdAt: 1607439288065,
    },
  ],
};

export default Projects;

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import CardHeader from '@material-ui/core/CardHeader';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import * as Jdenticon from 'jdenticon';

function ProjectCard(props) {
  const { project } = props;
  const svgRef = useRef(null);
  useEffect(() => {
    Jdenticon.update(svgRef.current);
  }, [svgRef]);

  // TODO: add functionality to project card buttons
  return (
    <Grid item spacing={3}>
      <Card>
        <CardHeader
          avatar={
            <Avatar
              alt={project.name}
              // src={imageUrl}
            >
              <svg
                ref={svgRef}
                width="60"
                height="60"
                style={{ backgroundColor: 'white' }}
                data-jdenticon-value={project.name}
              />
            </Avatar>
          }
          title={project.name}
          subheader={project.createdAt}
        />
        <CardContent>
          <Typography>{project.description}</Typography>
        </CardContent>
        <CardActions>
          <Button>SELECT</Button>
          <Button>MEMBERS</Button>
          <Button>TOKEN</Button>
          <Button>DELETE</Button>
        </CardActions>
      </Card>
    </Grid>
  );
}

ProjectCard.propTypes = {
  project: PropTypes.instanceOf(Object).isRequired,
};

function Projects(props) {
  const { projects } = props;

  const projectElements = projects.map((project) => {
    return <ProjectCard project={project} />;
  });

  return (
    <Grid container spacing={3}>
      {projectElements}
    </Grid>
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

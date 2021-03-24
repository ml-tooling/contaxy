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
  const {
    onApiTokenClick,
    onClickManageMembers,
    onDeleteProject,
    onSelect,
    project,
  } = props;
  const svgRef = useRef(null);
  useEffect(() => {
    Jdenticon.update(svgRef.current);
  }, [svgRef]);

  const createdAt = project.created_at
    ? project.created_at.toLocaleString()
    : '';

  return (
    <>
      <Grid item>
        <Card>
          <CardHeader
            avatar={
              <Avatar alt={project.display_name}>
                <svg
                  ref={svgRef}
                  width="60"
                  height="60"
                  style={{ backgroundColor: 'white' }}
                  data-jdenticon-value={project.display_name}
                />
              </Avatar>
            }
            title={project.display_name}
            subheader={createdAt}
          />
          <CardContent>
            <Typography>{project.description}</Typography>
          </CardContent>
          <CardActions>
            <Button onClick={() => onSelect(project)}>SELECT</Button>
            <Button onClick={() => onClickManageMembers(project)}>
              MEMBERS
            </Button>
            <Button onClick={() => onApiTokenClick(project)}>TOKEN</Button>
            <Button onClick={() => onDeleteProject(project)}>DELETE</Button>
          </CardActions>
        </Card>
      </Grid>
    </>
  );
}

ProjectCard.propTypes = {
  onApiTokenClick: PropTypes.func.isRequired,
  onClickManageMembers: PropTypes.func.isRequired,
  onDeleteProject: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
  project: PropTypes.instanceOf(Object).isRequired,
};

export default ProjectCard;

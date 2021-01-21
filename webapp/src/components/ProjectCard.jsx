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

import useApiTokenDialog from '../app/useApiTokenDialog';
import { fetchAPIToken } from '../services/lab-api';

function ProjectCard(props) {
  const { showApiTokenDialog, ApiTokenDialog } = useApiTokenDialog();
  const { project } = props;
  const svgRef = useRef(null);
  useEffect(() => {
    Jdenticon.update(svgRef.current);
  }, [svgRef]);

  const handleApiTokenClick = async () => {
    // TODO: pass correct resource for which the API Token should be generated
    const fetchedToken = await fetchAPIToken('foobar');
    showApiTokenDialog(fetchedToken);
  };

  // TODO: add functionality to project card buttons
  return (
    <>
      <Grid item>
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
            <Button onClick={handleApiTokenClick}>TOKEN</Button>
            <Button>DELETE</Button>
          </CardActions>
        </Card>
      </Grid>

      <ApiTokenDialog />
    </>
  );
}

ProjectCard.propTypes = {
  project: PropTypes.instanceOf(Object).isRequired,
};

export default ProjectCard;

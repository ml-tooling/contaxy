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

import { fetchAPIToken } from '../services/contaxy-api';
import showStandardSnackbar from '../app/showStandardSnackbar';
import { useShowAppDialog } from '../app/AppDialogServiceProvider';
import ApiTokenDialog from './Dialogs/ApiTokenDialog';
import ManageProjectDialog from './Dialogs/ManageProjectDialog';

function ProjectCard(props) {
  const showAppDialog = useShowAppDialog();

  const { onSelect, project } = props;
  const svgRef = useRef(null);
  useEffect(() => {
    Jdenticon.update(svgRef.current);
  }, [svgRef]);

  const handleApiTokenClick = async () => {
    // TODO: pass correct resource for which the API Token should be generated
    const fetchedToken = await fetchAPIToken('foobar');
    showAppDialog(ApiTokenDialog, { token: fetchedToken });
  };

  const handleManageMembersClick = () => {
    showAppDialog(ManageProjectDialog, { project });
  };

  const handleProjectSelectClick = () => {
    showStandardSnackbar(`Change to project '${project.name}'`);
    onSelect(project);
  };

  const handleDeleteClick = () => {
    showStandardSnackbar(`Delete project '${project.name}'`);
  };

  // TODO: add functionality to project card buttons
  return (
    <>
      <Grid item>
        <Card>
          <CardHeader
            avatar={
              <Avatar alt={project.name}>
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
            <Button onClick={handleProjectSelectClick}>SELECT</Button>
            <Button onClick={handleManageMembersClick}>MEMBERS</Button>
            <Button onClick={handleApiTokenClick}>TOKEN</Button>
            <Button onClick={handleDeleteClick}>DELETE</Button>
          </CardActions>
        </Card>
      </Grid>
    </>
  );
}

ProjectCard.propTypes = {
  onSelect: PropTypes.func.isRequired,
  project: PropTypes.instanceOf(Object).isRequired,
};

export default ProjectCard;

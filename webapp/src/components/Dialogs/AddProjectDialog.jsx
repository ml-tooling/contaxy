import React, { useState } from 'react';

import { useTranslation } from 'react-i18next';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import TextField from '@material-ui/core/TextField';

import { projectsApi } from '../../services/contaxy-api';
import showStandardSnackbar from '../../app/showStandardSnackbar';

const VALID_PROJECT_ID = new RegExp('^[a-z0-9-:/.]{0,25}$');
const VALID_PROJECT_NAME = new RegExp('^[a-zA-Z0-9-\\s]*$');
function AddProjectDialog(props) {
  const { className, onAdd, onClose } = props;
  const { t } = useTranslation();

  const [projectInput, setProjectInput] = useState({
    id: '',
    name: '',
    description: '',
  });
  const [isProjectIdDisabled, setIsProjectIdDisabled] = useState(true);

  const changeInput = async (e) => {
    const targetName = e.target.name;
    const targetValue = e.target.value;
    setProjectInput({ ...projectInput, [targetName]: targetValue });
  };

  const changeName = async (e) => {
    const input = e.target.value;
    let projectId = projectInput.id;
    if (input && input.length > 3) {
      try {
        projectId = await projectsApi.suggestProjectId(input);
      } catch (err) {
        showStandardSnackbar(
          'Error in getting a suggested project id. Please edit it manually.'
        );
      }
    }

    setProjectInput({ ...projectInput, name: input, id: projectId });
    setIsProjectIdDisabled(true);
  };

  const isProjectIdValid = VALID_PROJECT_ID.test(projectInput.id);
  const isProjectNameValid = VALID_PROJECT_NAME.test(projectInput.name);

  let displayNameHelperText = 'The name must be at least 4 characters long.';
  if (!isProjectNameValid) {
    displayNameHelperText = 'The name contains invalid characters.';
  }

  return (
    <Dialog open>
      <DialogTitle>{`${t('add')} ${t('project')}`}</DialogTitle>
      <DialogContent>
        <TextField
          required
          label="Project Displayname"
          name="name"
          type="text"
          value={projectInput.name}
          onChange={changeName}
          error={!isProjectNameValid}
          helperText={displayNameHelperText}
          margin="dense"
          fullWidth
        />
        <div className={`${className} projectIdFields`}>
          <TextField
            required
            disabled={isProjectIdDisabled}
            label="Project Id"
            name="id"
            type="text"
            value={projectInput.id}
            onChange={changeInput}
            error={!isProjectIdValid}
            helperText={
              !isProjectIdValid
                ? 'The project id must be at most 25 characters long and contain only valid characters.'
                : 'The project id is auto-generated based on the name. You can also edit it manually.'
            }
            margin="dense"
            fullWidth={!isProjectIdDisabled}
          />
          {isProjectIdDisabled ? (
            <Button onClick={() => setIsProjectIdDisabled(false)}>Edit</Button>
          ) : (
            false
          )}
        </div>
        <TextField
          label="Project Description"
          name="description"
          type="text"
          value={projectInput.description}
          onChange={changeInput}
          margin="dense"
          fullWidth
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          CANCEL
        </Button>
        <Button
          disabled={!isProjectIdValid || !projectInput.id}
          onClick={() => onAdd(projectInput, onClose)}
          color="primary"
        >
          ADD
        </Button>
      </DialogActions>
    </Dialog>
  );
}

AddProjectDialog.propTypes = {
  className: PropTypes.string,
  onAdd: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

AddProjectDialog.defaultProps = {
  className: '',
};

const StyledAddProjectDialog = styled(AddProjectDialog)`
  &.projectIdFields {
    display: flex;
  }
`;

export default StyledAddProjectDialog;

import React, { useState } from 'react';

import { useTranslation } from 'react-i18next';
import PropTypes from 'prop-types';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import TextField from '@material-ui/core/TextField';

const VALID_PROJECT_ID = new RegExp('[^a-z0-9-:/.]');

function AddProjectDialog(props) {
  const { onAdd, onClose } = props;
  const { t } = useTranslation();

  const [projectInput, setProjectInput] = useState({
    id: '',
    name: '',
    description: '',
  });
  const changeInput = (e) => {
    setProjectInput({ ...projectInput, [e.target.name]: e.target.value });
  };

  const isProjectIdInvalid = VALID_PROJECT_ID.test(projectInput.id);

  return (
    <Dialog open>
      <DialogTitle>{`${t('add')} ${t('project')}`}</DialogTitle>
      <DialogContent>
        <TextField
          required
          label="Project Id"
          name="id"
          type="text"
          value={projectInput.id}
          onChange={changeInput}
          error={isProjectIdInvalid}
          helperText={isProjectIdInvalid ? 'Project Id is not valid' : null}
          margin="dense"
          fullWidth
        />
        <TextField
          label="Project Displayname"
          name="name"
          type="text"
          value={projectInput.name}
          onChange={changeInput}
          margin="dense"
          fullWidth
        />
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
          disabled={isProjectIdInvalid || !projectInput.id}
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
  onAdd: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default AddProjectDialog;

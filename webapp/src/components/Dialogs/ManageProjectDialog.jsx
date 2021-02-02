import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Autocomplete from '@material-ui/lab/Autocomplete';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import HighlightOff from '@material-ui/icons/HighlightOff';
import IconButton from '@material-ui/core/IconButton';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import TextField from '@material-ui/core/TextField';

import GlobalStateContainer from '../../app/store';

function ManageProjectDialog(props) {
  const [projectMembers, setProjectMembers] = useState([]);
  const [userToAdd, setUserToAdd] = useState({}); // set to empty object so that material-ui knows that it is a controlled input

  const { users } = GlobalStateContainer.useContainer();
  const { className, project, onClose } = props;

  useEffect(() => {
    // TODO: load project members
    setProjectMembers([{ id: 'alpha', name: 'Alpha Beta' }]);
  }, [project]);

  const handleSelectUser = (e, newValue) => {
    setUserToAdd(newValue);
    return newValue;
  };

  const handleAddUser = () => {
    // TODO: add user `userToAdd` to project
  };

  const handleRemoveMemberFromProject = (user) => {
    // TODO: remove user from project in backend
    return user;
  };

  return (
    <Dialog open>
      <DialogTitle>Members of Your Project</DialogTitle>
      <DialogContent>
        <List>
          {projectMembers.map((member) => {
            return (
              <ListItem key={member.id}>
                <ListItemText primary={member.name} />
                <ListItemSecondaryAction>
                  <IconButton onClick={handleRemoveMemberFromProject}>
                    <HighlightOff />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            );
          })}
        </List>
        {/* <Input value={userToAdd} placeholder="Search users" /> */}
        <div className={`${className} userInputContainer`}>
          <Autocomplete
            className={`${className} userInputField`}
            getOptionLabel={(option) => option.name || ''}
            onChange={handleSelectUser}
            openOnFocus
            options={users}
            renderInput={(params) => (
              <TextField
                {...params} // eslint-disable-line react/jsx-props-no-spreading
                label="Available users"
                margin="normal"
              />
            )}
            value={userToAdd}
          />
          <Button
            color="secondary"
            onClick={handleAddUser}
            disabled={userToAdd === null || Object.keys(userToAdd).length === 0}
          >
            ADD
          </Button>
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          CANCEL
        </Button>
      </DialogActions>
    </Dialog>
  );
}

ManageProjectDialog.propTypes = {
  className: PropTypes.string,
  onClose: PropTypes.func.isRequired,
  project: PropTypes.instanceOf(Object).isRequired,
};

ManageProjectDialog.defaultProps = {
  className: '',
};

const StyledManageProjectDialog = styled(ManageProjectDialog)`
  &.userInputContainer {
    display: flex;
  }

  &.userInputField {
    min-width: 80%;
  }
`;

export default StyledManageProjectDialog;

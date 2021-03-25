import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AccountCircle from '@material-ui/icons/AccountCircle';
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
import Typography from '@material-ui/core/Typography';

import GlobalStateContainer from '../../app/store';
import { useProjectMembers } from '../../services/api-hooks';

function ManageProjectDialog(props) {
  const { className, project, onClose } = props;
  const users = GlobalStateContainer.useContainer().getUsers();
  const initialUserToAdd = users && users.length > 0 ? users[0] : {};
  const [userToAdd, setUserToAdd] = useState(initialUserToAdd); // set to empty object so that material-ui knows that it is a controlled input
  const projectMembers = useProjectMembers(project.id);

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
      <DialogTitle>{`Manage "${project.id}"`}</DialogTitle>
      <DialogContent>
        <Typography variant="subtitle1">Project members:</Typography>
        <List>
          {projectMembers.map((member) => {
            return (
              <ListItem key={member.id}>
                <AccountCircle />
                <ListItemText primary={member.username} />
                <ListItemSecondaryAction>
                  <IconButton onClick={handleRemoveMemberFromProject}>
                    <HighlightOff color="secondary" />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            );
          })}
        </List>
        {/* <Input value={userToAdd} placeholder="Search users" /> */}
        <Typography
          className={`${className} addUserHeader`}
          variant="subtitle1"
        >
          Add members:
        </Typography>
        <div className={`${className} userInputContainer`}>
          <Autocomplete
            className={`${className} userInputField`}
            getOptionLabel={(option) => option.name || ''}
            onChange={handleSelectUser}
            openOnFocus
            options={users}
            size="small"
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
  &.addUserHeader {
    margin-top: 16px;
  }

  &.userInputContainer {
    display: flex;
  }

  &.userInputField {
    min-width: 80%;
  }
`;

export default StyledManageProjectDialog;

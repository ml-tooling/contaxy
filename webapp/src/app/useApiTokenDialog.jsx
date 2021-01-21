import React, { useRef, useState } from 'react';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';

import setClipboardText from '../utils/clipboard';
import useAppDialog from './useAppDialog';

const useApiTokenDialog = () => {
  const textFieldRef = useRef();
  const [token, setToken] = useState();
  const { show, hide, RenderAppDialog } = useAppDialog();

  const handleCopyClick = () => {
    setClipboardText(null, textFieldRef.current);
  };

  const showApiTokenDialog = (_token) => {
    setToken(_token);
    show();
  };

  const ApiTokenDialog = () => {
    return (
      <RenderAppDialog>
        <Dialog open>
          <DialogTitle>API TOKEN</DialogTitle>
          <DialogContent>
            <DialogContentText ref={textFieldRef}>{token}</DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => handleCopyClick()} color="primary">
              COPY
            </Button>
            <Button onClick={hide} color="primary">
              OK
            </Button>
          </DialogActions>
        </Dialog>
      </RenderAppDialog>
    );
  };

  return {
    showApiTokenDialog,
    ApiTokenDialog,
  };
};

export default useApiTokenDialog;

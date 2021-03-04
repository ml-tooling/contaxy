import React, { useRef } from 'react';
import PropTypes from 'prop-types';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';

import setClipboardText from '../../utils/clipboard';

function ApiTokenDialog({ token, onClose }) {
  const textFieldRef = useRef();

  const handleCopyClick = () => {
    setClipboardText(null, textFieldRef.current);
  };

  return (
    <Dialog open>
      <DialogTitle>API TOKEN</DialogTitle>
      <DialogContent>
        <DialogContentText ref={textFieldRef}>{token}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => handleCopyClick()} color="primary">
          COPY
        </Button>
        <Button onClick={onClose} color="primary">
          OK
        </Button>
      </DialogActions>
    </Dialog>
  );
}

ApiTokenDialog.propTypes = {
  token: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ApiTokenDialog;

import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { useTranslation } from 'react-i18next';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import TextField from '@material-ui/core/TextField';
import { DialogContentText } from '@material-ui/core';

import KeyValueInputs from './KeyValueInputs';

const IMAGE_NAME = new RegExp('[^a-zA-Z0-9-_:/.]');
const SERVICE_NAME_REGEX = new RegExp(
  '^([a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9])?$'
);

function DeployContainerDialog(props) {
  const { t } = useTranslation();
  const [containerImage, setContainerImage] = useState('');
  const [deploymentName, setDeploymentName] = useState('');
  const [deploymentParameters, setDeploymentParameters] = useState([]);

  const handleContainerImageChange = (e) => setContainerImage(e.target.value);
  const handleNameChange = (e) => setDeploymentName(e.target.value);

  const { onClose, onDeploy } = props;

  const isContainerImageInvalid = IMAGE_NAME.test(containerImage);
  const isDeploymentNameInvalid = !SERVICE_NAME_REGEX.test(deploymentName);

  return (
    <Dialog open>
      <DialogTitle>{`${t('add')} ${t('deployment')}`}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Make a new deployment in the selected project based on the specific
          Docker image. Please make sure that the image is a compatible ML Lab
          service.
        </DialogContentText>
        <TextField
          label="Container Image"
          type="text"
          value={containerImage}
          onChange={handleContainerImageChange}
          onBlur={() => {}} // TODO: add here the "caching" logic handling
          autoComplete="on"
          error={isContainerImageInvalid}
          helperText={
            isContainerImageInvalid ? 'Image Name is not valid' : null
          }
          fullWidth
          margin="dense"
        />
        <TextField
          label="Deployment Name (optional)"
          type="text"
          value={deploymentName}
          onChange={handleNameChange}
          autoComplete="on"
          error={isDeploymentNameInvalid}
          helperText={isDeploymentNameInvalid ? 'Name is not valid' : null}
          fullWidth
          margin="dense"
        />
        <KeyValueInputs
          onKeyValuePairChange={(keyValuePairs) => {
            setDeploymentParameters(keyValuePairs);
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          CANCEL
        </Button>
        <Button
          onClick={() =>
            onDeploy(containerImage, deploymentName, deploymentParameters)
          }
          color="primary"
        >
          DEPLOY
        </Button>
      </DialogActions>
    </Dialog>
  );
}

DeployContainerDialog.propTypes = {
  onClose: PropTypes.func.isRequired,
  onDeploy: PropTypes.func.isRequired,
};

export default DeployContainerDialog;

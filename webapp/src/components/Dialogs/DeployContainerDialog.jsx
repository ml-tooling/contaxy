import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { useTranslation } from 'react-i18next';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import TextField from '@material-ui/core/TextField';

import KeyValueInputs from './KeyValueInputs';

const VALID_IMAGE_NAME = new RegExp('[^a-zA-Z0-9-_:/.]');
const SERVICE_NAME_REGEX = new RegExp(
  '^([a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9])?$'
);

function DeployContainerDialog(props) {
  const { onClose, onDeploy } = props;

  const { t } = useTranslation();

  const [deploymentInput, setDeploymentInput] = useState({
    containerImage: '',
    deploymentName: '',
    deploymentParameters: {},
  });

  const onChange = (e) =>
    setDeploymentInput({ ...deploymentInput, [e.target.name]: e.target.value });

  const isContainerImageInvalid = VALID_IMAGE_NAME.test(
    deploymentInput.containerImage
  );
  const isDeploymentNameInvalid = !SERVICE_NAME_REGEX.test(
    deploymentInput.deploymentName
  );

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
          required
          label="Container Image"
          type="text"
          name="containerImage"
          value={deploymentInput.containerImage}
          onChange={onChange}
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
          label="Deployment Name"
          type="text"
          name="deploymentName"
          value={deploymentInput.deploymentName}
          onChange={onChange}
          autoComplete="on"
          error={isDeploymentNameInvalid}
          helperText={isDeploymentNameInvalid ? 'Name is not valid' : null}
          fullWidth
          margin="dense"
        />
        <KeyValueInputs
          onKeyValuePairChange={(keyValuePairs) => {
            setDeploymentInput({
              ...deploymentInput,
              deploymentParameters: keyValuePairs,
            });
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          CANCEL
        </Button>
        <Button
          disabled={
            isContainerImageInvalid ||
            isDeploymentNameInvalid ||
            !deploymentInput.containerImage
          }
          onClick={() => onDeploy(deploymentInput, onClose)}
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

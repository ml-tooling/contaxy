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

function DeployServiceDialog(props) {
  const { t } = useTranslation();
  const [containerImage, setContainerImage] = useState('');
  const [serviceName, setServiceName] = useState('');
  const [serviceParameters, setServiceParameters] = useState([]);

  const handleContainerImageChange = (e) => setContainerImage(e.target.value);
  const handleServiceNameChange = (e) => setServiceName(e.target.value);

  const { onClose } = props;

  const isContainerImageInvalid = IMAGE_NAME.test(containerImage);
  const isServiceNameInvalid = !SERVICE_NAME_REGEX.test(serviceName);

  return (
    <Dialog open>
      <DialogTitle>{`${t('add')} ${t('service')}`}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Deploy a new service to the selected project based on the specific
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
        />
        <TextField
          label="Service Name (optional)"
          type="text"
          value={serviceName}
          onChange={handleServiceNameChange}
          autoComplete="on"
          error={isServiceNameInvalid}
          helperText={isServiceNameInvalid ? 'Service Name is not valid' : null}
          fullWidth
        />
        <KeyValueInputs
          onKeyValuePairChange={(keyValuePairs) => {
            setServiceParameters(keyValuePairs);
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          CANCEL
        </Button>
        <Button
          onClick={() => {
            // do something with the image, name and parameters
            console.log(serviceParameters);
          }}
          color="primary"
        >
          DEPLOY
        </Button>
      </DialogActions>
    </Dialog>
  );
}

DeployServiceDialog.propTypes = {
  onClose: PropTypes.func.isRequired,
};

export default DeployServiceDialog;

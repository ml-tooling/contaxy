import React, { useState } from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';
import Input from '@material-ui/core/Input';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import './App.css';

function App({ className }) {
  const [fileKey, setFileKey] = useState('');
  const [base64File, setBase64File] = useState();

  const handleSubmit = () => {
    // '/ui/' is the route of the Opyrator extension webapp
    const url = `${window.location.pathname.split('/ui/')[0]}/deploy`;
    const formData = new global.FormData();

    if (fileKey) {
      formData.append('filekey', fileKey);
    } else if (base64File) {
      formData.append('filedata', base64File.split(',')[1]);
    } else {
      return;
    }

    global.fetch(url, { method: 'POST', body: formData }).then(() => {});
  };

  const loadFile = async (file) => {
    return new Promise((resolve, reject) => {
      if (!file) resolve(null);
      const reader = new global.FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const handleSelectedFile = async (e) => {
    const file = e.target.files[0];
    try {
      const loadedFile = await loadFile(file);
      setBase64File(loadedFile);
    } catch (err) {
      setBase64File(null);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h1">Deploy your Opyrator!</Typography>
        <Typography>
          Upload an Opyrator file and deploy it via Contaxy!
        </Typography>
        <form className={`${className} form`} noValidate autoComplete="off">
          <TextField
            disabled={Boolean(base64File)}
            className={`${className} formTextField`}
            label="File key"
            onChange={(e) => {
              setFileKey(e.target.value);
            }}
            variant="filled"
          />

          <StyledSpan>-- or --</StyledSpan>

          <Input
            inputProps={{ accept: '.py' }}
            disabled={Boolean(fileKey)}
            className={`${className} formFileInput`}
            type="file"
            onChange={handleSelectedFile}
          />

          <Button color="primary" onClick={handleSubmit} variant="contained">
            Submit
          </Button>
        </form>
      </header>
    </div>
  );
}

App.propTypes = {
  className: PropTypes.string,
};

App.defaultProps = {
  className: '',
};

const StyledSpan = styled.span`
  color: ${(props) => props.theme.palette.gray};
  font-size: 0.75rem;
`;

const StyledApp = styled(App)`
  &.form {
    display: flex;
    flex-direction: column;
  }

  &.formFileInput {
    margin-bottom: 8px;
  }

  &.formTextField {
    /* display: block; */
    margin-bottom: 8px;
  }
`;

export default StyledApp;

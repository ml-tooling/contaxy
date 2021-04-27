import React, { useRef } from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import './App.css';

function App({ className }) {
  const valueRef = useRef('');
  const handleSubmit = () => {
    // '/ui/' is the route of the Opyrator extension webapp
    const url = `${window.location.pathname.split('/ui/')[0]}/deploy`;
    const formData = new global.FormData();
    formData.append('filekey', valueRef.current.value);

    global.fetch(url, { method: 'POST', body: formData }).then(() => {});
  };

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h1">Deploy your Opyrator!</Typography>
        <Typography>
          Upload an Opyrator file and deploy it via Contaxy!
        </Typography>
        <form noValidate autoComplete="off">
          <TextField
            className={`${className} formTextField`}
            label="File key"
            variant="filled"
            inputRef={valueRef}
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

const StyledApp = styled(App)`
  &.formTextField {
    display: block;
    margin-bottom: 8px;
  }
`;

export default StyledApp;

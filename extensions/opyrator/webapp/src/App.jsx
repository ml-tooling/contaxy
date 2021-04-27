import React, { useRef } from 'react';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import './App.css';

function App() {
  const valueRef = useRef('');
  const handleSubmit = () => {
    const url = `${window.location.pathname.substring(
      0,
      window.location.pathname.lastIndexOf('/')
    )}/deplopy`;
    global.fetch(url, { method: 'POST' }).then((res) => console.log(res));
  };

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h1">Deploy your Opyrator!</Typography>
        <Typography>
          Upload an Opyrator file and deploy it via Contaxy!
        </Typography>
        <form noValidate autoComplete="off">
          <TextField label="File key" variant="filled" inputRef={valueRef} />
          <Button variant="contained" onClick={handleSubmit}>
            Submit
          </Button>
        </form>
      </header>
    </div>
  );
}

export default App;

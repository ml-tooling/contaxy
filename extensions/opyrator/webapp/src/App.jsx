import React, { useRef } from 'react';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';

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
        <p>Deploy your Opyrator!</p>
        <form noValidate autoComplete="off">
          <TextField label="File key" variant="filled" inputRef={valueRef} />
          <Button variant="contained" onClick={handleSubmit} />
        </form>
      </header>
    </div>
  );
}

export default App;

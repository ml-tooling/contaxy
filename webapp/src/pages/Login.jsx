import React, { useReducer } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';

import { authApi } from '../services/contaxy-api';

function Login(props) {
  const { className } = props;

  const [formInput, setFormInput] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      username: '',
      password: '',
    }
  );

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(formInput);
    authApi.requestToken('password', {
      username: formInput.username,
      password: formInput.password,
    });
    return false;
  };

  const handleInput = (event) => {
    const { name, value } = event.target;
    setFormInput({ [name]: value });
  };

  return (
    <form className={`${className} container`} onSubmit={handleSubmit}>
      <TextField
        required
        className={`${className} input`}
        id="username"
        name="username"
        label="Username"
        variant="filled"
        defaultValue={formInput.username}
        onChange={handleInput}
      />
      <TextField
        required
        className={`${className} input`}
        id="password"
        name="password"
        label="Password"
        type="password"
        autoComplete="current-password"
        variant="filled"
        defaultValue={formInput.password}
        onChange={handleInput}
      />
      <Button
        type="submit"
        variant="contained"
        color="primary"
        className={className}
      >
        Login
      </Button>
    </form>
  );
}

Login.propTypes = {
  className: PropTypes.string,
};

Login.defaultProps = {
  className: '',
};

const StyledLogin = styled(Login)`
  &.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 24px;
  }

  &.input {
    margin-bottom: 8px;
  }
`;

export default StyledLogin;

import React from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';

import { getExternalLoginPageUrl } from '../services/contaxy-api';

function ExternalLogin(props) {
  const { className } = props;

  return (
    <div className={`${className} container`}>
      <Button
        variant="contained"
        color="primary"
        className={`${className} input`}
        href={getExternalLoginPageUrl()}
      >
        Go To Login
      </Button>
    </div>
  );
}

ExternalLogin.propTypes = {
  className: PropTypes.string,
};

ExternalLogin.defaultProps = {
  className: '',
};

const StyledExternalLogin = styled(ExternalLogin)`
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

export default StyledExternalLogin;

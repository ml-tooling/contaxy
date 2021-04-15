import React, { useEffect } from 'react';

import PropTypes from 'prop-types';

import { Redirect, Route } from 'react-router-dom';

import { getLoginPageUrl } from '../../services/contaxy-api';

function ExternalLoginRoute({ isAuthenticated }) {
  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = getLoginPageUrl();
    }
  }, [isAuthenticated]);

  return (
    <Route
      render={(props) => (
        <Redirect to={{ pathname: '/', state: { from: props.location } }} /> // eslint-disable-line react/prop-types
      )}
    />
  );
}

ExternalLoginRoute.propTypes = {
  isAuthenticated: PropTypes.bool,
};
ExternalLoginRoute.defaultProps = {
  isAuthenticated: false,
};

export default ExternalLoginRoute;

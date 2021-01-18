import React from 'react';
import PropTypes from 'prop-types';

import { Route, Redirect } from 'react-router-dom';

/* eslint-disable react/jsx-props-no-spreading */
function LoginRoute({ component: Component, isAuthenticated, ...rest }) {
  return (
    <Route
      {...rest}
      render={(props) =>
        !isAuthenticated ? (
          <Component {...props} />
        ) : (
          <Redirect to={{ pathname: '/', state: { from: props.location } }} /> // eslint-disable-line react/prop-types
        )
      }
    />
  );
}

LoginRoute.propTypes = {
  component: PropTypes.func.isRequired,
  isAuthenticated: PropTypes.bool,
};

LoginRoute.defaultProps = {
  isAuthenticated: false,
};

export default LoginRoute;

import React from 'react';

import PropTypes from 'prop-types';

import { Redirect, Route } from 'react-router-dom';

/* eslint-disable react/jsx-props-no-spreading */
function ExternalLoginRoute({
  component: Component,
  isAuthenticated,
  ...rest
}) {
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

ExternalLoginRoute.propTypes = {
  component: PropTypes.instanceOf(Object).isRequired,
  isAuthenticated: PropTypes.bool,
};

ExternalLoginRoute.defaultProps = {
  isAuthenticated: false,
};

export default ExternalLoginRoute;

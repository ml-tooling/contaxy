import React from 'react';
import PropTypes from 'prop-types';
import { Route, Redirect } from 'react-router-dom';

/* eslint-disable react/jsx-props-no-spreading */
function PrivateRoute({
  component: Component,
  isAuthenticated,
  componentProps,
  ...rest
}) {
  return (
    <Route
      {...rest}
      render={(props) =>
        isAuthenticated ? (
          <Component {...props} {...componentProps} />
        ) : (
          <Redirect
            to={{ pathname: '/login', state: { from: props.location } }} // eslint-disable-line react/prop-types
          />
        )
      }
    />
  );
}

PrivateRoute.propTypes = {
  component: PropTypes.oneOfType([PropTypes.func, PropTypes.object]).isRequired,
  componentProps: PropTypes.instanceOf(Object),
  isAuthenticated: PropTypes.bool,
};

PrivateRoute.defaultProps = {
  componentProps: {},
  isAuthenticated: false,
};

export default PrivateRoute;

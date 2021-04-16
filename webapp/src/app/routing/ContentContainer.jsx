import React from 'react';

import { Switch } from 'react-router-dom';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Toolbar from '@material-ui/core/Toolbar';

import APP_PAGES, { APP_DRAWER_ITEM_TYPES } from '../../utils/app-pages';
import DefaultLoginRoute from './DefaultLoginRoute';
import ExternalLoginRoute from './ExternalLoginRoute';
import GlobalStateContainer from '../store';
import PrivateRoute from './PrivateRoute';

function ContentContainer(props) {
  const { oauthEnabled } = GlobalStateContainer.useContainer();
  const { additionalPages, className, isAuthenticated } = props;
  const routes = [...APP_PAGES, ...additionalPages].filter(
    (item) => item.TYPE === APP_DRAWER_ITEM_TYPES.link
  ).map((item) => {
    const ConfiguredLoginRoute = oauthEnabled
      ? ExternalLoginRoute
      : DefaultLoginRoute;
    const RouteElement = item.REQUIRE_LOGIN
      ? PrivateRoute
      : ConfiguredLoginRoute;

      return (
        <RouteElement
          key={item.NAME}
          path={item.PATH}
          exact
          component={item.COMPONENT}
          isAuthenticated={isAuthenticated}
          componentProps={item.PROPS}
        />
      );
    });

  return (
    <div className={`${className} root`}>
      {/* Adding toolbar makes the drawer "clip" below the web app's top bar as the Toolbar has the same height */}
      <Toolbar />
      <Switch>{routes}</Switch>
    </div>
  );
}

ContentContainer.propTypes = {
  additionalPages: PropTypes.instanceOf(Array),
  className: PropTypes.string,
  isAuthenticated: PropTypes.bool.isRequired,
};

ContentContainer.defaultProps = {
  additionalPages: [],
  className: '',
};

const StyledContentContainer = styled(ContentContainer)`
  &.root {
    position: relative;
    width: 100%;
  }
`;

export default StyledContentContainer;

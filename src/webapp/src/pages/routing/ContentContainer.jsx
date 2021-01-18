import React from 'react';
import PropTypes from 'prop-types';
import { Switch } from 'react-router-dom';
import styled from 'styled-components';
import Toolbar from '@material-ui/core/Toolbar';
import { PAGES, APP_DRAWER_ITEM_TYPES } from '../../utils/config';
import PrivateRoute from './PrivateRoute';
import LoginRoute from './LoginRoute';

function ContentContainer(props) {
  const { className } = props;
  const routes = PAGES.filter(
    (item) => item.TYPE === APP_DRAWER_ITEM_TYPES.link
  ).map((item) => {
    const RouteElement = item.REQUIRE_LOGIN ? PrivateRoute : LoginRoute;

    return (
      <RouteElement
        key={item.NAME}
        path={item.PATH}
        exact
        component={item.COMPONENT}
        isAuthenticated
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
  className: PropTypes.string,
};

ContentContainer.defaultProps = {
  className: '',
};

const StyledContentContainer = styled(ContentContainer)`
  &.root {
    position: relative;
    width: 100%;
    padding: 24px;
  }
`;

export default StyledContentContainer;

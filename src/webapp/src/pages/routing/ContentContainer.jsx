import React from 'react';
import { Switch } from 'react-router-dom';

import { PAGES, APP_DRAWER_ITEM_TYPES } from '../../utils/config';
import PrivateRoute from './PrivateRoute';
import LoginRoute from './LoginRoute';

function ContentContainer() {
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
      />
    );
  });

  console.log(routes);

  return <Switch>{routes}</Switch>;
}

export default ContentContainer;

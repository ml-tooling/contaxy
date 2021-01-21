/* eslint-disable import/prefer-default-export */

import Projects from '../pages/Projects';
import Datasets from '../pages/Datasets';
import Services from '../pages/Services';
import Jobs from '../pages/Jobs';
import Login from '../pages/Login';

export const APP_NAME = 'Machine Learning Lab';

export const DOCUMENTATION_URL = '';
export const API_EXPLORER_URL = '';

export const ENDPOINT =
  process.env.REACT_APP_LAB_ENDPOINT === undefined
    ? (
        document.location.origin.toString() +
        document.location.pathname.toString()
      ).replace('/app/', '/api/')
    : process.env.REACT_APP_LAB_ENDPOINT;

export const ENDPOINTS = {
  research: {
    name: 'research-workspace',
    url: `${ENDPOINT}workspace`,
  },
  userWorkspace: {
    name: 'user-workspace',
    url: `${ENDPOINT}workspace/id/{user}`,
  },
  serviceAdmin: {
    name: 'service-admin',
    url: `${ENDPOINT}service-admin`,
  },
  monitoringDashboard: {
    name: 'monitoring-dashboard',
    url: `${ENDPOINT}netdata`,
  },
  documentation: {
    name: 'documentation',
    url: `${ENDPOINT}docs/`,
  },
  apiExplorer: {
    name: 'api-explorer',
    url: `${ENDPOINT}api-docs/`,
  },
};

// export const APP_DRAWER_ITEMS = [

// ];

export const APP_DRAWER_ITEM_TYPES = {
  divider: 'divider',
  link: 'link',
};

/**
 * The icons are from https://material.io/tools/icons/?style=baseline and embeded via material-ui/icons.
 */
export const PAGES = [
  {
    ICON: 'home',
    NAME: 'Home',
    PATH: '/',
    REQUIRE_LOGIN: true,
    APP_DRAWER_ITEM: true,
    NEW_TAB_OPTION: false,
    PROJECT_SPECIFIC: false,
    TYPE: APP_DRAWER_ITEM_TYPES.link,
    COMPONENT: Projects,
  },
  {
    NAME: 'project-specific-divider',
    APP_DRAWER_ITEM: true,
    TYPE: APP_DRAWER_ITEM_TYPES.divider,
  },
  {
    ICON: 'folder',
    NAME: 'Datasets',
    PATH: '/datasets',
    REQUIRE_LOGIN: true,
    APP_DRAWER_ITEM: true,
    PROJECT_SPECIFIC: false,
    TYPE: APP_DRAWER_ITEM_TYPES.link,
    COMPONENT: Datasets,
  },
  {
    ICON: 'apps',
    NAME: 'Services',
    PATH: '/services',
    REQUIRE_LOGIN: true,
    APP_DRAWER_ITEM: true,
    PROJECT_SPECIFIC: false,
    TYPE: APP_DRAWER_ITEM_TYPES.link,
    COMPONENT: Services,
  },
  {
    ICON: 'next_week',
    NAME: 'Jobs',
    PATH: '/jobs',
    REQUIRE_LOGIN: true,
    APP_DRAWER_ITEM: true,
    PROJECT_SPECIFIC: false,
    TYPE: APP_DRAWER_ITEM_TYPES.link,
    COMPONENT: Jobs,
  },
  {
    NAME: 'login',
    PATH: '/login',
    REQUIRE_LOGIN: false,
    APP_DRAWER_ITEM: false,
    PROJECT_SPECIFIC: false,
    TYPE: APP_DRAWER_ITEM_TYPES.link,
    COMPONENT: Login,
  },
];

/* eslint-disable import/prefer-default-export */

export const APP_NAME = 'Machine Learning Lab';

export const DOCUMENTATION_URL = '';

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

/**
 * The icons are from https://material.io/tools/icons/?style=baseline and embeded via material-ui/icons.
 */
export const APP_DRAWER_ITEMS = [
  {
    ICON: 'home',
    NAME: 'Home',
    PATH: '/',
    NEW_TAB_OPTION: false,
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
  {
    ICON: 'code',
    NAME: 'Workspace',
    PATH: '/workspace',
    NEW_TAB_OPTION: false,
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
  {
    ICON: 'developer_board',
    NAME: 'Admin',
    PATH: '/management',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
    REQUIRE_ADMIN: true,
  },
  {
    ICON: 'settings_applications',
    NAME: 'Service Admin',
    PATH: '/admin',
    NEW_TAB_LINK: ENDPOINTS.serviceAdmin.url,
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
    REQUIRE_ADMIN: true,
  },
  {
    TYPE: 'divider',
    NAME: 'project-specific-divider',
  },
  {
    ICON: 'folder',
    NAME: 'Datasets',
    PATH: '/datasets',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
  {
    ICON: 'equalizer',
    NAME: 'Experiments',
    PATH: '/experiments',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: true,
    TYPE: 'link',
  },
  {
    ICON: 'layers',
    NAME: 'Models',
    PATH: '/models',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
  {
    ICON: 'apps',
    NAME: 'Services',
    PATH: '/services',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
  {
    ICON: 'next_week',
    NAME: 'Jobs',
    PATH: '/jobs',
    NEW_TAB_LINK: '',
    PROJECT_SPECIFIC: false,
    TYPE: 'link',
  },
];

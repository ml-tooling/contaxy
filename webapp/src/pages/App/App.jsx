import React, { useEffect, useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';
import { authApi } from '../../services/contaxy-api';
import AppBar from '../../components/AppBar/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';
import ContentContainer from '../../app/routing/ContentContainer';
import GlobalStateContainer from '../../app/store';

function App() {
  // const { t } = useTranslation();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const {
    isAuthenticated,
    loadProjects,
    setIsAuthenticated,
  } = GlobalStateContainer.useContainer();
  const onDrawerClick = () => setDrawerOpen(!isDrawerOpen);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadProjects();
  }, [isAuthenticated, loadProjects]);

  // Check whether the user is logged in currently (the auth cookie - if existing - is sent to the endpoint which returns a 20x code when a valid token exists and an error otherwise)
  useEffect(() => {
    authApi
      .verifyAccess()
      .then(() => {
        setIsAuthenticated(true);
      })
      .catch(() => setIsAuthenticated(false));
  }, [setIsAuthenticated]);

  const appDrawerElement = (
    <AppDrawer isAdmin open={isDrawerOpen} handleDrawerClose={onDrawerClick} />
  );

  return (
    <div className="App">
      <AppBar isAuthenticated={isAuthenticated} onDrawerOpen={onDrawerClick} />
      {isAuthenticated ? appDrawerElement : false}
      <main className="main">
        <ContentContainer isAuthenticated={isAuthenticated} />
      </main>
      <div id="snackbar-container" />
    </div>
  );
}

export default App;

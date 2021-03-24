import React, { useEffect, useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';

import AppBar from '../../components/AppBar/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';
import ContentContainer from '../../app/routing/ContentContainer';
import GlobalStateContainer from '../../app/store';
import showStandardSnackbar from '../../app/showStandardSnackbar';

import { projectsApi } from '../../services/contaxy-api';

function App() {
  // const { t } = useTranslation();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const { isAuthenticated, setProjects } = GlobalStateContainer.useContainer();
  const onDrawerClick = () => setDrawerOpen(!isDrawerOpen);

  useEffect(() => {
    if (!isAuthenticated) return;
    projectsApi
      .listProjects()
      .then((result) => setProjects(result))
      .catch((err) => showStandardSnackbar(JSON.stringify(err.response.body)));
  }, [isAuthenticated, setProjects]);

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

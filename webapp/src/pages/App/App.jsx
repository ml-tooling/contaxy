import React, { useEffect, useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';
import { usersApi } from '../../services/contaxy-api';
import AppBar from '../../components/AppBar/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';
import ContentContainer from '../../app/routing/ContentContainer';
import GlobalStateContainer from '../../app/store';

function App() {
  // const { t } = useTranslation();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const { loadProjects, setUser, user } = GlobalStateContainer.useContainer();
  const onDrawerClick = () => setDrawerOpen(!isDrawerOpen);

  useEffect(() => {
    if (!user) return;
    loadProjects();
  }, [user, loadProjects]);

  // Check whether the user is logged in currently (the auth cookie - if existing - is sent to the endpoint which returns a user object when a valid token exists and an error otherwise)
  useEffect(() => {
    usersApi
      .getMyUser()
      .then((res) => {
        setUser(res);
      })
      .catch(() => setUser(null));
  }, [setUser]);

  const appDrawerElement = (
    <AppDrawer isAdmin open={isDrawerOpen} handleDrawerClose={onDrawerClick} />
  );

  return (
    <div className="App">
      <AppBar isAuthenticated={Boolean(user)} onDrawerOpen={onDrawerClick} />
      {user ? appDrawerElement : false}
      <main className="main">
        <ContentContainer isAuthenticated={Boolean(user)} />
      </main>
      <div id="snackbar-container" />
    </div>
  );
}

export default App;

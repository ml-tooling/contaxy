import React, { useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';

import AppBar from '../../components/AppBar/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';
import ContentContainer from '../../app/routing/ContentContainer';
import GlobalStateContainer from '../../app/store';

function App() {
  // const { t } = useTranslation();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const { isAuthenticated } = GlobalStateContainer.useContainer();
  const onDrawerClick = () => setDrawerOpen(!isDrawerOpen);

  return (
    <div className="App">
      <AppBar isAuthenticated={isAuthenticated} onDrawerOpen={onDrawerClick} />
      <AppDrawer
        isAdmin
        open={isDrawerOpen}
        handleDrawerClose={onDrawerClick}
      />
      <main className="main">
        <ContentContainer />
      </main>
      <div id="app-dialog" />
    </div>
  );
}

export default App;

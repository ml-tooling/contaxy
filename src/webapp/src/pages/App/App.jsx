import React, { useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';

import AppBar from '../../components/AppBar/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';
import ContentContainer from '../routing/ContentContainer';

function App() {
  // const { t } = useTranslation();
  const [isDrawerOpen, setDrawerOpen] = useState(false);

  const onDrawerClick = () => setDrawerOpen(!isDrawerOpen);

  // TODO: remove hardcoded isAuthenticated
  return (
    <div className="App">
      <AppBar isAuthenticated onDrawerOpen={onDrawerClick} />
      <AppDrawer
        isAdmin
        open={isDrawerOpen}
        handleDrawerClose={onDrawerClick}
      />
      <main>
        <ContentContainer />
      </main>
    </div>
  );
}

export default App;

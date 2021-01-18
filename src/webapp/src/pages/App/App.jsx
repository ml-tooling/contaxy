import React, { useState } from 'react';

// import { useTranslation } from 'react-i18next';

import './App.css';

import AppBar from '../../components/AppBar';
import AppDrawer from '../../components/AppDrawer/AppDrawer';

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
    </div>
  );
}

export default App;

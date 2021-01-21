import React, { useState } from 'react';
import AppDialog from '../components/AppDialog';

const useAppDialog = () => {
  const [isOpen, setIsOpen] = useState(false);

  const show = () => setIsOpen(true);
  const hide = () => setIsOpen(false);

  const RenderAppDialog = (
    { children } // eslint-disable-line react/prop-types
  ) => <>{isOpen && <AppDialog onClose={hide}>{children}</AppDialog>}</>;

  return {
    show,
    hide,
    RenderAppDialog,
  };
};

export default useAppDialog;

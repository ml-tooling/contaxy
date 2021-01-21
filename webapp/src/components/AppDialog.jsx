import React from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';

const AppDialog = React.memo(({ children }) => {
  const domEl = document.getElementById('app-dialog');

  if (!domEl) return null;

  // This is where the magic happens -> our modal div will be rendered into our 'modal-root' div, no matter where we
  // use this component inside our React tree
  return ReactDOM.createPortal(<div>{children}</div>, domEl);
});

AppDialog.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.instanceOf(Object),
    PropTypes.arrayOf(Object),
  ]).isRequired,
};

export default AppDialog;

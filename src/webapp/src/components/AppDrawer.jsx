import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Drawer from '@material-ui/core/Drawer';
import Toolbar from '@material-ui/core/Toolbar';

const DRAWER_WIDTH = 230;

function AppDrawer(props) {
  const { className, open } = props;
  const linkItem = 'foo';

  return (
    <Drawer
      variant="permanent"
      open={open}
      classes={{ paper: `${className} drawer ${!open ? 'drawerClose' : ''}` }}
    >
      {/* Adding toolbar makes the drawer "clip" below the web app's top bar as the Toolbar has the same height */}
      <Toolbar />
      <div>{linkItem}</div>
    </Drawer>
  );
}

AppDrawer.propTypes = {
  className: PropTypes.string,
  open: PropTypes.bool,
};

AppDrawer.defaultProps = {
  className: '',
  open: false,
};

const StyledAppDrawer = styled(AppDrawer)`
  ${({ theme }) => `
    &.drawer {
        position: relative;
        height: 100%;
        min-height: 100vh;
        width: ${DRAWER_WIDTH}px;
        transition: ${theme.transitions.create('width', {
          teasing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        })}
    }

    &.drawerClose {
        overflow-X: hidden;
        transition: ${theme.transitions.create('width', {
          teasing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        })};
        width: ${theme.spacing(7)}px;
        ${[theme.breakpoints.up('sm')]}: {
            width: ${theme.spacing(9)}px;
        }
    }
    `}
`;

export default StyledAppDrawer;

import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import AccountCircle from '@material-ui/icons/AccountCircle';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import IconButton from '@material-ui/core/IconButton';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import { DOCUMENTATION_URL } from '../../utils/config';
import setClipboardText from '../../utils/clipboard';

const ID_MENU_APPBAR = 'menu-appbar';
const REL = 'noopener noreferrer';

function UserMenu(props) {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState();
  const textFieldRef = useRef();
  const [DialogElement, setDialogElement] = useState();

  const { className } = props;

  const handleClose = () => setAnchorEl(null);
  const handleMenuClick = (event) => setAnchorEl(event.currentTarget);

  const handleCopyClick = () => {
    setClipboardText(null, textFieldRef.current);
  };

  const handleApiTokenClick = () => {
    // TODO: fetch API token and set the value
    const element = (
      <Dialog open>
        <DialogTitle>API TOKEN</DialogTitle>
        <DialogContent>
          <DialogContentText ref={textFieldRef}>FOOBAR</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCopyClick()} color="primary">
            COPY
          </Button>
          <Button onClick={() => setDialogElement(null)} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>
    );
    setDialogElement(element);
  };

  return (
    <div className={`${className} container`}>
      <IconButton
        aria-owns={ID_MENU_APPBAR}
        className={`${className} iconButton`}
        onClick={handleMenuClick}
      >
        <AccountCircle />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        id={ID_MENU_APPBAR}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem
          className={`${className} menuItem`}
          href={DOCUMENTATION_URL}
          rel={REL}
          target="_blank"
        >
          {t('documentation')}
        </MenuItem>
        <MenuItem onClick={handleApiTokenClick}>{t('Get API token')}</MenuItem>
      </Menu>

      {false || DialogElement}
    </div>
  );
}

UserMenu.propTypes = {
  className: PropTypes.string,
};

UserMenu.defaultProps = {
  className: '',
};

const StyledUserMenu = styled(UserMenu)`
  &.container {
    margin-right: 12px;
  }

  &.iconButton {
    color: inherit;
  }

  &.user {
    display: inline-block;
    color: white;
  }

  &.menuItem {
    color: initial;
    text-decoration: none;
  }
`;

export default StyledUserMenu;

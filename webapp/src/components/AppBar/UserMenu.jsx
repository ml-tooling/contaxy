import React, { useState } from 'react';

import { useTranslation } from 'react-i18next';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AccountCircle from '@material-ui/icons/AccountCircle';
import IconButton from '@material-ui/core/IconButton';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import { API_EXPLORER_URL, DOCUMENTATION_URL } from '../../utils/config';
import { authApi, fetchAPIToken } from '../../services/contaxy-api';
import { useShowAppDialog } from '../../app/AppDialogServiceProvider';
import ApiTokenDialog from '../Dialogs/ApiTokenDialog';

const ID_MENU_APPBAR = 'menu-appbar';
const REL = 'noopener noreferrer';

function UserMenu(props) {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState();
  const showAppDialog = useShowAppDialog();
  const { className, isAuthenticated, user } = props;

  const onClose = () => setAnchorEl(null);
  const onMenuClick = (event) => setAnchorEl(event.currentTarget);

  const onApiTokenClick = async () => {
    // TODO: pass correct resource for which the API Token should be generated
    const fetchedToken = await fetchAPIToken(user);
    showAppDialog(ApiTokenDialog, { token: JSON.stringify(fetchedToken) });
  };

  const onLogoutClick = async () => {
    try {
      await authApi.logoutUserSession();
    } catch (err) {
      // ignore
    }
    window.location.reload();
  };

  const privateElements = (
    <div>
      <MenuItem onClick={onApiTokenClick}>{t('Get API token')}</MenuItem>
      <MenuItem onClick={onLogoutClick}>{t('Logout')}</MenuItem>
    </div>
  );

  return (
    <div className={`${className} container`}>
      <IconButton
        aria-label="usermenu"
        aria-owns={ID_MENU_APPBAR}
        className={`${className} iconButton`}
        onClick={onMenuClick}
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
        onClose={onClose}
      >
        <MenuItem
          className={`${className} menuItem`}
          component="a"
          href={DOCUMENTATION_URL}
          rel={REL}
          target="_blank"
        >
          {t('documentation')}
        </MenuItem>
        <MenuItem
          className={`${className} menuItem`}
          component="a"
          href={API_EXPLORER_URL}
          rel={REL}
          target="_blank"
        >
          {t('api_explorer')}
        </MenuItem>
        {isAuthenticated ? privateElements : false}
      </Menu>
    </div>
  );
}

UserMenu.propTypes = {
  className: PropTypes.string,
  isAuthenticated: PropTypes.bool,
  user: PropTypes.instanceOf(Object),
};

UserMenu.defaultProps = {
  className: '',
  isAuthenticated: false,
  user: {},
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

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import AccountCircle from '@material-ui/icons/AccountCircle';
import IconButton from '@material-ui/core/IconButton';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import { API_EXPLORER_URL, DOCUMENTATION_URL } from '../../utils/config';
import { fetchAPIToken } from '../../services/lab-api';
import { useShowAppDialog } from '../../app/AppDialogServiceProvider';
import ApiTokenDialog from '../Dialogs/ApiTokenDialog';

const ID_MENU_APPBAR = 'menu-appbar';
const REL = 'noopener noreferrer';

function UserMenu(props) {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState();
  const { className, user } = props;
  const showAppDialog = useShowAppDialog();

  const handleClose = () => setAnchorEl(null);
  const handleMenuClick = (event) => setAnchorEl(event.currentTarget);

  const handleApiTokenClick = async () => {
    // TODO: pass correct resource for which the API Token should be generated
    const fetchedToken = await fetchAPIToken(user);
    showAppDialog(ApiTokenDialog, { token: JSON.stringify(fetchedToken) });
  };

  return (
    <div className={`${className} container`}>
      <IconButton
        aria-label="usermenu"
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
        <MenuItem
          className={`${className} menuItem`}
          href={API_EXPLORER_URL}
          rel={REL}
          target="_blank"
        >
          {t('api_explorer')}
        </MenuItem>
        <MenuItem onClick={handleApiTokenClick}>{t('Get API token')}</MenuItem>
      </Menu>
    </div>
  );
}

UserMenu.propTypes = {
  className: PropTypes.string,
  user: PropTypes.instanceOf(Object),
};

UserMenu.defaultProps = {
  className: '',
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

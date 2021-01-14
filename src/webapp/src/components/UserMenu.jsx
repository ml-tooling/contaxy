import React, { useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import AccountCircle from '@material-ui/icons/AccountCircle';
import IconButton from '@material-ui/core/IconButton';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { DOCUMENTATION_URL } from '../utils/config';

const ID_MENU_APPBAR = 'menu-appbar';
const REL = 'noopener noreferrer';

function UserMenu(props) {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState();
  // const [isOpen, setOpen] = useState(false);

  const { className } = props;

  const handleClose = useMemo(() => setAnchorEl(null), []);

  return (
    <div className={`${className} container`}>
      <IconButton aria-owns={ID_MENU_APPBAR}>
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
      </Menu>
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

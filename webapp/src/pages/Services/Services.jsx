import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import Button from '@material-ui/core/Button';

import { useShowAppDialog } from '../../app/AppDialogServiceProvider';
import DeployServiceDialog from './DeployServiceDialog';
import ServicesContainer from './ServicesContainer';

function Services(props) {
  const { t } = useTranslation();
  const { className } = props;
  const showAppDialog = useShowAppDialog();

  const onServiceDeploy = () => {
    showAppDialog(DeployServiceDialog);
  };

  return (
    <div className="pages-native-component">
      <Button
        variant="contained"
        color="primary"
        onClick={onServiceDeploy}
        className={`${className} button`}
      >
        {`${t('add')} ${t('service')}`}
      </Button>
      <ServicesContainer />
    </div>
  );
}

Services.propTypes = {
  className: PropTypes.string,
};

Services.defaultProps = {
  className: '',
};

const StyledServices = styled(Services)`
  &.button {
    margin: 8px 0px;
  }
`;

export default StyledServices;

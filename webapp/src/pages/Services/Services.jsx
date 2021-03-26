import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import Button from '@material-ui/core/Button';

import { useShowAppDialog } from '../../app/AppDialogServiceProvider';
import DeployServiceDialog from '../../components/Dialogs/DeployContainerDialog';
import ContentDialog from '../../components/Dialogs/ContentDialog';
import ServicesContainer from './ServicesContainer';
import GlobalStateContainer from '../../app/store';

import { servicesApi } from '../../services/contaxy-api';
import { useServices } from '../../services/api-hooks';
import showStandardSnackbar from '../../app/showStandardSnackbar';

// const getServiceUrl = (service) => {
//   // TODO: return url under which the service is reachable
//   return service;
// };

function Services(props) {
  const { t } = useTranslation();
  const { activeProject } = GlobalStateContainer.useContainer();
  const showAppDialog = useShowAppDialog();
  const [services, reloadServices] = useServices(activeProject.id);
  const { className } = props;

  const onServiceDeploy = () => {
    showAppDialog(DeployServiceDialog, {
      onDeploy: async (
        { containerImage, deploymentName, deploymentParameters },
        onClose
      ) => {
        const serviceInput = {
          container_image: containerImage,
          display_name: deploymentName,
          parameters: deploymentParameters,
        };
        try {
          await servicesApi.deployService(activeProject.id, serviceInput);
          showStandardSnackbar(`Deployed service '${deploymentName}'`);
          onClose();
        } catch (err) {
          showStandardSnackbar(`Could not deploy service '${deploymentName}'.`);
        }
      },
    });
  };

  const onShowServiceMetadata = async (projectId, serviceId) => {
    try {
      const serviceMetadata = await servicesApi.getServiceMetadata(
        projectId,
        serviceId
      );
      showAppDialog(ContentDialog, {
        jsonContent: serviceMetadata,
        title: 'Service Metadata',
      });
    } catch (err) {
      showStandardSnackbar('Could not load service metadata');
    }
  };

  const onShowServiceLogs = async (projectId, serviceId) => {
    try {
      const logs = await servicesApi.getServiceLogs(projectId, serviceId);
      showAppDialog(ContentDialog, { content: logs, title: 'Service Logs' });
    } catch (err) {
      showStandardSnackbar('Could not load service logs');
    }
  };

  const onServiceDelete = async (projectId, serviceId) => {
    try {
      await servicesApi.deleteService(projectId, serviceId);
      showStandardSnackbar(`Deleted service '${serviceId}'`);
      reloadServices();
    } catch (err) {
      showStandardSnackbar(`Could not delete service '${serviceId}'`);
    }
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
      <ServicesContainer
        data={services}
        onReload={reloadServices}
        onServiceDelete={(rowData) =>
          onServiceDelete(activeProject.id, rowData.id)
        }
        onShowServiceLogs={(rowData) =>
          onShowServiceLogs(activeProject.id, rowData.id)
        }
        onShowServiceMetadata={(rowData) =>
          onShowServiceMetadata(activeProject.id, rowData.id)
        }
      />
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

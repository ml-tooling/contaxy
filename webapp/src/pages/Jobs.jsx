import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

import MaterialTable from 'material-table';
import Button from '@material-ui/core/Button';

import Widget from '../components/Widget';
import WidgetsGrid from '../components/WidgetsGrid';

import { useShowAppDialog } from '../app/AppDialogServiceProvider';
import DeployServiceDialog from '../components/Dialogs/DeployContainerDialog';

const PAGE_SIZES = [5, 10, 15, 30, 50, 75, 100];

const COLUMNS = [
  {
    field: 'name',
    title: 'Name',
    numeric: false,
    align: 'left',
  },
  {
    field: 'status',
    title: 'Status',
    numeric: false,
    align: 'left',
  },
  {
    field: 'startedAt',
    title: 'Started At',
    align: 'left',
  },
  {
    field: 'finishedAt',
    title: 'Finished At',
    align: 'left',
  },
];

const onShowDeployCommand = (rowData) => {
  // TODO: return deploy command
  return rowData;
};

const onShowLogs = (rowData) => {
  // TODO: return service logs
  return rowData;
};

const onJobDelete = (rowData) => {
  // TODO: delete job
  return rowData;
};

function Jobs(props) {
  const { t } = useTranslation();
  const { className, data } = props;
  const showAppDialog = useShowAppDialog();

  const onJobDeploy = () => {
    showAppDialog(DeployServiceDialog, { onDeploy: () => {} });
  };

  // TODO: set correct values in Widgets

  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget name="Running" icon="loop" value="2" color="cyan" />
        <Widget name="Succeeded" icon="done" value="2" color="light-green" />
        <Widget name="Failed" icon="done" value="2" color="pink" />
      </WidgetsGrid>
      <Button
        variant="contained"
        color="primary"
        onClick={onJobDeploy}
        className={`${className} button`}
      >
        {`${t('run')} ${t('job')}`}
      </Button>
      <MaterialTable
        title={t('job_plural')}
        columns={COLUMNS}
        data={data}
        options={{
          filtering: true,
          columnsButton: false,
          exportButton: true,
          exportFileName: 'data',
          grouping: false,
          pageSize: 5,
          pageSizeOptions: PAGE_SIZES,
          actionsColumnIndex: -1,
          headerStyle: {
            fontSize: '0.75rem',
            fontWeight: 500,
            fontFamily: 'Roboto',
          },
          rowStyle: {
            fontSize: '0.75rem',
            fontFamily: 'Roboto',
          },
        }}
        localization={{ header: { actions: '' } }} // disable localization header name
        actions={[
          {
            icon: 'code',
            iconProps: { className: `` },
            onClick: (event, rowData) => {
              onShowDeployCommand(rowData);
            },
            tooltip: 'Show deploy command',
          },
          {
            icon: 'assignment',
            iconProps: { className: `` },
            onClick: (event, rowData) => {
              onShowLogs(rowData);
            },
            tooltip: 'Display logs',
          },
          {
            icon: 'delete',
            iconProps: { className: `` },
            onClick: (event, rowData) => {
              onJobDelete(rowData);
            },
            tooltip: 'Delete job',
          },
        ]}
      />
    </div>
  );
}

Jobs.propTypes = {
  className: PropTypes.string,
  data: PropTypes.arrayOf(Object),
};

Jobs.defaultProps = {
  className: '',
  data: [],
};

const StyledJobs = styled(Jobs)`
  &.button {
    margin: 8px 0px;
  }
`;

export default StyledJobs;

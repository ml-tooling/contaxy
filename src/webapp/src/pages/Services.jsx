import React from 'react';
import PropTypes from 'prop-types';
import MaterialTable from 'material-table';
import { useTranslation } from 'react-i18next';

const PAGE_SIZES = [5, 10, 15, 30, 50, 75, 100];

const COLUMNS = [
  {
    field: 'name',
    title: 'Name',
    numeric: false,
    align: 'left',
  },
  {
    field: 'startedAt',
    title: 'Started At',
    align: 'left',
  },
];

const getServiceUrl = (service) => {
  // TODO: return url under which the service is reachable
  return service;
};

const onShowDeployCommand = (rowData) => {
  // TODO: return deploy command
  return rowData;
};

const onShowLogs = (rowData) => {
  // TODO: return service logs
  return rowData;
};

function Services(props) {
  const { t } = useTranslation();
  const { data } = props;

  return (
    <MaterialTable
      title={t('service_plural')}
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
          icon: 'access',
          iconProps: { className: `` },
          onClick: (event, rowData) => {
            window.open(getServiceUrl(rowData), '_blank');
          },
          tooltip: 'Download dataset',
        },
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
      ]}
    />
  );
}

Services.propTypes = {
  data: PropTypes.arrayOf(Object),
};

Services.defaultProps = {
  data: [],
};

export default Services;

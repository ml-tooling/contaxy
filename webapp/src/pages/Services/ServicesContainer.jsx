import React from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';
import MaterialTable from 'material-table';

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

const PAGE_SIZES = [5, 10, 15, 30, 50, 75, 100];

function ServicesContainer(props) {
  const { t } = useTranslation();
  const {
    data,
    onReload,
    onServiceDelete,
    onShowServiceLogs,
    onShowServiceMetadata,
  } = props;

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
          icon: 'autorenew',
          isFreeAction: true,
          onClick: onReload,
          tooltip: t('reload'),
        },
        {
          icon: 'access',
          iconProps: { className: `` },
          onClick: (event, rowData) => {
            // window.open(getServiceUrl(rowData), '_blank');
            console.log(event, rowData);
          },
          tooltip: 'Access service',
        },
        {
          icon: 'code',
          iconProps: { className: `` },
          onClick: (event, rowData) => {
            onShowServiceMetadata(rowData);
          },
          tooltip: 'Show service metadata',
        },
        {
          icon: 'assignment',
          iconProps: { className: `` },
          onClick: (event, rowData) => {
            onShowServiceLogs(rowData);
          },
          tooltip: 'Display logs',
        },
        {
          icon: 'delete',
          iconProps: { className: `` },
          onClick: (event, rowData) => {
            onServiceDelete(rowData);
          },
          tooltip: 'Delete service',
        },
      ]}
    />
  );
}

ServicesContainer.propTypes = {
  data: PropTypes.arrayOf(Object),
  onReload: PropTypes.func,
  onServiceDelete: PropTypes.func,
  onShowServiceLogs: PropTypes.func,
  onShowServiceMetadata: PropTypes.func,
};

ServicesContainer.defaultProps = {
  data: [],
  onReload: () => {},
  onServiceDelete: () => {},
  onShowServiceLogs: () => {},
  onShowServiceMetadata: () => {},
};

export default ServicesContainer;

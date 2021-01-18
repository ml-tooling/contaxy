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
  },
  {
    field: 'modifiedAt',
    title: 'Last modified',
    numeric: false,
    type: 'date',
  },
  {
    field: 'modifiedBy',
    title: 'Modified By',
  },
  {
    field: 'version',
    title: 'Version',
    type: 'numeric',
  },
  {
    field: 'size',
    title: 'Size',
  },
];

function Datasets(props) {
  const { t } = useTranslation();
  const { data } = props;

  const onReload = () => {
    // TODO: reload data
    return data;
  };

  return (
    <MaterialTable
      title="Datasets"
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
      actions={[
        {
          icon: 'autorenew',
          isFreeAction: true,
          onClick: onReload,
          tooltip: t('reload'),
        },
      ]}
    />
  );
}

Datasets.propTypes = {
  data: PropTypes.arrayOf(Object),
};

Datasets.defaultProps = {
  data: [],
};

export default Datasets;

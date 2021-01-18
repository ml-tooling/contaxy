import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import MaterialTable from 'material-table';
import { useTranslation } from 'react-i18next';

import setClipboardText from '../utils/clipboard';

const PAGE_SIZES = [5, 10, 15, 30, 50, 75, 100];

const COLUMNS = [
  {
    field: 'name',
    title: 'Name',
    numeric: false,
    align: 'center',
  },
  {
    field: 'modifiedAt',
    title: 'Last modified',
    numeric: false,
    type: 'date',
    align: 'center',
  },
  {
    field: 'modifiedBy',
    title: 'Modified By',
    align: 'center',
  },
  {
    field: 'version',
    title: 'Version',
    type: 'numeric',
    align: 'center',
  },
  {
    field: 'size',
    title: 'Size',
    align: 'center',
  },
];

const onDatasetDelete = (rowData) => {
  // TODO: add delete logic
  return rowData;
};

const onDatasetDownload = (rowData) => {
  const a = document.createElement('a');
  // TODO: use correct URL
  a.href = `http://localhost:30002/api/projects/ml-lab-demo/files/download?fileKey=datasets%2Fnews-categorized.csv.v1`;
  a.target = '_blank';
  a.download = rowData.name || 'download';
  a.click();
};

function Datasets(props) {
  const { t } = useTranslation();
  const { className, data } = props;

  const onReload = () => {
    // TODO: reload data
    return data;
  };

  return (
    <MaterialTable
      title={t('dataset_plural')}
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
          icon: 'download',
          iconProps: { className: `${className} actionIcon` },
          onClick: (event, rowData) => {
            onDatasetDownload(rowData);
          },
          tooltip: `${t('download')} ${t('dataset')}`,
        },
        {
          icon: 'content_copy',
          iconProps: { className: `${className} actionIcon` },
          onClick: (event, rowData) => {
            setClipboardText(rowData.name);
          },
          tooltip: 'Copy dataset key',
        },
        {
          icon: 'delete',
          iconProps: { className: `${className} actionIcon` },
          onClick: (event, rowData) => {
            onDatasetDelete(rowData);
          },
          tooltip: 'Delete dataset',
        },
      ]}
    />
  );
}

Datasets.propTypes = {
  className: PropTypes.string,
  data: PropTypes.arrayOf(Object),
};

Datasets.defaultProps = {
  className: '',
  data: [
    {
      name: 'Foobar',
      modifiedAt: 'a month ago',
      modifiedBy: 'admin',
      version: 2,
      size: '8.32 mb',
    },
  ],
};

const StyledDatasets = styled(Datasets)`
  &.actionIcon {
    color: rgba(0, 0, 0, 0.54);
  }
`;

export default StyledDatasets;

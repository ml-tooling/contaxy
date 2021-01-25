import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import MaterialTable from 'material-table';
import { useTranslation } from 'react-i18next';

import Widget from '../components/Widget';
import WidgetsGrid from '../components/WidgetsGrid';
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

const onFileDelete = (rowData) => {
  // TODO: add delete logic
  return rowData;
};

const onFileDownload = (rowData) => {
  const a = document.createElement('a');
  // TODO: use correct URL
  a.href = `http://localhost:30002/api/projects/ml-lab-demo/files/download?fileKey=datasets%2Fnews-categorized.csv.v1`;
  a.target = '_blank';
  a.download = rowData.name || 'download';
  a.click();
};

function Files(props) {
  const { t } = useTranslation();
  const { className, data } = props;

  const onReload = () => {
    // TODO: reload data
    return data;
  };

  // TODO: add correct value on Widget components
  const filesPluralLiteral = t('file_plural');
  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget name={filesPluralLiteral} icon="list" value="2" color="pink" />
        <Widget name="Total Size" icon="cloud" value="2" color="cyan" />
        <Widget
          name="Last Modified"
          icon="build"
          value="2"
          color="light-green"
        />
      </WidgetsGrid>
      <MaterialTable
        title={filesPluralLiteral}
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
              onFileDownload(rowData);
            },
            tooltip: `${t('download')} ${t('file')}`,
          },
          {
            icon: 'content_copy',
            iconProps: { className: `${className} actionIcon` },
            onClick: (event, rowData) => {
              setClipboardText(rowData.name);
            },
            tooltip: 'Copy File Key',
          },
          {
            icon: 'delete',
            iconProps: { className: `${className} actionIcon` },
            onClick: (event, rowData) => {
              onFileDelete(rowData);
            },
            tooltip: 'Delete File',
          },
        ]}
      />
    </div>
  );
}

Files.propTypes = {
  className: PropTypes.string,
  data: PropTypes.arrayOf(Object),
};

Files.defaultProps = {
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

const StyledFiles = styled(Files)`
  &.actionIcon {
    color: rgba(0, 0, 0, 0.54);
  }
`;

export default StyledFiles;

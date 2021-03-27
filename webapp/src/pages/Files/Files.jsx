import React, { useEffect, useState } from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';

import {
  filesApi,
  getFileDownloadUrl,
  getFileUploadUrl,
} from '../../services/contaxy-api';
import FilesTable from './FilesTable';
import GlobalStateContainer from '../../app/store';
import UploadFilesDialog from '../../components/Dialogs/UploadFilesDialog';
import Widget from '../../components/Widget';
import WidgetsGrid from '../../components/WidgetsGrid';
import showStandardSnackbar from '../../app/showStandardSnackbar';

const onFileDownload = (projectId, rowData) => {
  const a = document.createElement('a');
  a.href = getFileDownloadUrl(projectId, rowData.key);
  a.target = '_blank';
  a.download = rowData.name || 'download';
  a.click();
};

function Files(props) {
  const { className } = props;
  const [data, setData] = useState([]);
  const { activeProject } = GlobalStateContainer.useContainer();
  const [isUploadFileDialogOpen, setUploadFileDialogOpen] = useState(false);

  const onReload = async (projectId) => {
    if (!projectId) {
      return;
    }

    const files = await filesApi.listFiles(projectId);
    setData(files);
  };

  const onFileDelete = async (projectId, rowData) => {
    try {
      await filesApi.deleteFile(projectId, rowData.key);
      showStandardSnackbar(`Deleted file (${rowData.key})`);
      onReload(activeProject.id);
    } catch (err) {
      showStandardSnackbar(`Error in deleting file (${rowData.key})`);
    }
  };

  useEffect(() => onReload(activeProject.id), [activeProject]);

  // TODO: add correct values to widget
  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget name="Amount" icon="list" value={data.length} color="pink" />
        <Widget name="Total Size" icon="cloud" value="2" color="cyan" />
        <Widget
          name="Last Modified"
          icon="build"
          value="2"
          color="light-green"
        />
      </WidgetsGrid>
      <Button
        variant="contained"
        color="primary"
        onClick={() => setUploadFileDialogOpen(true)}
        className={`${className} button`}
      >
        Upload
      </Button>
      <FilesTable
        data={data}
        onFileDownload={(rowData) => onFileDownload(activeProject.id, rowData)}
        onFileDelete={(rowData) => onFileDelete(activeProject.id, rowData)}
        onReload={() => onReload(activeProject.id)}
      />
      <UploadFilesDialog
        endpoint={getFileUploadUrl(activeProject.id, '')}
        open={isUploadFileDialogOpen}
        onClose={() => setUploadFileDialogOpen(false)}
      />
    </div>
  );
}

Files.propTypes = {
  className: PropTypes.string,
};

Files.defaultProps = {
  className: '',
};

const StyledFiles = styled(Files)`
  &.actionIcon {
    color: rgba(0, 0, 0, 0.54);
  }

  &.button {
    margin: 8px 0px;
  }
`;

export default StyledFiles;

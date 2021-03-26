import React, { useEffect, useState } from 'react';

import styled from 'styled-components';

import { filesApi, getFileDownloadUrl } from '../../services/contaxy-api';
import FilesTable from './FilesTable';
import GlobalStateContainer from '../../app/store';
import Widget from '../../components/Widget';
import WidgetsGrid from '../../components/WidgetsGrid';
import showStandardSnackbar from '../../app/showStandardSnackbar';

const onFileDownload = (projectId, rowData) => {
  const a = document.createElement('a');
  a.href = getFileDownloadUrl(projectId, rowData.id);
  a.target = '_blank';
  a.download = rowData.name || 'download';
  a.click();
};

function Files() {
  const [data, setData] = useState([]);
  const { activeProject } = GlobalStateContainer.useContainer();

  const onReload = async (projectId) => {
    if (!projectId) {
      return;
    }

    const files = await filesApi.listFiles(projectId);
    setData(files);
  };

  const onFileDelete = async (projectId, rowData) => {
    try {
      await filesApi.deleteFile(projectId, rowData.id);
      showStandardSnackbar(`Deleted file (${rowData.id})`);
      onReload(activeProject.id);
    } catch (err) {
      showStandardSnackbar(`Error in deleting file (${rowData.id})`);
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
      <FilesTable
        data={data}
        onFileDownload={(rowData) => onFileDownload(activeProject.id, rowData)}
        onFileDelete={(rowData) => onFileDelete(activeProject.id, rowData)}
        onReload={() => onReload(activeProject.id)}
      />
    </div>
  );
}

const StyledFiles = styled(Files)`
  &.actionIcon {
    color: rgba(0, 0, 0, 0.54);
  }
`;

export default StyledFiles;

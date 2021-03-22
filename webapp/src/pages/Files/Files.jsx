import React, { useEffect, useState } from 'react';
import styled from 'styled-components';

import Widget from '../../components/Widget';
import WidgetsGrid from '../../components/WidgetsGrid';

import GlobalStateContainer from '../../app/store';

import { filesApi, getFileDownloadUrl } from '../../services/lab-api';

import FilesTable from './FilesTable';

const onFileDelete = async (projectId, rowData) => {
  const result = filesApi.deleteFile(projectId, rowData.fileKey);
  return result;
};

const onFileDownload = (projectId, rowData) => {
  const a = document.createElement('a');
  a.href = getFileDownloadUrl(projectId, rowData.fileKey);
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

  useEffect(() => onReload(activeProject.id), [activeProject]);

  return (
    <div className="pages-native-component">
      <WidgetsGrid>
        <Widget name="Amount" icon="list" value="2" color="pink" />
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
        onFileDownload={(rowData) => onFileDownload(activeProject, rowData)}
        onFileDelete={(rowData) => onFileDelete(activeProject, rowData)}
        onReload={onReload}
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

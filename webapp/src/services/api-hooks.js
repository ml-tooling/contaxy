/* eslint-disable import/prefer-default-export */
import { useEffect, useState } from 'react';

import { projectsApi } from './contaxy-api';

export function useProjectMembers(projectId) {
  const [projectMembers, setProjectMembers] = useState([]);

  const reload = async () => {
    const newProjectMembers = await projectsApi.listProjectMembers(projectId);
    setProjectMembers(newProjectMembers);
  };

  useEffect(() => {
    reload();
  });

  return [projectMembers, reload];
}

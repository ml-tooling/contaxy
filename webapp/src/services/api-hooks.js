/* eslint-disable import/prefer-default-export */
import { useEffect, useRef, useState } from 'react';

import { projectsApi } from './contaxy-api';

export function useProjectMembers(projectId) {
  const [projectMembers, setProjectMembers] = useState([]);
  const isCanceled = useRef(false);

  const reload = async () => {
    if (!projectId) return;
    try {
      const newProjectMembers = await projectsApi.listProjectMembers(projectId);
      if (isCanceled.current) return;
      setProjectMembers(newProjectMembers);
    } catch (err) {
      // ignore
    }
  };

  useEffect(() => {
    reload();
    return () => {
      isCanceled.current = true;
    };
  });

  return [projectMembers, reload];
}

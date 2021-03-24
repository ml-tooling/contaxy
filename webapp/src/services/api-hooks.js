/* eslint-disable import/prefer-default-export */
import { useEffect, useState } from 'react';

import { projectsApi } from './contaxy-api';

export function useProjectMembers(projectId) {
  const [projectMembers, setProjectMembers] = useState([]);

  useEffect(() => {
    let isCanceled = false;
    const reload = async () => {
      if (!projectId) return;
      try {
        const newProjectMembers = await projectsApi.listProjectMembers(
          projectId
        );
        if (isCanceled) return;
        setProjectMembers(newProjectMembers);
      } catch (err) {
        // ignore
      }
    };

    reload();
    return () => {
      isCanceled = true;
    };
  }, [projectId]);

  return projectMembers;
}

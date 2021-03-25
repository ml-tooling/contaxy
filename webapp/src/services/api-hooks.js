/* eslint-disable import/prefer-default-export */
import { useCallback, useEffect, useRef, useState } from 'react';

import { projectsApi } from './contaxy-api';

export function useProjectMembers(projectId) {
  const [projectMembers, setProjectMembers] = useState([]);
  const [reloadRequested, setReloadRequested] = useState(new Date().getTime());
  const isCanceled = useRef(false);

  const requestReload = useCallback(() => {
    setReloadRequested(new Date().getTime());
  }, []);

  const memoizedReload = useCallback(async () => {
    if (!projectId) return;
    try {
      const newProjectMembers = await projectsApi.listProjectMembers(projectId);
      if (isCanceled.current) {
        isCanceled.current = false;
        return;
      }
      setProjectMembers(newProjectMembers);
    } catch (err) {
      // ignore
    }
  }, [projectId]);

  useEffect(() => {
    isCanceled.current = false;
    memoizedReload();
    return () => {
      isCanceled.current = true;
    };
  }, [memoizedReload, reloadRequested]);

  return [projectMembers, requestReload];
}

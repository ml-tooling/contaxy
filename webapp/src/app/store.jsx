// import React, { createContext, useReducer } from 'react';
import { useState } from 'react';
import { createContainer } from 'unstated-next';

// const initialState = {};
// const store = createContext(initialState);
// const { Provider } = store;

// const StateProvider = ({ children }) => {
// const [state, dispatch] = useReducer((prevState, action) => {
//   switch (action.type) {
//     case 'action description': {
//       const newState = { foo: 'foo' }; // do something with the action
//       return newState;
//     }
//     default: {
//       throw new Error();
//     }
//   }
// }, initialState);
// return <Provider value={{ state, dispatch }}>{children}</Provider>;
// };

// function useContainer() {
//   let value = React.useContext(store);
//   return value;
// }

// const container = {
//   Provider: <Provider value={{ state, dispatch }}>{children}</Provider>,
//   useContainer:
// };

// export { store, StateProvider };

export const initialState = {
  user: {},
  activeProject: {},
  projects: [
    {
      id: 'foobar',
      name: 'foobar',
      description: '',
      creator: 'admin',
      visibility: 'private',
      createdAt: 1606470094642,
    },
    {
      id: 'ml-lab-demo',
      name: 'ml-lab-demo',
      description: '',
      creator: 'admin',
      visibility: 'private',
      createdAt: 1607439288065,
    },
  ],
  isAuthenticated: true,
};

const useGlobalState = (_initialState) => {
  const state = _initialState || initialState;

  const [user, setUser] = useState(state.user);
  const [activeProject, setActiveProject] = useState(state.activeProject);
  const [projects, setProjects] = useState(state.projects);
  const [isAuthenticated, setIsAuthenticated] = useState(state.isAuthenticated);

  return {
    user,
    setUser,
    activeProject,
    setActiveProject,
    projects,
    setProjects,
    isAuthenticated,
    setIsAuthenticated,
  };
};

export default createContainer(useGlobalState);

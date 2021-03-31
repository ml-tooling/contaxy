import React, { useEffect } from 'react';

import { APP_NAME } from '../../utils/config';
import { fireEvent, render, screen } from '../../utils/test-custom-render';
import APP_PAGES, { APP_DRAWER_ITEM_TYPES } from '../../utils/app-pages';
import App from './App';

import GlobalStateContainer from '../../app/store';

test('tests app name', () => {
  render(<App />);
  const linkElement = screen.getByText(new RegExp(APP_NAME, 'i'));
  expect(linkElement).toBeInTheDocument();
});

test('tests the usermenu and its entries', () => {
  render(<App />);
  expect(screen.queryByText(/documentation/i)).toBeNull();
  fireEvent.click(screen.getByLabelText('usermenu'));
  expect(screen.getByText(/documentation/i)).toBeInTheDocument();
  expect(screen.getByText(/api_explorer/i)).toBeInTheDocument();
  expect(screen.getByText(/get api token/i)).toBeInTheDocument();
});

test('test that all link app drawer link items exist', () => {
  render(<App />);
  APP_PAGES.filter((page) => page.type === APP_DRAWER_ITEM_TYPES.link).forEach(
    (page) => {
      expect(screen.queryAllByText(page.NAME).length > 0);
    }
  );
});

test('add plugin dialog', () => {
  render(<App />);
  const addPluginDialogButton = screen.getByText(/add plugin/i);
  fireEvent.click(addPluginDialogButton);
  const addPluginDialog = screen.getByRole('dialog');
  expect(addPluginDialog).toBeInTheDocument();
  expect(
    addPluginDialog.getElementsByTagName('h2')[0].innerText === /add plugin/i
  );
});

test('tests global state', () => {
  const Component = () => {
    const { projects, setProjects } = GlobalStateContainer.useContainer();

    expect(typeof setProjects).toBe('function');

    useEffect(
      () => setProjects([{ id: 'myFooProject', name: 'My Foo Project' }]),
      [setProjects]
    );
    return (
      <div>
        {projects.map((project) => (
          <div key={project.id}>{project.id}</div>
        ))}
      </div>
    );
  };
  render(<Component />);

  expect(screen.getByText('myFooProject')).toBeInTheDocument();
});

test('tests the project selector and its entries', () => {
  const AppWrapper = () => {
    const { setProjects } = GlobalStateContainer.useContainer();
    useEffect(
      () => setProjects([{ id: 'myFooProject', name: 'My Foo Project' }]),
      [setProjects]
    );

    return <App />;
  };

  render(<AppWrapper />);
  const projectSelector = screen.getByLabelText('projectselector');
  expect(projectSelector).toBeInTheDocument();
  fireEvent.click(projectSelector);
  expect(screen.getByText('My Foo Project')).toBeInTheDocument();
});

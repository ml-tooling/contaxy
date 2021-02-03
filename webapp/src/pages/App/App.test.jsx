import React from 'react';

import App from './App';
import { fireEvent, render, screen } from '../../utils/test-custom-render';
import { APP_NAME } from '../../utils/config';

test('tests app name', () => {
  render(<App />);
  const linkElement = screen.getByText(new RegExp(APP_NAME, 'i'));
  expect(linkElement).toBeInTheDocument();
});

test('tests usermenu', () => {
  render(<App />);
  expect(screen.queryByText(/documentation/i)).toBeNull();
  fireEvent.click(screen.getByLabelText('usermenu'));
  expect(screen.getByText(/documentation/i)).toBeInTheDocument();
  expect(screen.getByText(/api_explorer/i)).toBeInTheDocument();
  expect(screen.getByText(/get api token/i)).toBeInTheDocument();
});

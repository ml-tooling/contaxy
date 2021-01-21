import React from 'react';

import App from './App';
import { render, screen } from '../../utils/test-custom-render';
import { APP_NAME } from '../../utils/config';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(new RegExp(APP_NAME, 'i'));
  expect(linkElement).toBeInTheDocument();
});

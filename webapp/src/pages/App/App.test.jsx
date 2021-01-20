import React from 'react';

import App from './App';
import { render, screen } from '../../utils/test-custom-render';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/machine learning lab/i);
  expect(linkElement).toBeInTheDocument();
});

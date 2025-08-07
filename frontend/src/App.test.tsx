import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

test('renders equity valuation app', () => {
  render(<App />);
  expect(document.body).toBeInTheDocument();
});

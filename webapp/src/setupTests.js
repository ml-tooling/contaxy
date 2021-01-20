// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// add mocks here that are needed for all tests as this file is automatically executed (see https://github.com/facebook/create-react-app/issues/9706)
jest.mock('jdenticon', () => ({
  update: () => 'foo',
}));

import '@testing-library/jest-dom';

const isHappyDomAbortError = (value: unknown): boolean => {
  if (!(value instanceof Error)) return false;
  const name = value.name || '';
  const message = value.message || '';
  return name === 'AbortError' && /operation was aborted/i.test(message);
};

if (typeof window !== 'undefined') {
  window.addEventListener('unhandledrejection', (event) => {
    if (isHappyDomAbortError(event.reason)) {
      event.preventDefault();
    }
  });
}

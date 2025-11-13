// Jest setup file
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn()
};

// Mock do VanillaCalendar globalmente
global.VanillaCalendar = jest.fn().mockImplementation(() => ({
  init: jest.fn(),
  set: jest.fn(),
  update: jest.fn()
}));

// Mock global do fetch
global.fetch = jest.fn();
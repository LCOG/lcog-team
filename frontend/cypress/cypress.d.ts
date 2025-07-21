/// <reference types="cypress" />

// Type definitions for Cypress

// Not currently needed because I don't have any custom commands
declare namespace Cypress {
  interface Chainable<Subject = any> {
    step(description: string, fn: () => void): Chainable<any>;
    loginSuperuser(): Chainable<any>;
    loginEmployeeWithUI(): Chainable<any>;
    loginManagerWithUI(): Chainable<any>;
    loginEmployee(): Chainable<any>;
  }
}

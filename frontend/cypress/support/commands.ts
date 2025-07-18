/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

import { visitUrl } from '../support/helpers'

Cypress.Commands.add('step', (description, fn) => {
  cy.log(`🔄🔄🔄 ${description} 🔄🔄🔄`)
  return fn()
})

Cypress.Commands.add('loginEmployeeWithUI', () => {
  visitUrl('/auth/login')
  cy.get('#username')
    .type(Cypress.env('users').employee.username)
  cy.get('#password')
    .type(Cypress.env('users').employee.password, {log: false})
  cy.contains('Login').click()
});

Cypress.Commands.add('loginManagerWithUI', () => {
  visitUrl('/auth/login')
  cy.get('#username')
    .type(Cypress.env('users').gsmanager.username)
  cy.get('#password')
    .type(Cypress.env('users').gsmanager.password, {log: false})
  cy.contains('Login').click()
});

Cypress.Commands.add('loginEmployee', () => {
  const username = Cypress.env('users').employee.username
  const password = Cypress.env('users').employee.pw

  cy.request('POST', 'http://localhost:8000/api/api-token-auth-password/', {username, password})
    .its('body.token')
    .should('exist')
    .then(token =>
        localStorage.setItem('user-token', `${token}`)
    );
    // TODO: Also need to set Axios default header for subsequent requests?

    // Verify user token was set
    // expect(localStorage.getItem('user-token')).to.eq('dbbe99f7301bf3134d2259e1919d82148a68676d')
});
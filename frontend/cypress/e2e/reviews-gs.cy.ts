import { effect } from 'vue'
import { loginSuperuser, loginUser, visitUrl } from '../support/helpers'

// Cypress clears localstorage between tests, so use this to store data
const LOCAL_STORAGE_MEMORY: { [key: string]: string } = {}

describe('GS employee performance review process', () => {

  it('Creates a review', () => {
    loginSuperuser().then(() => {
      const token = localStorage.getItem('user-token')
      const url = `${ Cypress.env('api_url') }/api/v1/review`
      cy.request({
        method: 'POST',
        url,
        headers: {
          Authorization: `Token ${ token }`,
        },
        body: {
          employee: Cypress.env('users').employee.pk,
          manager: Cypress.env('users').gsmanager.pk,
          period_start_date: '2024-06-30',
          period_end_date: '2025-06-30',
          effective_date: '2024-07-01',
        },
      }).then((resp) => {
        const pk = resp.body.pk
        LOCAL_STORAGE_MEMORY['reviewPK'] = pk
        cy.log(`Created review pk: ${ pk }`)
      })
    })
  })

  it('Deletes the review', () => {
    const pk = LOCAL_STORAGE_MEMORY['reviewPK']
    loginSuperuser().then(() => {
      const token = localStorage.getItem('user-token')
      const url = `${ Cypress.env('api_url') }/api/v1/review/${ pk }`
      if (pk) {
        cy.request({
          method: 'DELETE',
          url,
          headers: {
            Authorization: `Token ${ token }`,
          },
        }).then(() => {
          cy.log(`Deleted review pk: ${ pk }`)
        })
      }
    })
  })

  // it('Submitter logs in, creates a new employee workflow, and submits it', () => {
  //   // Create a new employee workflow
  //   loginUser(Cypress.env('users').gsmanager).then(() => {
  //     visitUrl(Cypress.env('workflows_dashboard_path'))
  //     cy.get('.workflowtable-employee-new .row-add-new').click()
  //     cy.get('.q-dialog .q-btn').contains('Yes, start it').click()
  //     cy.wait(500) // Wait for the new transition form to load
  //     cy.url().then((url) => {
  //       const match = url.match(/wf\/(\d+)\/transition/)
  //       const pk = match ? match[1] : null
  //       if (pk) {
  //         LOCAL_STORAGE_MEMORY['workflowPK'] = pk
  //       }
  //       cy.log(`Created workflow pk: ${ pk }`)
  //       // Enter data into the form
  //       cy.get('input[name="first-name"]').type('Dustin')
  //       cy.get('input[name="last-name"]').type('Albrecht')
  //       // TODO: Try cypress-real-events to focus the email field
  //       cy.get('input[name="email"]').focus()
  //       const titleInput = cy.get('select[name="title"]').siblings('input')
  //       titleInput.type('Case')
  //       cy.wait(500) // Wait for the title to be selected
  //       titleInput.type('{downArrow}{enter}')
  //       const managerInput = cy.get('select[name="manager"]').siblings('input')
  //       managerInput.type('Hiring M')
  //       cy.wait(500) // Wait for the title to be selected
  //       managerInput.type('{downArrow}{enter}')
  //       const officeInput = cy.get('select[name="office-location"]').siblings('input').click()
  //       cy.get('span').contains('Cottage Grove').click()
  //       // Cannot reassign
  //       cy.get('button[name="reassign-button"]').should('have.attr', 'disabled')
  //       cy.get('button[name="reassign-button"]').contains('Status: Not submitted')
  //       // Save the form
  //       cy.get('button[name="save-button"]').click()
  //       // Submit the form
  //       cy.get('button[name="send-fiscal-button"]').click()
  //       cy.get('button[name="send-fiscal-dialog-button"]').click()
  //       cy.get('button[name="reassign-button"]').contains('Assigned to: Fiscal')
  //     })
  //   })
  // })

  // it('Fiscal reassigns back to submitter', () => {
  //   const pk = LOCAL_STORAGE_MEMORY['workflowPK']
  //   loginUser(Cypress.env('users').fiscalemployee).then(() => {
  //     visitUrl(`/wf/${pk}/transition`)
  //     // Can reassign
  //     const reassignButton = cy.get('button[name="reassign-button"]')
  //     reassignButton.should('not.have.attr', 'disabled')
  //     reassignButton.contains('Assigned to: Fiscal')
  //     // Reassign to SDS Hiring Lead
  //     reassignButton.click()
  //     cy.get('button[name="reassign-dialog-assignee-dropdown"]').click()
  //     cy.get('.q-menu > .q-list > .q-item').first().click()
  //     cy.get('textarea[name="reassign-extra-message"]').type('Reassigning to Submitter')
  //     cy.get('button[name="reassign-dialog-button"]').click()
  //     // Now cannot reassign
  //     cy.get('button[name="reassign-button"]').should('have.attr', 'disabled')
  //     cy.get('button[name="reassign-button"]').contains('Assigned to: GS Manager')
  //   })
  // })

  // it ('Submitter sends to fiscal a second time', () => {
  //   const pk = LOCAL_STORAGE_MEMORY['workflowPK']
  //   loginUser(Cypress.env('users').gsmanager).then(() => {
  //     visitUrl(`/wf/${pk}/transition`)
  //     // Cannot reassign
  //     cy.get('button[name="reassign-button"]').should('have.attr', 'disabled')
  //     cy.get('button[name="reassign-button"]').contains('Assigned to: GS Manager')
  //     // Submit the form
  //     cy.get('button[name="send-fiscal-button"]').click()
  //     cy.get('button[name="send-fiscal-dialog-button"]').click()
  //     cy.get('button[name="reassign-button"]').contains('Assigned to: Fiscal')
  //   })
  // })

  // it('Fiscal sends to HR', () => {
  //   const pk = LOCAL_STORAGE_MEMORY['workflowPK']
  //   loginUser(Cypress.env('users').fiscalemployee).then(() => {
  //     visitUrl(`/wf/${pk}/transition`)
  //     // Can reassign
  //     const reassignButton = cy.get('button[name="reassign-button"]')
  //     reassignButton.should('not.have.attr', 'disabled')
  //     reassignButton.contains('Assigned to: Fiscal')
  //     // Submit the form
  //     cy.get('button[name="send-hr-button"]').click()
  //     cy.get('button[name="send-hr-dialog-button"]').click()
  //     cy.get('button[name="reassign-button"]').contains('Assigned to: HR')
  //   })
  // })

  // it('HR sends to STN', () => {
  //   const pk = LOCAL_STORAGE_MEMORY['workflowPK']
  //   loginUser(Cypress.env('users').hremployee).then(() => {
  //     visitUrl(`/wf/${pk}/transition`)
  //     // Can reassign
  //     const reassignButton = cy.get('button[name="reassign-button"]')
  //     reassignButton.should('not.have.attr', 'disabled')
  //     reassignButton.contains('Assigned to: HR')
  //     // Submit the form
  //     cy.get('button[name="send-stn-button"]').click()
  //     cy.get('button[name="send-stn-dialog-button"]').click()
  //     cy.get('button[name="reassign-button"]').contains('Status: Complete')
  //   })
  // })

  // it('Deletes the workflow', () => {
  //   const pk = LOCAL_STORAGE_MEMORY['workflowPK']
  //   loginSuperuser().then(() => {
  //     const token = localStorage.getItem('user-token')
  //     const url = `${ Cypress.env('api_url') }/api/v1/workflowinstance/${ pk }`
  //     if (pk) {
  //       cy.request({
  //         method: 'DELETE',
  //         url,
  //         headers: {
  //           Authorization: `Token ${ token }`,
  //         },
  //       }).then(() => {
  //         cy.log(`Deleted workflow instance pk: ${ pk }`)
  //       })
  //     }
  //   })
  // })
})

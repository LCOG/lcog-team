import { loginSuperuser, loginUser, randomString, visitUrl } from '../support/helpers'

// Cypress clears localstorage between tests, so use this to store data
const LOCAL_STORAGE_MEMORY: { [key: string]: string } = {}

function employeeIDViewAndEdit() {
  const employeeIDSelect = cy.get('select[name="employee-id"]')
  const employeeIDInput = employeeIDSelect.siblings('input')
  employeeIDInput.click()
  cy.get(
    '.q-menu > .q-virtual-scroll__content > .q-item > .q-item__section > ' +
    '.q-item__label'
  ).first().click()
  employeeIDSelect.get('option').first().should('have.value', 'CLSD')
  const employeeNumber = cy.get('input[name="employee-number"]')
  employeeNumber.type('1234')
  employeeNumber.should('have.value', '1234')
  const email = cy.get('input[name="email"]')
  email.click()
  email.invoke('val').should('not.be.empty')
}

function employeeIDViewNotEdit() {
  const employeeIDSelect = cy.get('select[name="employee-id"]')
  employeeIDSelect.siblings('input').should('not.exist')
  const employeeNumber = cy.get('input[name="employee-number"]').should('exist')
  employeeNumber.should('have.attr', 'readonly')
  const email = cy.get('input[name="email"]')
  email.click()
  email.invoke('val').should('be.empty')
}

function salaryViewAndEdit() {
  const salaryRange = cy.get('input[name="salary-range"]').should('exist')
  salaryRange.should('not.have.attr', 'readonly', 'readonly')
  const salaryStep = cy.get('#salary-step input').should('exist')
  salaryStep.click()
  cy.get(
    '.q-menu > .q-virtual-scroll__content > .q-item > .q-item__section > ' +
    '.q-item__label'
  ).first().click()
}

function salaryNotView() {
  cy.get('input[name="salary-range"]').should('not.exist')
  cy.get('#salary-step input').should('not.exist')
}

function managerViewAndEdit() {
  const managerInput = cy.get('select[name="manager"]').siblings('input')
  managerInput.should('not.have.attr', 'readonly', 'readonly')
}

function managerViewNotEdit() {
  const managerInput = cy.get('select[name="manager"]').siblings('input')
  managerInput.should('have.attr', 'readonly', 'readonly')
}

function fiscalViewAndEdit() {
  const fiscalField = cy.get('textarea[name="fiscal-field"]')
  fiscalField.type('123-456-7890 / 30%{enter}555-555-5555 / 70%')
  fiscalField.invoke('val').should('contain', '123-456-7890 / 30%')
}

function fiscalViewNotEdit() {
  const fiscalField = cy.get('textarea[name="fiscal-field"]')
  fiscalField.should('have.attr', 'readonly', 'readonly')
}

function otherFieldsViewAndEdit() {
  const firstName = randomString(10)
  cy.get('input[name="first-name"]').clear().type(firstName)
  cy.get('input[name="first-name"]').should('have.value', firstName)
  const middleInitial = randomString(1)
  cy.get('input[name="middle-initial"]').clear().type(middleInitial)
  cy.get('input[name="middle-initial"]').should('have.value', middleInitial)
  const lastName = randomString(10)
  cy.get('input[name="last-name"]').clear().type(lastName)
  cy.get('input[name="last-name"]').should('have.value', lastName)
  const preferredName = randomString(20)
  cy.get('input[name="preferred-name"]').clear().type(preferredName)
  cy.get('input[name="preferred-name"]').should('have.value', preferredName)
  const titleInput = cy.get('select[name="title"]').siblings('input')
  titleInput.type('Senior Web')
  cy.wait(500) // Wait for the title to be selected
  titleInput.type('{downArrow}{enter}')
  titleInput.should('have.value', 'Senior Web Developer')
  const fte = 2
  cy.get('input[name="fte"]').clear().type(fte.toString())
  cy.get('input[name="fte"]').should('have.value', fte.toString())
  cy.get('#bilingual').click()
  cy.get('#bilingual').should('have.attr', 'aria-checked', 'true')
  cy.get('#second-language').click()
  cy.get('.q-menu > .q-virtual-scroll__content > .q-item').first().click()
  cy.get('#union-affiliation').click()
  cy.get('.q-menu > .q-virtual-scroll__content > .q-item').first().click()
  const unitInput = cy.get('select[name="unit"]').siblings('input')
  unitInput.type('Test')
  cy.get('.q-menu > .q-virtual-scroll__content > .q-item').first().click()
  cy.get('#transition-date .q-date__calendar-item .q-btn').first().click()
  cy.get('#transition-time .q-time__clock-position').first().click()
  cy.get('#transition-time .q-time__clock-position').first().click()
  cy.get('#lwop').click()
  cy.get('#lwop').should('have.attr', 'aria-checked', 'false')
  cy.get('#lwop').click()
  cy.get('#lwop').should('have.attr', 'aria-checked', 'true')
  const lwopDetails = randomString(10)
  cy.get('input[name="lwop-details"]').clear().type(lwopDetails)
  cy.get('input[name="lwop-details"]').should('have.value', lwopDetails)
  cy.get('#preliminary-hire').click()
  cy.get('#preliminary-hire').should('have.attr', 'aria-checked', 'true')
  // TODO: Delete profile (exit only)
  cy.get('select[name="office-location"]').siblings('input').click()
  cy.get('.q-menu > .q-virtual-scroll__content > .q-item').first().click()
  const cubicleNumber = '123'
  cy.get('input[name="cubicle-number"]').clear().type(cubicleNumber)
  cy.get('input[name="cubicle-number"]').should('have.value', cubicleNumber)
  cy.get('#teleworking').click()
  cy.get('#teleworking').should('have.attr', 'aria-checked', 'true')
  cy.get('#computer-new').click()
  cy.get('#computer-new').should('have.attr', 'aria-checked', 'true')
  const computerGL = randomString(10)
  cy.get('input[name="computer-gl"]').clear().type(computerGL)
  cy.get('input[name="computer-gl"]').should('have.value', computerGL)
  cy.get('#computer-repurposed').click()
  cy.get('#computer-repurposed').should('have.attr', 'aria-checked', 'true')
  const computerDescription = randomString(10)
  cy.get('input[name="computer-description"]').clear().type(computerDescription)
  cy.get('input[name="computer-description"]')
    .should('have.value', computerDescription)
  const phoneNumber = '555-555-1234'
  cy.get('input[name="phone-number"]').clear().type(phoneNumber)
  cy.get('input[name="phone-number"]').should('have.value', '(555) 555-1234')
  cy.get('select[name="phone-request"]').siblings('input').click()
  cy.get('.q-menu > .q-virtual-scroll__content > .q-item').eq(3).click()
  const phoneRequestData = 'Machiavelli'
  cy.get('input[name="phone-request-data"]').clear().type(phoneRequestData)
  cy.get('input[name="phone-request-data"]')
    .should('have.value', phoneRequestData)
  const loadCode = '21421'
  cy.get('input[name="load-code"]').clear().type(loadCode)
  cy.get('input[name="load-code"]').should('have.value', loadCode)
  cy.get('#cell-phone-needed').click()
  cy.get('#cell-phone-needed').should('have.attr', 'aria-checked', 'true')
  cy.get('#gas-pin-needed').click()
  cy.get('#gas-pin-needed').should('have.attr', 'aria-checked', 'true')
  cy.get('#business-cards').click()
  cy.get('#business-cards').should('have.attr', 'aria-checked', 'true')
  cy.get('#prox-card-needed').click()
  cy.get('#prox-card-needed').should('have.attr', 'aria-checked', 'true')
  cy.get('button[name="save-button"]').should('exist')
}

function otherFieldsViewNotEdit() {
  cy.get('input[name="first-name"]').should('have.attr', 'readonly')
  cy.get('input[name="middle-initial"]').should('have.attr', 'readonly')
  cy.get('input[name="last-name"]').should('have.attr', 'readonly')
  cy.get('input[name="preferred-name"]').should('have.attr', 'readonly')
  cy.get('select[name="title"]').should('not.exist')
  cy.get('input[name="fte"]').should('have.attr', 'readonly')
  cy.get('#bilingual').click()
  cy.get('#bilingual').should('have.attr', 'aria-checked', 'false')
  cy.get('select[name="second-language"]').should('not.exist')
  cy.get('select[name="union-affiliation"]').should('not.exist')
  cy.get('select[name="unit"]').should('not.exist')
  cy.get('#transition-date').should('have.class', 'q-date--readonly')
  cy.get('#transition-time').should('have.class', 'q-time--readonly')
  cy.get('#lwop').click()
  cy.get('#lwop').should('have.attr', 'aria-checked', 'true')
  cy.get('input[name="lwop-details"]').should('have.attr', 'readonly')
  cy.get('#preliminary-hire').click()
  cy.get('#preliminary-hire').should('have.attr', 'aria-checked', 'false')
  // TODO: Delete profile (exit only)
  cy.get('select[name="office-location"]').should('not.exist')
  cy.get('input[name="cubicle-number"]').should('have.attr', 'readonly')
  cy.get('#teleworking').click()
  cy.get('#teleworking').should('have.attr', 'aria-checked', 'false')
  cy.get('#computer-new').click()
  cy.get('#computer-new').should('have.attr', 'aria-checked', 'false')
  cy.get('#computer-repurposed').click()
  cy.get('#computer-repurposed').should('have.attr', 'aria-checked', 'false')
  cy.get('input[name="computer-gl"]').should('not.exist')
  cy.get('input[name="computer-description"]').should('have.attr', 'readonly')
  cy.get('input[name="phone-number"]').should('have.attr', 'readonly')
  cy.get('select[name="phone-request"]').should('not.exist')
  cy.get('input[name="phone-request-data"]').should('not.exist')
  cy.get('input[name="load-code"]').should('have.attr', 'readonly')
  cy.get('#cell-phone-needed').click()
  cy.get('#cell-phone-needed').should('have.attr', 'aria-checked', 'false')
  // TODO: Delete (exit only)
  // TODO: Reassign to (exit only)
  cy.get('#gas-pin-needed').click()
  cy.get('#gas-pin-needed').should('have.attr', 'aria-checked', 'false')
  cy.get('#business-cards').click()
  cy.get('#business-cards').should('have.attr', 'aria-checked', 'false')
  cy.get('#prox-card-needed').click()
  cy.get('#prox-card-needed').should('have.attr', 'aria-checked', 'false')
  // TODO: Prox card returned (exit only)
  // TODO: Show access emails (exit only)
  // TODO: Access emails (exit only)
  cy.get('textarea[name="special-instructions"]')
    .should('have.attr', 'readonly')
  cy.get('button[name="save-button"]').should('not.exist')
}

function noSubmitButtonsExist() {
  cy.get('button[name="send-sds-button"]').should('not.exist')
  cy.get('button[name="send-fiscal-button"]').should('not.exist')
  cy.get('button[name="send-hr-button"]').should('not.exist')
  cy.get('button[name="send-stn-button"]').should('not.exist')
}

function sendSDSButtonExists() {
  cy.get('button[name="send-sds-button"]').should('exist')
  cy.get('button[name="send-fiscal-button"]').should('not.exist')
  cy.get('button[name="send-hr-button"]').should('not.exist')
  cy.get('button[name="send-stn-button"]').should('not.exist')
}

describe('WF: Transition Form', () => {
it('Fill out new employee form', () => {

  cy.step('Completed and deleted workflows load', () => {
    loginUser(Cypress.env('users').sdsmanager).then(() => {
      visitUrl(Cypress.env('workflows_complete_path'))
      cy.get('.q-table__container').should('exist')
      visitUrl(Cypress.env('workflows_deleted_path'))
      cy.get('.q-table__container').should('exist')
    })
  })

  cy.step('Submitter creates a new employee workflow and submits it', () => {
    // Create a new employee workflow
    loginUser(Cypress.env('users').sdsmanager).then(() => {
      visitUrl(Cypress.env('workflows_dashboard_path'))
      cy.get('.workflowtable-employee-new .row-add-new').click()
      cy.get('.q-dialog .q-btn').contains('Yes, start it').click()
      cy.wait(500) // Wait for the new transition form to load
      cy.url().then((url) => {
        const match = url.match(/wf\/(\d+)\/transition/)
        const pk = match ? match[1] : null
        if (pk) {
          LOCAL_STORAGE_MEMORY['workflowPK'] = pk
        }
        cy.log(`Created workflow pk: ${ pk }`)
        // Enter data into the form
        cy.get('input[name="first-name"]').type('Xavier')
        cy.get('input[name="last-name"]').type('Xanthopoulos')
        // TODO: Try cypress-real-events to focus the email field
        cy.get('input[name="email"]').focus()
        const titleInput = cy.get('select[name="title"]').siblings('input')
        titleInput.type('Case')
        cy.wait(500) // Wait for the title to be selected
        titleInput.type('{downArrow}{enter}')
        managerViewAndEdit()
        const managerInput = cy.get('select[name="manager"]').siblings('input')
        managerInput.type('Hiring M')
        cy.wait(1500) // Wait for the title to be selected
        managerInput.type('{downArrow}{enter}')
        cy.get('#lwop').click()
        // Save the form
        cy.get('button[name="save-button"]').click()
        // Can view but not edit employee ID fields
        employeeIDViewNotEdit()
        // Can view and edit the salary fields
        salaryViewAndEdit()
        // Can view but not edit the fiscal field
        fiscalViewNotEdit()
        // Can view and edit all other fields
        otherFieldsViewAndEdit()
        sendSDSButtonExists()
      })
    })
  })

  cy.step('Another manager can view workflow but not edit some fields', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').gsmanager).then(() => {
      visitUrl(`/wf/${pk}/transition`)
      // Can view but not edit employee ID fields
      employeeIDViewNotEdit()
      // Cannot view the salary fields
      salaryNotView()
      // Can view but not edit the manager field
      managerViewNotEdit()
      // Can view but not edit the fiscal field
      fiscalViewNotEdit()
      // Can view but not edit all other fields
      otherFieldsViewNotEdit()
      noSubmitButtonsExist()
    })
  })

  cy.step('Hiring Manager can view workflow and edit certain fields', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').hiringmanager).then(() => {
      visitUrl(`/wf/${pk}/transition`)
      // Can view but not edit employee ID fields
      employeeIDViewNotEdit()
      // Can view and edit the salary fields
      salaryViewAndEdit()
      // Can view but not edit the manager field
      managerViewNotEdit()
      // Can view but not edit the fiscal field
      fiscalViewNotEdit()
      // Can view and edit all other fields
      otherFieldsViewAndEdit()
      noSubmitButtonsExist()
    })
  })

  cy.step('SDS Hiring Lead can view workflow and edit certain fields', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').sdshiringlead).then(() => {
      visitUrl(`/wf/${pk}/transition`)
      // Can view but not edit employee ID fields
      employeeIDViewNotEdit()
      // Can view and edit the salary fields
      salaryViewAndEdit()
      // Can view but not edit the manager field
      managerViewNotEdit()
      // Can view and edit the fiscal field
      fiscalViewNotEdit()
      // Can view and edit all other fields
      otherFieldsViewAndEdit()
      noSubmitButtonsExist()
    })
  })

  cy.step('Fiscal can view the workflow and edit certain fields', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').fiscalemployee).then(() => {
      visitUrl(`/wf/${pk}/transition`)
      // Can view but not edit employee ID fields
      employeeIDViewNotEdit()
      // Can view and edit the salary fields
      salaryViewAndEdit()
      // Can view but not edit the manager field
      managerViewNotEdit()
      // Can view and edit the fiscal field
      fiscalViewAndEdit()
      // Can view and edit all other fields
      otherFieldsViewAndEdit()
      noSubmitButtonsExist()
    })
  })

  cy.step('HR can view the workflow and edit certain fields', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').hremployee).then(() => {
      visitUrl(`/wf/${pk}/transition`)
      // Can view and edit employee ID fields
      employeeIDViewAndEdit()
      // Can view and edit the salary fields
      salaryViewAndEdit()
      // Can view but not edit the manager field
      managerViewAndEdit()
      // Can view but not edit the fiscal field
      fiscalViewNotEdit()
      // Can view and edit all other fields
      otherFieldsViewAndEdit()
      noSubmitButtonsExist()
    })
  })

  cy.step('Non-qualified users cannot view the workflow', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginUser(Cypress.env('users').employee).then(() => {
      visitUrl(Cypress.env('workflows_dashboard_path')).then(() => {
        cy.location('pathname').should('eq', Cypress.env('dashboard_path'))
      })
      visitUrl(`/wf/${pk}/transition`).then(() => {
        cy.location('pathname').should('eq', Cypress.env('dashboard_path'))
      })
    })
  })

  cy.step('Deletes the workflow', () => {
    const pk = LOCAL_STORAGE_MEMORY['workflowPK']
    loginSuperuser().then(() => {
      const token = localStorage.getItem('user-token')
      const url = `${ Cypress.env('api_url') }/api/v1/workflowinstance/${ pk }`
      if (pk) {
        cy.request({
          method: 'DELETE',
          url,
          headers: {
            Authorization: `Token ${ token }`,
          },
        }).then(() => {
          cy.log(`Deleted workflow instance pk: ${ pk }`)
        })
      }
    })
  })

})
})

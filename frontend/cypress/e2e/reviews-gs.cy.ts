import {
  loginSuperuser, loginUser, randomString, visitUrl
} from '../support/helpers'

// Cypress clears localstorage between tests, so use this to store data
const LOCAL_STORAGE_MEMORY: { [key: string]: string } = {}

describe('PR: Review Process', () => {
it('GS employee performance review process', () => {
    
  cy.step('Create a review', () => {
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
            form_pk: 1,
            period_start_date: '2024-06-30',
            period_end_date: '2025-06-30',
            effective_date: '2025-07-01',
          },
        }).then((resp) => {
          const reviewPK = resp.body.pk
          LOCAL_STORAGE_MEMORY['reviewPK'] = reviewPK
          cy.log(`Created review pk: ${ reviewPK }`)
          submitFeedback()
        })
      })
  })

  function copyLink() {
    // We used cypress-clipboard to copy the link to the clipboard
    // but the latest Chrome version does not allow copying to clipboard
    // from a Cypress test, so we just fake it for now.
    cy.step('Manager logs in and copies the link', () => {
      // Create a new employee workflow
      loginUser(Cypress.env('users').gsmanager).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.get('.feedback-link').first().click()
        // cy.copyFromClipboard().then((text) => {
        //   const feedbackRoute = `/note/new?employee=${Cypress.env('users').employee.pk}`
        //   LOCAL_STORAGE_MEMORY['feedbackRoute'] = feedbackRoute
        //   expect(text).to.eq(`${Cypress.env('base_url')}${feedbackRoute}`);
        //   submitFeedback()
        // })
      })
    })
  }

  function submitFeedback() {
    cy.step('Colleague uses link to submit feedback', () => {
      const feedbackRoute =
        `/note/new?employee=${Cypress.env('users').employee.pk}`
      loginUser(Cypress.env('users').colleague).then(() => {
        visitUrl(feedbackRoute)
        cy.get('.employee-select input')
          .should('have.value', Cypress.env('users').employee.name)
        const feedback = randomString(20)
        LOCAL_STORAGE_MEMORY['feedback'] = feedback
        cy.get('#review-note-editor').type(feedback)
        cy.get("#review-note-create-button").click()
        selfEvaluation()
      })  
    })
  }
  
  function selfEvaluation() {
    cy.step('Employee submits self-evaluation', () => {
      loginUser(Cypress.env('users').employee).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Needs evaluation').siblings().last().find('button').click()
        // Colleague feedback should NOT be present
        cy.contains(LOCAL_STORAGE_MEMORY['feedback']).should('not.exist')
        const selfEvaluation = randomString(20)
        LOCAL_STORAGE_MEMORY['selfEvaluation'] = selfEvaluation
        cy.get('#employee-self-evaluation').type(selfEvaluation)
        cy.get('#save-comments-employee').click()
        managerSubmitAndSign()
      })
    })
  }

  function managerSubmitAndSign() {
    cy.step('Manager submits and signs evaluation', () => {
      loginUser(Cypress.env('users').gsmanager).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Needs evaluation').siblings().last().find('button').first()
          .click()
        cy.get('#step-increase').should('be.visible').should('not.be.disabled')
          .siblings().first().should('be.visible').should('not.be.disabled')
          .click()
        cy.get('#top-step-bonus').siblings().first().click()
        // Self-evaluation should be present
        cy.contains(LOCAL_STORAGE_MEMORY['selfEvaluation'])
        // Colleague feedback should be present
        cy.contains(LOCAL_STORAGE_MEMORY['feedback'])
        cy.get('.factors-radio-box-meets-job-requirements').each(($el) => {
          cy.wrap($el).click()
        })
        const longResponse = randomString(20)
        LOCAL_STORAGE_MEMORY['longResponse'] = longResponse
        cy.get('.long-response-editor').each(($el) => {
          cy.wrap($el).type(longResponse)
        })
        cy.get('#update-button').click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        employeeReviewsAndSigns()
      })
    })
  }
  
  function employeeReviewsAndSigns() {
    cy.step('Employee reviews and signs evaluation', () => {
      const reviewPK = LOCAL_STORAGE_MEMORY['reviewPK']
      loginUser(Cypress.env('users').employee).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Evaluation written and reviewed with employee').siblings()
          .last().find('button').click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        programManagerSigns()
      })
    })
  }

  function programManagerSigns() {
    cy.step('Program manager signs evaluation', () => {
      loginUser(Cypress.env('users').programmanager).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Evaluation written and reviewed with employee').siblings()
          .last().find('button').first().click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        divisionDirectorSigns()
      })
    })
  }

  function divisionDirectorSigns() {
    cy.step('Division Director signs evaluation', () => {
      loginUser(Cypress.env('users').divisiondirector).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Evaluation written and reviewed with employee').siblings()
          .last().find('button').first().click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        hrManagerSigns()
      })
    })
  }

  function hrManagerSigns() {
    cy.step('HR Manager signs evaluation', () => {
      loginUser(Cypress.env('users').hrmanager).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.wait(1000) // Wait for the page to load
        cy.contains('Evaluation approved up to division director').siblings()
          .last().find('button').first().click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        executiveDirectorSigns()
      })
    })
  }

  function executiveDirectorSigns() {
    cy.step('Executive Director signs evaluation', () => {
      loginUser(Cypress.env('users').executivedirector).then(() => {
        visitUrl(Cypress.env('reviews_dashboard_path'))
        cy.contains('Evaluation processed by HR').siblings()
          .last().find('button').first().click()
        cy.contains('Click to Sign').click()
        cy.contains('Your signature has been recorded')
        cy.contains('Return to Dashboard').click()
        cy.url().should('include', Cypress.env('reviews_dashboard_path'))
        // TODO: Check if the review is now in the "Completed" state
        deleteReview()
      })
    })
  }

  function deleteReview() {
    cy.step('Deletes the review', () => {
      const reviewPK = LOCAL_STORAGE_MEMORY['reviewPK']
      loginSuperuser().then(() => {
        const token = localStorage.getItem('user-token')
        const url = `${ Cypress.env('api_url') }/api/v1/review/${ reviewPK }`
        if (reviewPK) {
          cy.request({
            method: 'DELETE',
            url,
            headers: {
              Authorization: `Token ${ token }`,
            },
          }).then(() => {
            cy.log(`Deleted review pk: ${ reviewPK }`)
          })
        }
        // Delete most recently created review note
      })
    })
  }
  
})
})

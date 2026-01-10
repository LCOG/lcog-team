import { RouteRecordRaw } from 'vue-router'
import {
  isDivisionDirector, isExpenseApprover, isExpenseSubmitter, isFiscal
} from './guards'

let routes: RouteRecordRaw[] = []

const maintenanceMode = false

if (maintenanceMode) {
  routes = [
    {
      path: '/:pathMatch(.*)*',
      component: () => import('pages/MaintenancePage.vue'),
    }
  ]
} else {
  routes = [
    {
      path: '/',
      component: () => import('layouts/MainLayout.vue'),
      children: [
        { path: '/', redirect: '/dashboard' },
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('pages/Dashboard.vue')
        },
        {
          path: 'release-notes',
          name: 'release-notes',
          component: () => import('src/pages/ReleaseNotes.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'help',
          name: 'help',
          component: () => import('src/pages/help/HelpBase.vue'),
          children: [
            {
              path: 'phish',
              name: 'help-phish',
              component: () => import('src/pages/help/Phish.vue')
            },
            {
              path: 'workflows',
              name: 'help-workflows',
              component: () => import('src/pages/help/Workflows.vue')
            },
            {
              path: 'cc-expenses',
              name: 'help-cc-expenses',
              component: () => import('src/pages/help/CCExpenses.vue')
            },
          ]
        },

        //////////////
        // EXPENSES //
        //////////////
        {
          path: 'expenses',
          name: 'expenses',
          component: () => import('src/pages/purchases/ExpensesBase.vue'),
          redirect: () => {
            if (isFiscal()) {
              return { name: 'fiscal-approve-expenses' }
            } else if (isDivisionDirector()) {
              return { name: 'director-view-expenses' }
            } else if (isExpenseApprover()) {
              return { name: 'approve-expenses' }
            } else if (isExpenseSubmitter()) {
              return { name: 'submit-expenses' }
            } else {
              return { name: 'dashboard' }
            }
          },
          children: [
            {
              path: 'submit',
              name: 'submit-expenses',
              component: () => import('src/pages/purchases/SubmitExpenses.vue'),
              meta: {
                requiresAuth: true, requiresExpenseSubmitter: true,
                allowMonthNav: true
              },
            },
            {
              path: 'approve',
              name: 'approve-expenses',
              component: () => import('src/pages/purchases/ApproveExpenses.vue'),
              meta: {
                requiresAuth: true, requiresExpenseApprover: true,
                allowMonthNav: true
              },
            },
            {
              path: 'director',
              name: 'director-view-expenses',
              component: () => import('src/pages/purchases/DirectorView.vue'),
              meta: {
                requiresAuth: true, requiresDivisionDirector: true,
                allowMonthNav: true
              },
            },
            {
              path: 'director/:expenseMonthPK',
              name: 'director-view-expenses-detail',
              component: () => {
                return import('src/pages/purchases/DirectorViewDetail.vue')
              },
              meta: {
                requiresAuth: true, requiresDivisionDirector: true,
                allowMonthNav: false
              },
            },
            {
              path: 'fiscal',
              name: 'fiscal-approve-expenses',
              component: () => import('src/pages/purchases/FiscalApprove.vue'),
              meta: {
                requiresAuth: true, requiresFiscal: true, allowMonthNav: true
              },
            },
            {
              path: 'fiscal/:expenseMonthPK',
              name: 'fiscal-approve-expenses-detail',
              component: () => {
                return import('src/pages/purchases/FiscalApproveDetail.vue')
              },
              meta: {
                requiresAuth: true, requiresFiscal: true, allowMonthNav: false
              },
            },
          ]
        },

        //////////////////////
        // SECURITY MESSAGE //
        //////////////////////
        {
          path: '/security-message',
          name: 'security-message',
          component: () => import('pages/SecurityMessage.vue'),
          meta: { requiresAuth: true }
        },

        /////////////
        // PROFILE //
        /////////////
        {
          path: '/profile',
          name: 'my-profile',
          component: () => import('src/pages/MyProfile.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'profile/:pk',
          name: 'profile',
          component: () => import('src/pages/Profile.vue'),
          meta: { requiresAuth: true, requiresManager: true }
        },
        {
          path: 'organization',
          name: 'organization',
          component: () => import('src/pages/Organization.vue'),
          meta: { requiresAuth: true, requiresManager: true }
        },

        /////////////////////////
        // PERFORMANCE REVIEWS //
        /////////////////////////
        {
          path: '/reviews',
          name: 'reviews',
          component: () => import('pages/reviews/ReviewsBase.vue'),
          meta: { requiresAuth: true },
          children: [
            {
              path: '',
              name: 'reviews-dashboard-redirect',
              redirect: { name: 'reviews-dashboard' }
            },
            {
              path: 'dashboard',
              name: 'reviews-dashboard',
              component: () => import('pages/reviews/ReviewsDashboard.vue'),
            },
            {
              path: 'complete',
              name: 'reviews-complete',
              component: () => import('pages/reviews/ReviewsComplete.vue'),
            },
            {
              path: 'admin',
              name: 'reviews-admin',
              component: () => import('pages/reviews/ReviewsAdmin.vue'),
            }
          ]
        },
        {
          path: '/pr/:pk',
          name: 'pr-details',
          component: () => import('src/pages/reviews/ReviewDetail.vue'),
          meta: { requiresAuth: true, },
          // beforeEnter: ifCanViewReview
          children: [
            {
              path: 'self',
              name: 'pr-self-evaluation',
              component: () => import('pages/reviews/SelfEvaluation.vue'),
              meta: { requiresAuth: true },
            }
          ]
        },
        {
          path: '/pr/:pk/self',
          name: 'pr-self-evaluation',
          component: () => import('pages/reviews/SelfEvaluation.vue'),
          meta: { requiresAuth: true },
          // beforeEnter: ifCanViewReview
        },
        {
          path: '/note/new',
          name: 'note-create',
          component: () => import('src/pages/reviews/ReviewNoteCreate.vue'),
          meta: { requiresAuth: true },
          // beforeEnter: ifManager
        },
        {
          path: '/note/:pk',
          name: 'note-details',
          component: () => import('src/pages/reviews/ReviewNoteDetail.vue'),
          meta: { requiresAuth: true },
          // beforeEnter: ifCanViewNote
        },

        //////////////
        // PHISHING //
        //////////////
        {
          path: '/phish',
          name: 'phish',
          component: () => {
            return import('src/pages/phish/PhishBase.vue')
          },
          redirect: {name: 'phish-reports'},
          meta: { requiresAuth: true },
          children: [
            {
              path: 'reports',
              name: 'phish-reports',
              component: () => import('src/pages/phish/PhishReports.vue'),
            },
          ]
        },

        //////////////////////
        // RESPONSIBILITIES //
        //////////////////////
        {
          path: '/responsibilities',
          name: 'responsibilities',
          component: () => {
            return import('src/pages/responsibilities/Responsibilities.vue')
          },
          redirect: {name: 'all-responsibilities'},
          meta: { requiresAuth: true },
          children: [
            {
              path: 'all',
              name: 'all-responsibilities',
              component: () => {
                return import(
                  'src/pages/responsibilities/AllResponsibilities.vue'
                )
              }
            },
            {
              path: 'orphaned',
              name: 'orphaned-responsibilities',
              component: () => {
                return import(
                  'src/pages/responsibilities/OrphanedResponsibilities.vue'
                )
              }
            },
            {
              path: 'tag',
              name: 'tag',
              component: () => import('src/pages/responsibilities/Tags.vue'),
              children: [
                {
                  path: 'all',
                  name: 'all-tags',
                  component: () => {
                    return import('src/pages/responsibilities/AllTags.vue')
                  }
                },
                {
                  path: ':pk',
                  name: 'tagged-responsibilities',
                  component: () => {
                    return import (
                      'src/pages/responsibilities/TaggedResponsibilities.vue'
                    )
                  }
                }
              ]
            },
            {
              path: ':pk',
              name: 'employee-responsibilities',
              component: () => {
                return import(
                  'src/pages/responsibilities/EmployeeResponsibilities.vue'
                )
              },
              children: [
                {
                  path: 'secondary',
                  name: 'employee-secondary-responsibilities',
                  component: () => {
                    return import(
                      'src/pages/responsibilities/EmployeeResponsibilities.vue'
                    )
                  },
                  props: { secondary: true }
                }
              ]
            }
          ]
        },
        //////////////
        // TIME OFF //
        //////////////
        {
          path: '/timeoff',
          name: 'timeoff',
          component: () => import('src/pages/timeoff/TimeOffBase.vue'),
          meta: { requiresAuth: true },
          redirect: {name: 'timeoff-my-requests'},
          children: [
            {
              path: 'calendar',
              name: 'timeoff-calendar',
              component: () => import('src/pages/timeoff/Calendar.vue'),
            },
            {
              path: 'new-request',
              name: 'timeoff-new-request',
              component: () => import('src/pages/timeoff/NewRequest.vue'),
            },
            {
              path: 'my-requests',
              name: 'timeoff-my-requests',
              component: () => import('src/pages/timeoff/MyRequests.vue'),
            },
            {
              path: 'request-detail/:pk',
              name: 'timeoff-request-detail',
              component: () => import('src/pages/timeoff/RequestDetail.vue'),
              meta: { requiresAuth: true, requiresCanViewTimeOffRequest: true }
            },
            {
              path: 'manage-requests',
              name: 'timeoff-manage-requests',
              component: () => import('src/pages/timeoff/ManageRequests.vue'),
            }
          ]
        },

        ///////////////
        // Workflows //
        ///////////////
        {
          path: '/workflows',
          name: 'workflows',
          component: () => import('pages/workflows/WorkflowsBase.vue'),
          meta: { requiresAuth: true },
          children: [
            {
              path: '',
              name: 'workflow-dashboard-redirect',
              redirect: { name: 'workflow-dashboard' }
            },
            {
              path: 'dashboard',
              name: 'workflow-dashboard',
              component: () => import('pages/workflows/WorkflowDashboard.vue')
            },
            {
              path: 'complete',
              name: 'workflows-complete',
              component: () => import('src/pages/workflows/WorkflowsComplete.vue'),
              // TODO: For now we just have one complete page/table
              // children: [
              //   {
              //     path: '',
              //     name: 'workflows-complete-onboarding-redirect',
              //     redirect: { name: 'workflows-complete-onboarding' }
              //   },
              //   {
              //     path: 'onboarding',
              //     name: 'workflows-complete-onboarding',
              //     component: () => {
              //       return import(
              //         'src/pages/workflows/WorkflowsCompleteOnboarding.vue'
              //       )
              //     }
              //   }
              // ]
            },
            {
              path: 'deleted',
              name: 'workflows-archived',
              component: () => import('src/pages/workflows/WorkflowsArchived.vue')
            }
          ]
        },
        {
          path: '/wf/:pk',
          name: 'workflow-instance-detail',
          component: () => {
            return import('src/pages/workflows/WorkflowInstanceDetail.vue')
          },
          meta: { requiresAuth: true },
          children: [
            {
              path: 'processes',
              name: 'workflow-processes',
              component: () => import('src/pages/workflows/WorkflowProcesses.vue')
            },
            {
              path: 'transition',
              name: 'workflow-transition-form',
              component: () => {
                return import('src/pages/workflows/EmployeeTransitionDetail.vue')
              }
            }
          ]
        }
      ],
    },

    //////////////////////
    // DESK RESERVATION //
    //////////////////////
    {
      path: '/desk-reservation',
      component: () => import('src/pages/deskReservation/DeskReservation.vue'),
      children: [
        {
          path: 'schaefers',
          name: 'schaefers',
          component: () => import('src/pages/deskReservation/Schaefers.vue'),
          children: [
            {
              path: '1',
              name: 'schaefers-1',
              component: () => import('src/pages/deskReservation/Schaefers1.vue'),
              children: [
                {
                  path: 'desk/:deskNumber',
                  name: 'schaefers-1-desk',
                  component: () => {
                    return import('src/pages/deskReservation/Schaefers1.vue')
                  }
                }
              ]
            },
            {
              path: '2',
              name: 'schaefers-2',
              component: () => import('src/pages/deskReservation/Schaefers2.vue'),
              children: [
                {
                  path: 'desk/:deskNumber',
                  name: 'schaefers-2-desk',
                  component: () => {
                    return import('src/pages/deskReservation/Schaefers2.vue')
                  }
                }
              ]
            },
            {
              path: '3',
              name: 'schaefers-3',
              component: () => import('src/pages/deskReservation/Schaefers3.vue'),
              children: [
                {
                  path: 'desk/:deskNumber',
                  name: 'schaefers-3-desk',
                  component: () => {
                    return import('src/pages/deskReservation/Schaefers3.vue')
                  }
                }
              ]
            }
          ]
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('src/pages/deskReservation/Reports.vue'),
          meta: { requiresAuth: true, requiresDeskReservationReportsPermission: true }
        }
      ]
    },
    {
      // Shortcut path for CIAO to direct to a specific highlighted desk on the
      // desk reservation map.
      path: '/desk/:deskNumber',
      redirect: to => {
        let name = 'schaefers-1-desk'
        if (to.params.deskNumber[0] == '2') {
          name = 'schaefers-2-desk'
        } else if (to.params.deskNumber[0] == '3') {
          name = 'schaefers-3-desk'
        }
        return { name }
      }
    },

    /////////////////////
    // SCHAEFERS KIOSK //
    /////////////////////
    {
      path: '/kiosk',
      name: 'schaefers-kiosk',
      component: () => import('src/pages/SchaefersKiosk.vue'),
    },

    /////////////////////////
    // MEALS ON WHEELS MAP //
    /////////////////////////
    {
      path: '/mow-map',
      name: 'mow-map',
      component: () => import('src/pages/meals/MOWMap.vue'),
      meta: { requiresAuth: true, requiresMealsOnWheelsPermission: true }
    },

    ////////////////////
    // MARKETING PAGE //
    ////////////////////
    { path: '/about', component: () => import('pages/MarketingPage.vue') },

    ///////////////
    // ZOOM TEST //
    ///////////////
    {
      path: '/zoom',
      name: 'zoom',
      component: () => import('src/pages/ZoomTest.vue'),
    },

    //////////////////
    // PRINT LAYOUT //
    //////////////////
    {
      path: '/print',
      component: () => import('layouts/PrintLayout.vue'),
      children: [
        {
          path: 'pr/:pk',
          name: 'pr-print',
          component: () => import('src/pages/reviews/ReviewDetail.vue'),
          meta: { requiresManager: true },
          props: {
            print: true
          }
        },
        {
          path: 'wf/:pk/transition',
          name: 'workflow-print',
          component: () => {
            return import('src/pages/workflows/EmployeeTransitionDetail.vue')
          },
          meta: { requiresAuth: true },
          props: {
            print: true
          }
        },
        {
          path: 'expenses/fiscal/:expenseMonthPK',
          name: 'expense-month-print',
          component: () => {
            return import('src/pages/purchases/FiscalApproveDetail.vue')
          },
          meta: { requiresAuth: true, requiresFiscal: true },
          props: {
            print: true
          }
        }
      ]
    },

    /////////////////////////
    // USERNAME LOGIN PAGE //
    /////////////////////////
    {
      path: '/auth',
      component: () => import('layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('pages/UsernameLogin.vue'),
          // beforeEnter: ifNotAuthenticated,
        },
      ]
    },

    /////////////////
    // Outage page //
    /////////////////
    {
      path: '/outage',
      name: 'outage-notice',
      component: () => import('src/pages/OutageNotice.vue'),
    },

    ///////////////
    // Test page //
    ///////////////
    {
      path: '/test204kjfmo4oerpkg',
      name: 'test-page',
      component: () => import('src/pages/TestPage.vue'),
    },

    // Always leave this as last one,
    // but you can also remove it
    {
      path: '/:catchAll(.*)*',
      component: () => import('pages/ErrorNotFound.vue'),
    },
  ]
}

export default routes

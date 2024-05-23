import { RouteRecordRaw } from 'vue-router'
import { isExpenseApprover, isExpenseManager, isFiscal } from './guards'

const routes: RouteRecordRaw[] = [
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
        component: () => import('src/pages/ReleaseNotes.vue')
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
            return { name: 'fiscal-approve' }
          } else if (isExpenseApprover()) {
            return { name: 'approve-expenses' }
          } else if (isExpenseManager()) {
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
            meta: { requiresAuth: true, requiresExpenseManager: true },
          },
          {
            path: 'approve',
            name: 'approve-expenses',
            component: () => import('src/pages/purchases/ApproveExpenses.vue'),
            meta: { requiresAuth: true, requiresExpenseApprover: true },
          },
          {
            path: 'fiscal',
            name: 'fiscal-approve',
            component: () => import('src/pages/purchases/FiscalApprove.vue'),
            meta: { requiresAuth: true, requiresFiscal: true },
          },
          {
            path: 'fiscal/:employeePK/:year/:month',
            name: 'fiscal-approve-detail',
            component: () => import('src/pages/purchases/FiscalApproveDetail.vue'),
            meta: { requiresAuth: true, requiresFiscal: true },
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
        component: () => import('pages/performanceReview/PerformanceReviewList.vue'),
        // beforeEnter: ifManager
      },
      {
        path: '/pr/:pk',
        name: 'pr-details',
        component: () => import('pages/performanceReview/PerformanceReviewDetail.vue'),
        // beforeEnter: ifCanViewReview
      },
      {
        path: '/note/new',
        name: 'note-create',
        component: () => import('src/pages/performanceReview/ReviewNoteCreate.vue'),
        // beforeEnter: ifManager
      },
      {
        path: '/note/:pk',
        name: 'note-details',
        component: () => import('src/pages/performanceReview/ReviewNoteDetail.vue'),
        // beforeEnter: ifCanViewNote
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
        component: () => import('pages/workflows/Workflows.vue'),
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
        component: () => import('pages/performanceReview/PerformanceReviewDetail.vue'),
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

export default routes

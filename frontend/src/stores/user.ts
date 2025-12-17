import axios from 'axios'
import { defineStore } from 'pinia'
import { useCookies } from 'vue3-cookies'

import { apiURL, handlePromiseError } from 'src/stores/index'
import { useSecurityMessageStore } from 'src/stores/securitymessage'
import {
  ClientError, EmployeeRetrieve, SimpleEmployeeRetrieve, WorkflowOption
} from 'src/types'

const { cookies } = useCookies()

export const useUserStore = defineStore('user', {
  state: () => ({
    status: '',
    profile: {
      employee_pk: -1,
      username: '',
      email: '',
      name: '',
      division: '',
      is_manager: false,
      has_manager: false,
      is_is_employee: false,
      is_hr_employee: false,
      is_sds_hiring_lead: false,
      is_fiscal_employee: false,
      is_eligible_for_telework_application: false,
      can_view_seating_charts: false,
      can_edit_seating_charts: false,
      is_upper_manager: false,
      is_hr_manager: false,
      is_division_director: false,
      is_executive_director: false,
      viewed_security_message: false,
      prs_can_view: [] as Array<number>,
      notes_can_view: [] as Array<number>,
      telework_applications_can_view: [] as Array<number>,
      time_off_requests_can_view: [] as Array<number>,
      next_to_sign_prs: '',
      workflow_roles: [] as Array<number>,
      workflow_display_options: [] as Array<WorkflowOption>,
      is_all_workflows_admin: false,
      is_expense_submitter: false,
      is_expense_approver: false,
      can_view_phish: false,
      can_view_reviews: false,
      can_view_mow_routes: false,
      can_manage_mow_stops: false
    },
    simpleEmployeeList: [] as Array<SimpleEmployeeRetrieve>,
    simpleEmployeeDetail: { pk: -1, name: '' } as SimpleEmployeeRetrieve,
  }),

  getters: {
    getEmployeeProfile: state => state.profile,
    isProfileLoaded: state => !!state.profile.username,
    isManager: state => state.profile.is_manager,
    isFiscal: state => state.profile.is_fiscal_employee,
    isDivisionDirector: state => state.profile.is_division_director,
    hasWorkflowRoles: state => !!state.profile.workflow_roles.length,
    isExpenseSubmitter: state => state.profile.is_expense_submitter,
    isExpenseApprover: state => state.profile.is_expense_approver,
    canViewPhish: state => state.profile.can_view_phish,
    canViewReviews: state => state.profile.can_view_reviews,
    canViewMOWRoutes: state => state.profile.can_view_mow_routes,
    canManageMOWStops: state => state.profile.can_manage_mow_stops
  },

  actions: {
    // For requesting user on login
    userRequest() {
      return new Promise((resolve, reject) => {
        this.status = 'loading'
        axios({ url: `${ apiURL }api/v1/current-user/` })
          .then((resp: {data: EmployeeRetrieve}) => {
            this.status = 'success'
            this.profile.employee_pk = resp.data.pk
            this.profile.username = resp.data.username
            this.profile.email = resp.data.email
            this.profile.name = resp.data.name
            this.profile.division = resp.data.division
            this.profile.is_manager = resp.data.is_manager
            this.profile.has_manager = resp.data.has_manager
            this.profile.is_is_employee = resp.data.is_is_employee
            this.profile.is_hr_employee = resp.data.is_hr_employee
            this.profile.is_sds_hiring_lead = resp.data.is_sds_hiring_lead
            this.profile.is_fiscal_employee = resp.data.is_fiscal_employee
            this.profile.is_eligible_for_telework_application =
              resp.data.is_eligible_for_telework_application
            this.profile.can_view_seating_charts =
              resp.data.can_view_seating_charts
            this.profile.can_edit_seating_charts =
              resp.data.can_edit_seating_charts
            this.profile.is_upper_manager = resp.data.is_upper_manager
            this.profile.is_hr_manager = resp.data.is_hr_manager
            this.profile.is_division_director = resp.data.is_division_director
            this.profile.is_executive_director = resp.data.is_executive_director
            this.profile.viewed_security_message =
              resp.data.viewed_security_message
            this.profile.prs_can_view = resp.data.prs_can_view
            this.profile.notes_can_view = resp.data.notes_can_view
            this.profile.telework_applications_can_view =
              resp.data.telework_applications_can_view
            this.profile.time_off_requests_can_view =
              resp.data.time_off_requests_can_view
            this.profile.next_to_sign_prs = resp.data.next_to_sign_prs
            this.profile.workflow_roles = resp.data.workflow_roles
            this.profile.workflow_display_options =
              resp.data.workflow_display_options
            this.profile.is_all_workflows_admin =
              resp.data.is_all_workflows_admin
            this.profile.is_expense_submitter = resp.data.is_expense_submitter
            this.profile.is_expense_approver = resp.data.is_expense_approver
            this.profile.can_view_phish = resp.data.can_view_phish
            this.profile.can_view_reviews = resp.data.can_view_reviews
            this.profile.can_view_mow_routes = resp.data.can_view_mow_routes
            this.profile.can_manage_mow_stops = resp.data.can_manage_mow_stops
            cookies.set('division', resp.data.division.toString())
            cookies.set('is_manager', resp.data.is_manager.toString())
            cookies.set('has_manager', resp.data.has_manager.toString())
            cookies.set('is_is_employee', resp.data.is_is_employee.toString())
            cookies.set('is_hr_employee', resp.data.is_hr_employee.toString())
            cookies.set(
              'is_sds_hiring_lead', resp.data.is_sds_hiring_lead.toString()
            )
            cookies.set(
              'is_fiscal_employee', resp.data.is_fiscal_employee.toString()
            )
            cookies.set(
              'is_division_director', resp.data.is_division_director.toString()
            )
            cookies.set(
              'is_eligible_for_telework_application',
              resp.data.is_eligible_for_telework_application.toString()
            )
            cookies.set(
              'can_view_seating_charts',
              resp.data.can_view_seating_charts.toString()
            )
            cookies.set(
              'can_edit_seating_charts',
              resp.data.can_edit_seating_charts.toString()
            )
            cookies.set('prs_can_view', resp.data.prs_can_view.toString())
            cookies.set('notes_can_view', resp.data.notes_can_view.toString())
            cookies.set(
              'telework_applications_can_view',
              resp.data.telework_applications_can_view.toString()
            )
            cookies.set(
              'time_off_requests_can_view',
              resp.data.time_off_requests_can_view.toString()
            )
            cookies.set('workflow_roles', resp.data.workflow_roles.toString())
            cookies.set(
              'workflow_display_options',
              resp.data.workflow_display_options.toString()
            )
            cookies.set(
              'is_expense_submitter', resp.data.is_expense_submitter.toString()
            )
            cookies.set(
              'is_expense_approver', resp.data.is_expense_approver.toString()
            )
            cookies.set(
              'can_view_reviews', resp.data.can_view_reviews.toString()
            )
            cookies.set(
              'can_view_mow_routes', resp.data.can_view_mow_routes.toString()
            )
            cookies.set(
              'can_manage_mow_stops', resp.data.can_manage_mow_stops.toString()
            )

            // TODO: Convert this
            // dispatch(
            //   'performanceReviewModule/getMyNextPR',
            //   {pk: resp.data.pk}, { root: true }
            // )
            //   .catch(err => console.log(err))
            const securityMessageStore = useSecurityMessageStore()
            securityMessageStore.getViewedLatestSecurityMessage()
              .catch(err => console.log(err))
            resolve(resp)
          })
          .catch(e => {
            this.status = 'error'
            // if resp is unauthorized, logout, to
            this.authLogout()
              .catch(err => console.log(err))
            reject(e)
          })
      })
    },
    // For getting just the current user on specific pages
    simpleUserRequest: (): Promise<EmployeeRetrieve> => {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/current-user/` })
          .then(resp => resolve(resp.data))
          .catch(e => handlePromiseError(
            reject, 'Error getting current user', e
          ))
      })
    },
    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        cookies.remove('division')
        cookies.remove('is_manager')
        cookies.remove('has_manager')
        cookies.remove('is_is_employee')
        cookies.remove('is_hr_employee')
        cookies.remove('is_sds_hiring_lead')
        cookies.remove('is_fiscal_employee')
        cookies.remove('is_division_director')
        cookies.remove('is_eligible_for_telework_application')
        cookies.remove('can_view_seating_charts')
        cookies.remove('can_edit_seating_charts')
        cookies.remove('prs_can_view')
        cookies.remove('notes_can_view')
        cookies.remove('telework_applications_can_view')
        cookies.remove('time_off_requests_can_view')
        cookies.remove('workflow_roles')
        cookies.remove('workflow_display_options')
        cookies.remove('is_expense_submitter')
        cookies.remove('is_expense_approver')
        cookies.remove('can_view_reviews')
        cookies.remove('can_view_mow_routes')
        cookies.remove('can_manage_mow_stops')
        resolve('Successfully triggered logout')
      })
    },
    // Log a frontend error in AWS CloudWatch
    // TODO: This doesn't belong here, but I don't have a generic utility store.
    logError(data: ClientError) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/log-error`, data, method: 'POST' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error logging error LOL:', e)
          })
      })
    },

    // TODO: More stuff that doesn't belong here: Zoom test create meetings
    // Authenticate a Zoom user
    // TODO: Unused
    getZoomAuthorizationToken() {
      return new Promise((resolve, reject) => {
        const client_id = import.meta.env.VITE_ZOOM_CLIENT_ID
        const redirect_uri = import.meta.env.VITE_ZOOM_REDIRECT_URI
        axios({
          url:
            'https://zoom.us/oauth/authorize?response_type=code&client_id=' +
            `${ client_id }&redirect_uri=${ redirect_uri }`,
          method: 'GET'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error authenticating Zoom user: requesting user authoriation:',
              e
            )
          })
      })
    },

    // Authenticate a Zoom user
    getZoomAccessToken(authorizationCode: string) {
      return new Promise((resolve, reject) => {
        const client_id = import.meta.env.VITE_ZOOM_CLIENT_ID
        const client_secret = import.meta.env.VITE_ZOOM_CLIENT_SECRET
        const encodedString = btoa(`${ client_id }:${ client_secret }`)
        console.log('encoded:', encodedString)
        axios({
          url: `${ apiURL }api/v1/zoom-access-token/`,
          data: { 'code': authorizationCode },
          method: 'POST',
        })
          .then(resp => resolve(resp.data))
          .catch(e => handlePromiseError(
            reject, 'Error getting Zoom access token', e
          ))



        // axios({
        //   url: 'https://zoom.us/oauth/token',
        //   data: {
        //     grant_type: 'authorization_code',
        //     code: authorizationCode,
        //     redirect_uri: 'https://team-staging.lcog.org/'
        //   },
        //   method: 'POST',
        //   headers: {
        //     'Authorization': `Basic ${ encodedString }`,
        //     'Content-Type': 'application/x-www-form-urlencoded'
        //   }
        // })
        //   .then(resp => {
        //     console.log(resp)
        //     resolve(resp)
        //   })
        // .catch(e => {
        //   handlePromiseError(
        //     reject, 'Error authenticating Zoom user: requesting access token',
        //     e
        //   )
        // })
      })
    },

    // Create a Zoom meeting link
    createZoomMeeting(userId: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `https://api.zoom.us/v2/users/${userId}/meetings`, data: { },
          method: 'POST'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating Zoom meeting link:', e)
          })
      })
    },
  }
})

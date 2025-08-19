import { useCookies } from 'vue3-cookies'
import { RouteLocationNormalized } from 'vue-router'

import http from 'src/http-common'
import { useAuthStore } from 'src/stores/auth'
import { EmployeeRetrieve } from 'src/types'

const { cookies } = useCookies()

export function canViewDeskReservationReports(): Promise<boolean> {
  return http.get('api/v1/current-user/')
    .then((resp: {data: EmployeeRetrieve}) => {
      if (resp.data.can_view_desk_reservation_reports) {
        return true
      } else {
        return false
      }
    })
    .catch(e => {
      console.error('Error getting current user:', e)
      return false
    })
}

export function canViewExpenses() {
  if (
    cookies.get('is_expense_submitter') == 'true' ||
    cookies.get('is_expense_approver') == 'true' ||
    cookies.get('is_fiscal_employee') == 'true'
  ) {
    return true
  } else {
    console.info('User cannot view Expenses. Redirecting to dashboard.')
    return false
  }
}

export function canViewReviews() {
  if (cookies.get('can_view_reviews') == 'true') {
    return true
  } else {
    console.info('User cannot view Reviews. Redirecting to dashboard.')
    return false
  }
}

export function isDivisionDirector() {
  if (cookies.get('is_division_director') == 'true') {
    return true
  } else {
    console.info('User is not a division director. Redirecting to dashboard.')
    return false
  }
}

export function isExpenseSubmitter() {
  if (cookies.get('is_expense_submitter') == 'true') {
    return true
  } else {
    console.info('User is not an expense manager. Redirecting to dashboard.')
    return false
  }
}

export function isExpenseApprover() {
  if (cookies.get('is_expense_approver') == 'true') {
    return true
  } else {
    console.info('User is not an expense approver. Redirecting to dashboard.')
    return false
  }
}

export function canViewMealsOnWheelsRoutes() {
  if (cookies.get('can_view_mow_routes') == 'true') {
    return true
  } else {
    console.info(
      'User cannot view Meals on Wheels routes. Redirecting to dashboard.'
    )
    return false
  }
}

export function canViewTimeOffRequest(to: RouteLocationNormalized) {
  const authStore = useAuthStore()
  const toPk = typeof to.params.pk == 'string' ? to.params.pk : to.params.pk[0]
  if (
    authStore.isAuthenticated && cookies.get('time_off_requests_can_view') &&
    cookies.get('time_off_requests_can_view').indexOf(toPk) != -1
  ) {
    return true
  } else {
    return false
  }
}

export function isFiscal() {
  if (cookies.get('is_fiscal_employee') == 'true') {
    return true
  } else {
    console.info('User is not a fiscal employee. Redirecting to dashboard.')
    return false
  }
}

export function isManager() {
  if (cookies.get('is_manager') == 'true') {
    return true
  } else {
    console.info('User is not a manager. Redirecting to dashboard.')
    return false
  }
}

export function isAuthenticated() {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    return true
  } else {
    console.info(
      'User is not logged in. Redirecting to dashboard.'
    )
    return false
  }
}

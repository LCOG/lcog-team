import { route } from 'quasar/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'

import routes from 'src/router/routes'

import {
  canViewDeskReservationReports, canViewMealsOnWheelsRoutes,
  canViewTimeOffRequest, isAuthenticated, isDivisionDirector, isExpenseApprover,
  isExpenseSubmitter, isFiscal, isHROrDirector, isManager 
} from './guards'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  Router.beforeEach(async (to) => {
    if (to.meta.requiresAuth && !isAuthenticated()) {
      return '/dashboard'
    }
    if (to.meta.requiresDeskReservationReportsPermission) {
      const canViewReports = await canViewDeskReservationReports()
      if (!canViewReports) {
        return '/dashboard'
      }
    }
    if (to.meta.requiresManager && !isManager()) {
      return '/dashboard'
    }
    if (to.meta.requiresFiscal && !isFiscal()) {
      return '/dashboard'
    }
    if (to.meta.requiresDivisionDirector && !isDivisionDirector()) {
      return '/dashboard'
    }
    if (to.meta.requiresExpenseSubmitter && !isExpenseSubmitter()) {
      return '/dashboard'
    }
    if (to.meta.requiresExpenseApprover && !isExpenseApprover()) {
      return '/dashboard'
    }
    if (to.meta.requiresMealsOnWheelsPermission && !canViewMealsOnWheelsRoutes()) {
      return '/dashboard'
    }
    if (to.meta.requiresCanViewTimeOffRequest && !canViewTimeOffRequest(to)) {
      return '/timeoff'
    }
    if (to.meta.requiresHROrDirector && !isHROrDirector()) {
      return '/reviews/dashboard'
    }

  })

  return Router
})

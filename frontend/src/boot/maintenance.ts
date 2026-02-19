import { boot } from 'quasar/wrappers'
import axios, { AxiosError } from 'axios'
import { ref } from 'vue'

// Create a global reactive state for maintenance mode
export const maintenanceEnabled = ref(false)
export const backendUnreachable = ref(false)

const MAINTENANCE_MESSAGE = `The site is currently undergoing maintenance and will be back shortly.

Downtime should only last 10 minutes or so. If the site isn't up after 10 minutes, please contact the help desk at help@lcog-or.gov`

export default boot(async ({ app, router }) => {
  // Try to ping the backend to see if it's up
  try {
    const apiUrl = process.env.API_URL || 'http://localhost:8000/'
    await axios.get(`${apiUrl}health/`, {
      timeout: 5000 // 5 second timeout
    })
    // Backend is up, proceed normally
  } catch (error) {
    // Check if this is a network error (backend completely down)
    // vs an HTTP error (backend up but endpoint failed)
    const isNetworkError = 
      !error.response && 
      (error.code === 'ECONNREFUSED' || 
       error.code === 'ENOTFOUND' ||
       error.code === 'ETIMEDOUT' ||
       error.message?.includes('Network Error'))
    
    if (isNetworkError) {
      // Backend is unreachable - assume maintenance/deployment
      console.warn('Backend unreachable, showing maintenance page')
      backendUnreachable.value = true
      maintenanceEnabled.value = true
      
      // Redirect to maintenance page if not already there
      router.beforeEach((to, from, next) => {
        if (to.path !== '/maintenance') {
          next('/maintenance')
        } else {
          next()
        }
      })
    } else {
      // Some other error (like 404) - backend is up, let the app try to load normally
      console.error('Error checking backend health:', error)
    }
  }
})

export { MAINTENANCE_MESSAGE }

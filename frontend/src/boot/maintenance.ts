import { boot } from 'quasar/wrappers'
import axios, { AxiosError } from 'axios'
import { ref } from 'vue'

// Create a global reactive state for maintenance mode
export const maintenanceEnabled = ref(false)
export const maintenanceMessage = ref('')
export const backendUnreachable = ref(false)

export default boot(async ({ app, router }) => {
  // Check maintenance status before app loads
  try {
    const apiUrl = process.env.API_URL || 'http://localhost:8000/'
    const response = await axios.get(`${apiUrl}api/v1/maintenance-status/`, {
      timeout: 5000 // 5 second timeout
    })
    
    if (response.data.enabled) {
      maintenanceEnabled.value = true
      maintenanceMessage.value = response.data.message
      
      // Redirect to maintenance page if not already there
      router.beforeEach((to, from, next) => {
        if (to.path !== '/maintenance') {
          next('/maintenance')
        } else {
          next()
        }
      })
    }
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
      maintenanceMessage.value = 'The site is currently undergoing maintenance. Please check back in 10-15 minutes.'
      
      router.beforeEach((to, from, next) => {
        if (to.path !== '/maintenance') {
          next('/maintenance')
        } else {
          next()
        }
      })
    } else {
      // Some other error - let the app try to load normally
      console.error('Error checking maintenance status:', error)
    }
  }
})

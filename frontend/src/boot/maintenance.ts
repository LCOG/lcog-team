import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { ref } from 'vue'

// Create a global reactive state for maintenance mode
export const maintenanceEnabled = ref(false)
export const backendUnreachable = ref(false)

const MAINTENANCE_MESSAGE = `The site is currently undergoing maintenance and will be back shortly.

If the site isn't back after 10 minutes, please contact the help desk at <a href="https://lcog-or.gov/help" target="_blank" rel="noopener noreferrer">https://lcog-or.gov/help</a>`

export default boot(async ({ app, router }) => {
  // Try to ping the backend to see if it's up using image ping (avoids CORS)
  try {
    const apiUrl = process.env.API_URL || 'https://api.team.lcog.org/'
    
    // Use image ping to check connectivity - doesn't require CORS
    // This avoids preflight request issues
    await new Promise<void>((resolve, reject) => {
      const img = new Image()
      const timer = setTimeout(() => {
        reject(new Error('Timeout'))
      }, 5000)
      
      img.onload = () => {
        clearTimeout(timer)
        resolve()
      }
      img.onerror = () => {
        clearTimeout(timer)
        reject(new Error('Failed to load'))
      }
      // Point to any static file that exists on the backend
      img.src = `${apiUrl}static/admin/img/icon-yes.svg?t=${Date.now()}`
    })
    // Backend is up, proceed normally
  } catch (error) {
    // Backend is unreachable - assume maintenance/deployment
    console.warn('Backend unreachable, showing maintenance page:', error)
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
  }
})

export { MAINTENANCE_MESSAGE }

<template>
  <q-page class="flex flex-center bg-grey-2">
    <div class="maintenance-container text-center q-pa-xl">
      <q-icon 
        name="construction" 
        size="100px" 
        color="orange-7" 
        class="q-mb-md"
      />
      <h3 class="text-h3 text-weight-bold q-mt-none q-mb-md">
        Site Maintenance
      </h3>
      <div class="text-h6 text-grey-8 q-mb-lg" style="white-space: pre-line;">
        {{ message }}
      </div>
      <q-spinner-dots
        color="primary"
        size="50px"
      />
      <div class="text-caption text-grey-6 q-mt-lg">
        This page will automatically reload when maintenance is complete.
      </div>
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { maintenanceMessage, backendUnreachable } from 'src/boot/maintenance'
import axios from 'axios'

export default defineComponent({
  name: 'MaintenancePage',
  setup() {
    const message = ref(maintenanceMessage.value || 'The site is currently undergoing maintenance. Please check back in 10-15 minutes.')
    let intervalId: number | null = null

    // Check every 30 seconds if maintenance is still active
    const checkMaintenanceStatus = async () => {
      try {
        const apiUrl = process.env.API_URL || 'http://localhost:8000/'
        const response = await axios.get(`${apiUrl}api/v1/maintenance-status/`, {
          timeout: 5000
        })
        
        if (!response.data.enabled) {
          // Maintenance is over, reload the page to get back to normal app
          window.location.href = '/'
        } else {
          // Update message in case it changed
          message.value = response.data.message
        }
      } catch (error) {
        // Backend still down/unreachable - that's expected during maintenance
        // Just log and keep waiting
        if (backendUnreachable.value) {
          console.log('Backend still unreachable, waiting...')
        } else {
          console.error('Error checking maintenance status:', error)
        }
      }
    }

    onMounted(() => {
      // Check status every 30 seconds
      intervalId = window.setInterval(checkMaintenanceStatus, 30000)
    })

    onUnmounted(() => {
      if (intervalId !== null) {
        window.clearInterval(intervalId)
      }
    })

    return {
      message
    }
  }
})
</script>

<style scoped>
.maintenance-container {
  max-width: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>

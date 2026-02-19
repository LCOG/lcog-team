<template>
  <div class="flex flex-center bg-grey-2" style="height: 100vh;">
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
      <div
        class="text-h6 text-grey-8 q-mb-lg"
        style="white-space: pre-line;"
        v-html="message"
      >
      </div>
      <q-spinner-dots
        color="primary"
        size="50px"
      />
      <div class="text-caption text-grey-6 q-mt-lg">
        This page will automatically reload when maintenance is complete.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { MAINTENANCE_MESSAGE } from 'src/boot/maintenance'
import axios from 'axios'

export default defineComponent({
  name: 'MaintenancePage',
  setup() {
    const message = ref(MAINTENANCE_MESSAGE)
    let intervalId: number | null = null

    // Check every 30 seconds if backend is back up
    const checkBackendStatus = async () => {
      try {
        const apiUrl = process.env.API_URL || 'http://localhost:8000/'
        await axios.get(`${apiUrl}health/`, {
          timeout: 5000
        })
        
        // Backend is back up, reload the page to get back to normal app
        window.location.href = '/'
      } catch (error) {
        // Backend still down/unreachable - that's expected during maintenance
        // Just log and keep waiting
        console.log('Backend still unreachable, waiting...')
      }
    }

    onMounted(() => {
      // Check status every 5 seconds
      intervalId = window.setInterval(checkBackendStatus, 5000)
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

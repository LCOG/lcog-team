<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h4">Phishing</div>
      <q-icon
        name="help"
        color="primary"
        size=48px
        class="cursor-pointer"
        @click="router.push({ name: 'help-phish' })"
      />
    </div>
    <div v-if="userHasPhishRoles()">
      <q-btn-toggle
        :model-value="$route.path"
        @update:model-value="router.push($event)"
        spread
        no-caps
        toggle-color="primary"
        class="q-mb-md"
        :options="[
          { label: 'Reports', value: '/phish/admin/reports' },
          { label: 'Team', value: '/phish/admin/team' }
        ]"
      />
      <router-view />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
const userStore = useUserStore()

function userHasPhishRoles() {
  return userStore.getEmployeeProfile.can_view_phish
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasPhishRoles()) {
        router.push({ name: 'dashboard' })
      }
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

</script>

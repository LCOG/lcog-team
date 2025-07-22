<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h4">Performance Reviews</div>
      <q-icon
        name="help"
        color="primary"
        size=48px
        class="cursor-pointer"
        @click="router.push({ name: 'help-reviews' })"
      />
    </div>
    <div v-if="userHasWorkflowRoles()">
      <router-view />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

// import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
// const userStore = useUserStore()

function userHasWorkflowRoles() {
  // return userStore.getEmployeeProfile.workflow_roles.length > 0
  return true
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasWorkflowRoles()) {
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

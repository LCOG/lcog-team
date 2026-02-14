<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h4">Security Dashboard</div>
      <q-icon
        name="help"
        color="primary"
        size=48px
        class="cursor-pointer"
        @click="router.push({ name: 'help-phish' })"
      />
    </div>
    <div class="text-h6 q-mb-md">Your Training Assignments</div>
    <phish-training-assignments-table
      :training-assignments="trainingAssignments()" />
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'
import { usePhishStore } from 'src/stores/phish'
import PhishTrainingAssignmentsTable from
  'src/components/phish/PhishTrainingAssignmentsTable.vue'

const router = useRouter()
const phishStore = usePhishStore()
const userStore = useUserStore()

function userHasPhishRoles() {
  return userStore.getEmployeeProfile.can_view_phish
}

function trainingAssignments() {
  return phishStore.trainingAssignments[userStore.getEmployeeProfile.employee_pk] || []
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasPhishRoles()) {
        router.push({ name: 'dashboard' })
      } else {
        phishStore.getTrainingAssignmentsForEmployee(userStore.getEmployeeProfile.employee_pk)
      }
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

</script>

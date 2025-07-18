<template>
<div class="row">
  <q-btn-group push>
    <q-btn
      name="reviews-incomplete-button"
      push
      color="secondary"
      glossy
      label="Active"
      :to="{ name: 'reviews-dashboard' }"
    />
    <q-btn
      name="reviews-complete-button"
      push
      color="primary"
      glossy
      label="Complete"
      :to="{ name: 'reviews-complete' }"
    />
  </q-btn-group>
</div>

<!-- REVIEWS TO MANAGE -->
<div v-if="isManager()">
  <div class="row items-center q-mb-sm q-mt-md">
    <q-avatar
      icon="assignment_ind"
      color="primary"
      text-color="white"
      font-size="22px"
      class="q-mr-sm"
      size="md"
    />
    <div class="text-h5">Current Reviews</div>
  </div>
    <ReviewTable
      :managerPk="userStore.getEmployeeProfile.employee_pk"
      :incomplete="true"
    />
</div>

<!-- YOUR NEXT REVIEW -->
<div class="q-py-md">
  <div class="row items-center q-mb-md">
    <q-avatar
      icon="assignment_ind"
      color="primary"
      text-color="white"
      font-size="22px"
      class="q-mr-sm"
      size="md"
    />
    <div class="text-h5">Your Next Review</div>
  </div>
  <ReviewTable
    :employeePk="userStore.getEmployeeProfile.employee_pk"
    :incomplete="true"
  />
</div>

<!-- PEER FEEDBACK -->
<div class="q-py-md">
  <div class="row items-center q-mb-md">
    <q-avatar
      icon="insert_chart_outlined"
      color="primary"
      text-color="white"
      font-size="22px"
      class="q-mr-sm"
      size="md"
    />
    <div class="text-h5">Peer Feedback</div>
  </div>
  <ReviewNoteTable />
</div>
</template>

<script setup lang="ts">
import { useUserStore } from 'src/stores/user'
import ReviewTable from 'src/components/ReviewTable.vue'
import ReviewNoteTable from 'src/components/ReviewNoteTable.vue'

const userStore = useUserStore()

function isManager() {
    return userStore.getEmployeeProfile.is_manager ||
      userStore.getEmployeeProfile.is_hr_manager ||
      userStore.getEmployeeProfile.is_executive_director
}

</script>

<template>
<div class="row">
  <q-btn-group push>
    <q-btn
      name="reviews-incomplete-button"
      push
      color="primary"
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
    <q-btn
      name="reviews-admin-button"
      push
      color="secondary"
      glossy
      label="Admin"
      :to="{ name: 'reviews-admin' }"
    />
  </q-btn-group>
</div>

<!-- ALL REVIEWS -->
<div class="row items-center q-mb-sm q-mt-md">
  <q-avatar
    icon="assignment_ind"
    color="primary"
    text-color="white"
    font-size="22px"
    class="q-mr-sm"
    size="md"
  />
  <div class="text-h5">All Complete Reviews</div>
</div>
<ReviewTable
  :managerPk="userStore.getEmployeeProfile.employee_pk"
  :allComplete="true"
/>

<!-- ALL REVIEWS -->
<div class="row items-center q-mb-sm q-mt-md">
  <q-avatar
    icon="assignment_ind"
    color="primary"
    text-color="white"
    font-size="22px"
    class="q-mr-sm"
    size="md"
  />
  <div class="text-h5">All Incomplete Reviews</div>
</div>
<ReviewTable
  :managerPk="userStore.getEmployeeProfile.employee_pk"
  :allIncomplete="true"
/>
</template>

<script setup lang="ts">

import ReviewTable from 'src/components/ReviewTable.vue'
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()

function isManager() {
    return userStore.getEmployeeProfile.is_manager ||
      userStore.getEmployeeProfile.is_hr_manager ||
      userStore.getEmployeeProfile.is_executive_director
}

</script>

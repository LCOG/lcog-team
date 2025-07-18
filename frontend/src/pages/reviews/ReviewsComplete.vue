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
      color="secondary"
      glossy
      label="Complete"
      :to="{ name: 'reviews-complete' }"
    />
  </q-btn-group>
</div>

<!-- REVIEWS MANAGED -->
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
    <div class="text-h5">Complete Reviews</div>
    <!-- <div>Only the 100 most recently completed reviews are shown.</div> -->
  </div>
    <ReviewTable
      :managerPk="userStore.getEmployeeProfile.employee_pk"
      :complete="true"
    />
    <!-- TODO: For now we just have one complete page/table -->
</div>

<!-- YOUR PAST REVIEWS -->
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
    <div class="text-h5">Your Past Reviews</div>
  </div>
  <ReviewTable
    :employeePk="userStore.getEmployeeProfile.employee_pk"
    :complete="true"
  />
</div>
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

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

<!-- ALL COMPLETE REVIEWS -->
<div class="row items-center q-mb-sm q-mt-md">
  <q-avatar
    icon="assignment_ind"
    color="primary"
    text-color="white"
    font-size="22px"
    class="q-mr-sm"
    size="md"
  />
  <div class="text-h5">Recent Complete Reviews</div>
</div>
<ReviewTable :allComplete="true" />

<!-- ALL INCOMPLETE REVIEWS -->
<div class="row items-center q-mb-sm q-mt-md">
  <q-avatar
    icon="assignment_ind"
    color="primary"
    text-color="white"
    font-size="22px"
    class="q-mr-sm"
    size="md"
  />
  <div class="text-h5">Upcoming Incomplete Reviews</div>
</div>
<ReviewTable :allIncomplete="true" />
</template>

<script setup lang="ts">

import ReviewTable from 'src/components/ReviewTable.vue'
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()

</script>

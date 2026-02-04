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

<div v-if="isHR()" class="actions-pane q-mt-md q-pa-md">
  <div class="text-bold q-mb-sm">Actions</div>
  <q-btn
    color="primary"
    label="Prepare Quarterly NRD Notifications"
    v-on:click="prepareNRDNotifications()"
  />
</div>

<div v-if="showNRDDialog">
  <q-dialog v-model="showNRDDialog">
    <q-card>
      <q-card-section>
        <div class="text-h6">Quarterly NRD Notifications</div>
        <div>
          Next Review Date notifications will be sent to supervisors about
          upcoming employee review dates. They should be sent quarterly.
        </div>
        
        <div
          v-if="!NRDDataFetched"
          class="row justify-center items-center q-mt-md"
        >
          <q-spinner-audio size="md" class="q-mr-xs" />
          Fetching data
        </div>
        
        <div v-if="NRDDataFetched" class="q-mt-md">
          <div class="row justify-center text-red text-bold q-mb-xs">
            Notifications will be sent to
            {{ Object.keys(reviewStore.NRDNotificationData).length }} managers
          </div>
          <div class="row justify-center">
            <q-btn color="primary" label="Send Notifications" />
          </div>
          
          <div class="q-mt-md nrd-data">
            <div v-for="manager of reviewStore.NRDNotificationData" :key="manager.pk" class="q-mb-md">
              <div class="text-bold q-mt-sm">
                {{ manager.manager.name }}
              </div>
              <ul>
                <li v-for="review of manager.reviews" :key="review.pk" class="q-mt-xs">
                  {{ review.employee_name }} – {{ readableDateNEW(review.period_end_date) }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" v-on:click="showNRDDialog = false" />
      </q-card-actions>
    </q-card>
  </q-dialog>
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

<style lang="scss">
.actions-pane {
  border: 1px solid black;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.nrd-data {
  max-height: 400px;
  overflow-y: auto;
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  margin-top: 12px;
}
</style>

<script setup lang="ts">

import { ref } from 'vue'
import ReviewTable from 'src/components/ReviewTable.vue'
import { readableDateNEW } from 'src/filters'
import { useReviewStore } from 'src/stores/review'
import { useUserStore } from 'src/stores/user'

const reviewStore = useReviewStore()
const userStore = useUserStore()

const showNRDDialog = ref(false)
const NRDDataFetched = ref(false)

function isHR() {
  return userStore.getEmployeeProfile.is_hr_employee
}

function prepareNRDNotifications() {
  showNRDDialog.value = true
  reviewStore.getNRDNotificationData().then(() => {
    NRDDataFetched.value = true
  })
}

</script>

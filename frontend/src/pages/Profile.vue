<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">{{ peopleStore.fullEmployeeDetail.name }}</div>
    <div class="q-mb-md">
      <div class="text-h5 q-mb-sm">Basic Info</div>
      <div>Legal Name: {{ peopleStore.fullEmployeeDetail.legal_name }}</div>
      <div>Title: {{ peopleStore.fullEmployeeDetail.title }}</div>
    </div>
    <div>
      <div class="q-mb-md">
        <div class="text-h5 q-mb-sm">Direct Reports</div>
        <EmployeeTable :pk=pk() />
      </div>
      <div class="q-mb-md">
        <div class="text-h5 q-mb-sm">Performance Reviews</div>
        <ReviewTable :employeePk="pk()" />
      </div>
      <div class="q-mb-md">
        <div class="text-h5 q-mb-sm">Managed Performance Reviews</div>
        <ReviewTable :managerPk="pk()" :incomplete="true" />
      </div>
    </div>
  </q-page>
</template>

<style scoped lang="scss">

</style>

<script setup lang="ts">
import { onMounted, onUpdated } from 'vue'
import { useRoute } from 'vue-router';

import EmployeeTable from 'src/components/EmployeeTable.vue'
import ReviewTable from 'src/components/ReviewTable.vue'
import { usePeopleStore } from 'src/stores/people'
import { EmployeeRetrieve } from 'src/types'

const peopleStore = usePeopleStore()
const route = useRoute()

function pk(): number {
  if (typeof route.params.pk == 'string') {
    return parseInt(route.params.pk)
  } else {
    return parseInt(route.params.pk[0])
  }
}

function retrieveProfile(): Promise<EmployeeRetrieve> {
  return new Promise((resolve, reject) => {

    peopleStore.getFullEmployeeDetail({pk: pk()})
      .then((employee) => {
        resolve(employee)
      })
      .catch((error) => {
        reject(error)
      })
  })
}

onMounted(() => {
  retrieveProfile()
})

onUpdated(() => {
  retrieveProfile()
})
</script>

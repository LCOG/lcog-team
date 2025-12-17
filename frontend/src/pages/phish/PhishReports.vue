<template>
<q-page class="q-pa-md">
  <div class="text-h4">Phishing Reports</div>
  <div class="q-mt-md">
    <div class="row items-center justify-between q-mb-sm">
      <q-btn label="Mark Selected Complete" color="primary" :disable="selected.length === 0" @click="markSelectedComplete" />
    </div>

    <q-table
      title="Submitted Reports"
      :rows="activeReports"
      :columns="columns"
      row-key="id"
      selection="multiple"
      v-model:selected="selected"
      flat
      dense
    >
    </q-table>

    <div class="q-mt-lg">
      <div class="text-subtitle2 q-mb-sm">Completed Reports</div>
      <q-table
        :rows="completedReports"
        :columns="columns"
        row-key="id"
        flat
        dense
      />
    </div>
  </div>
</q-page>
</template>

<style scoped lang="scss"></style>

<script setup lang="ts">
import { ref } from 'vue'

const columns = [
  { name: 'employee', label: 'Employee Name', field: 'employee', sortable: true },
  { name: 'date', label: 'Date of Submission', field: 'date', sortable: true }
]
const activeReports = ref([
  { id: 1, employee: 'Alice Johnson', date: '2025-12-10' },
  { id: 2, employee: 'Bob Smith', date: '2025-12-11' },
  { id: 3, employee: 'Carla Gomez', date: '2025-12-12' },
  { id: 4, employee: 'Daniel Lee', date: '2025-12-13' },
  { id: 5, employee: 'Evelyn Tran', date: '2025-12-14' }
])

const completedReports = ref([])

const selected = ref([])

function markSelectedComplete() {
  const selectedIds = selected.value.map(s => (typeof s === 'object' ? s.id : s))
  const idSet = new Set(selectedIds)
  const moved = activeReports.value.filter(r => idSet.has(r.id))
  if (moved.length) {
    completedReports.value.push(...moved)
    activeReports.value = activeReports.value.filter(r => !idSet.has(r.id))
    selected.value = []
  }
}

</script>

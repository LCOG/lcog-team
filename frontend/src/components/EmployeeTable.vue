<template>
  <div class="q-py-sm">
    <q-table
      :rows="peopleStore.directReports"
      :columns="columns()"
      :grid="$q.screen.lt.md"
      no-data-label="Nothing to show."
      row-key="name"
      @row-click="navigateToEmployeeDetail"
    />
  </div>
</template>

<style lang="scss">

</style>

<script setup lang="ts">
import { QTable, QTableProps } from 'quasar'
import { onMounted, onUpdated, ref } from 'vue'
import { useRouter } from 'vue-router'

import { EmployeeRetrieve } from 'src/types'
import { usePeopleStore } from 'src/stores/people'

const router = useRouter()
const peopleStore = usePeopleStore()

let lastPk = ref(-1)

const props = defineProps<{
  pk: number,
}>()

function columns(): QTableProps['columns'] {
  return [
    { 
      name: 'name', label: 'Name', field: 'name', align: 'center',
      sortable: true
    },
    {
      name: 'title', label: 'Title', field: 'title', align: 'center',
      sortable: true
    }
  ]
}

function retrieveDirectReports(): void {
  if (props.pk != lastPk.value) {
    lastPk.value = props.pk
    peopleStore.getDirectReports(props.pk)
      .catch(e => {
        console.error('Error retrieving direct reports', e)
      })
  }
}

function navigateToEmployeeDetail(evt: Event, row: EmployeeRetrieve): void {
  router.push({ name: 'profile', params: { pk: row.pk } })
    .catch(e => {
      console.error('Error navigating to employee profile:', e)
    })
}

onUpdated(() => {
  retrieveDirectReports()
})

onMounted(() => {
  retrieveDirectReports()
})

</script>

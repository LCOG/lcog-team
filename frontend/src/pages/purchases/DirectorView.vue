<template>
<div class="q-mt-md">
  <div class="q-mt-md">
    <q-spinner-grid
      v-if="!selectedMonthExpensesLoaded()"
      class="spinner"
      color="primary"
      size="xl"
    />
    <div v-else>
      <q-table
        flat bordered
        :title="purchaseStore.monthDisplay"
        :rows="selectedMonthExpenseMonths()"
        :columns="columns"
        row-key="name"
        binary-state-sort
        :pagination="pagination"
        class="expense-table"
        no-data-label="No expenses entered this month"
      >
        <template v-slot:body="props">
          <q-tr
            :props="props"
            :class="canViewDetail(props.row.status) ? 'cursor-pointer' : ''"
            @click="() => {
              if (canViewDetail(props.row.status)) {
                navigateToDetail(props.row.pk)
              }
            }"
          >
            <q-td key="employee" :props="props">
              {{ props.row.purchaser.name }} - {{  props.row.card?.display }}
            </q-td>
            <q-td key="status" :props="props">
              <q-linear-progress
                size="25px"
                rounded
                :value="progressBarSize(props.row.status)"
                :color="progressBarColor(props.row.status)"
              >
                <div class="absolute-full flex flex-center">
                  <q-badge
                    color="white"
                    :text-color="progressBarColor(props.row.status)"
                    :label="progressBarLabel(props.row.status)"
                  />
                </div>
              </q-linear-progress>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  </div>
</div>
</template>

<style scoped lang="scss"></style>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { handlePromiseError } from 'src/stores'
import { usePurchaseStore } from 'src/stores/purchase';
import { ExpenseMonth } from 'src/types';

const router = useRouter()
const purchaseStore = usePurchaseStore()

const pagination = {
  rowsPerPage: 50
}

const columns = [
  {
    name: 'employee', required: true, label: 'Name', sortable: true,
    align: 'left'
  },
  {
    name: 'status', label: 'Status', field: 'status', sortable: true,
    align: 'center'
  }
]

function viewingThisMonth() {
  return purchaseStore.firstOfSelectedMonth.getTime() ==
    purchaseStore.firstOfThisMonth.getTime()
}

function selectedMonthExpenseMonths() {
  return purchaseStore.directorExpenseMonths[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function selectedMonthExpensesLoaded() {
  return purchaseStore.directorExpenseMonths[purchaseStore.yearInt] &&
    purchaseStore.directorExpenseMonths[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function progressBarSize(status: string) {
  switch (status) {
    case 'draft':
      return 0
    case 'submitted':
    case 'approver_denied':
      return .25
    case 'approver_approved':
      return .5
    case 'fiscal_denied':
      return .75
    case 'fiscal_approved':
      return 1
    default:
      return 0
  }
}

function progressBarLabel(status: string) {
  switch (status) {
    case 'draft':
      return 'Not Submitted'
    case 'submitted':
      return 'Submitted by Employee'
    case 'approver_denied':
      return 'Denied by Manager'
    case 'approver_approved':
      return 'Approved by Manager'
    case 'fiscal_denied':
      return 'Denied by Fiscal'
    case 'fiscal_approved':
      return 'Approved by Fiscal'
    default:
      return 'Unknown'
  }
}

function progressBarColor(status: string) {
  switch (status) {
    case 'draft':
      return 'grey'
    case 'submitted':
      return 'blue'
    case 'approver_denied':
    case 'fiscal_denied':
      return 'red'
    case 'approver_approved':
    case 'fiscal_approved':
      return 'green'
    default:
      return 'grey'
  }
}

function canViewDetail(status: string) {
  return status !== 'draft'
}

function retrieveMonthEMs(year: number, month: number): Promise<void> {
  if (
    purchaseStore.directorExpenseMonths[year] &&
    purchaseStore.directorExpenseMonths[year][month]
  ) {
    return Promise.resolve()
  }
  // Get a month of EMs 
  return new Promise((resolve, reject) => {
    purchaseStore.getDirectorMonthEMs(year, month)
      .then(() => {
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving director EMs', error)
        reject()
      })
  })
}

function navigateToDetail(expenseMonthPK: number) {
  router.push({
    name: 'director-view-expenses-detail',
    params: {
      expenseMonthPK: expenseMonthPK.toString()
    }
  })
  .catch(e => {
    console.error('Error navigating to time off request detail:', e)
  })
}

onMounted(() => {
  // Retrieve this and then last month's EMs to start
  retrieveMonthEMs(purchaseStore.yearInt, purchaseStore.monthInt).then(() => {
    let yearInt = purchaseStore.yearInt
    let lastMonthInt = purchaseStore.monthInt - 1
    if (lastMonthInt < 1) {
      lastMonthInt = 12
      yearInt -= 1
    }
    retrieveMonthEMs(yearInt, lastMonthInt)
  })
})

watch(() => purchaseStore.firstOfSelectedMonth, (newVal) => {
  if (viewingThisMonth()) return // Never do this on pageload
  const year = newVal.getFullYear()
  const month = newVal.getMonth()
  retrieveMonthEMs(year, month + 1)
})

</script>

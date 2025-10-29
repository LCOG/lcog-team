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
      <div class="text-h5 text-center">Submitted Expenses</div>
      <q-table
        flat bordered
        :title="purchaseStore.monthDisplay"
        :rows="selectedMonthExpenseMonths()"
        :columns="columns"
        row-key="name"
        binary-state-sort
        :pagination="pagination"
        class="expense-table q-mt-sm"
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
              {{ props.row.purchaser.name }}
              <span
                v-if="props.row.card"
              > - {{  props.row.card.display }}</span>
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
            <q-td key="date" :props="props">
              {{ dateLabel(props.row) }}
            </q-td>
            <q-td key="approved" :props="props">
              <q-icon
                v-if="expenseMonthFiscalApproved(props.row)"
                color="green"
                name="check_circle"
                size="lg"
              />
              <q-icon
                v-else-if="expenseMonthFiscalDenied(props.row)"
                color="red"
                name="cancel"
                size="lg"
              />
              <q-icon
                v-else
                color="warning"
                name="radio_button_unchecked"
                size="lg"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
      <div class="row items-center justify-center q-mt-sm">
        <div class="text-bold">
          Month is
          <span v-if="purchaseStore.expenseMonthLocked">locked</span>
          <span v-else>
            <span class="text-uppercase">active</span> and available
          </span>
          for submission
        </div>
        <div class="row justify-center q-ml-md">
          <q-btn 
            :label="purchaseStore.expenseMonthLocked ?
              'Unlock Month' : 'Lock Month'"
            :color="purchaseStore.expenseMonthLocked ? 'white' : 'primary'"
            :text-color="purchaseStore.expenseMonthLocked ? 'primary' : 'white'"
            @click="lockMonthDialogVisible = true"
          />
        </div>
      </div>
    </div>
    <div class="q-mt-md">
      <hr />
      <div class="text-h5 text-center">Expense Statements</div>
      <div class="row justify-between q-gutter-md q-mt-none">
        <div class="col">
          <q-spinner-grid
            v-if="!selectedMonthStatementsLoaded()"
            class="spinner"
            color="primary"
            size="xl"
          />
          <div v-else>
            <q-table
              flat bordered dense
              :rows="selectedMonthStatements()"
              :columns="statementCols"
              row-key="name"
              binary-state-sort
              :pagination="pagination"
              class="expense-table"
            >
              <template v-slot:body-cell-card="props">
                <q-td key="card" :props="props">
                  {{ props.row.card.display }}
                </q-td>
              </template>
              <template v-slot:body-cell-allCleared="props">
                <q-td key="card" :props="props">
                  <q-icon
                    v-if="props.row.all_cleared"
                    color="green"
                    name="check_circle"
                    size="lg"
                  />
                  <q-icon
                    v-else
                    color="warning"
                    name="radio_button_unchecked"
                    size="lg"
                  />
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td key="actions" :props="props">
                  <q-btn
                    icon="visibility"  
                    round
                    flat    
                    @click="showStatmentDialog(props.row)"
                  />
                  <q-btn
                    v-if="!purchaseStore.expenseMonthLocked"
                    icon="delete"
                    round
                    flat
                    @click="showDeleteStatementDialog(props.row)"  
                  />
                </q-td>
              </template>
            </q-table>
            <div
              v-if="!purchaseStore.expenseMonthLocked"
              class="row justify-center q-mt-md"
            >
              <q-btn
                :disabled="selectedMonthStatements().length === 0"  
                label="Send notification to card holders"
                color="primary"
                @click="sendNotificationDialogVisible = true"
              ></q-btn>
            </div>  
          </div>
        </div>
        <div class="col">
          <div class="row justify-center q-mb-sm text-h6">
            Upload Statements for {{ purchaseStore.monthDisplay }}
          </div>
          <div class="row justify-center">
            <FileUploader
                :file=selectedFiles
                multiple
                contentTypeAppLabel="purchases"
                contentTypeModel="expensestatement"
                :data="{
                  'year': purchaseStore.yearInt,
                  'month': purchaseStore.monthInt
                }"
                :readOnly=false
                v-on="{
                  'uploaded': (url: string) => {
                    retrieveMonthStatements(
                      purchaseStore.yearInt, purchaseStore.monthInt, true
                    )
                  }
                }"
              />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Send Notification Dialog -->
  <q-dialog v-model="sendNotificationDialogVisible">
    <q-card>
      <q-card-section>
        <div class="row items-center">
          <q-avatar
            icon="send"
            color="primary"
            text-color="white"
          />
          <span class="q-ml-md col">
            Notification will be sent to all card holders. Please do not send
            multiple notifications unless you really need to.
          </span>
        </div>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn
          flat
          label="Yes, send them!"
          color="primary"
          @click="sendNotifications()"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

    <!-- Lock Month Dialog -->
    <q-dialog v-model="lockMonthDialogVisible">
    <q-card>
      <q-card-section>
        <div class="row items-center">
          <q-avatar
            icon="lock"
            color="primary"
            text-color="white"
          />
          <span class="q-ml-md col">
            <span v-if="purchaseStore.expenseMonthLocked" class="text-bold">
              Unlock
            </span>
            <span v-else class="text-bold">Lock</span>
            expenses for
            <span class="text-bold">{{ purchaseStore.monthDisplay }}</span>?
            <span v-if="purchaseStore.expenseMonthLocked">
              Submitters will once again be able to revise and submit new
              expenses.
            </span>
            <span v-else>
              No one will be able to revise or submit new expenses.
            </span>
          </span>
        </div>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn
          flat
          :label="purchaseStore.expenseMonthLocked ? 'Yes, unlock it' :
            'Yes, lock it'"
          color="primary"
          @click="toggleLockCurrentExpenseMonth()"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- Statement Dialog -->
  <q-dialog v-model="statementDialogVisible">
    <q-card>
      <q-card-section>
        <div class="row items-center">
          <q-avatar
            icon="book"
            color="primary"
            text-color="white"
          />
          <span class="q-ml-sm">
            Card Number:
            <span class="text-bold">
              {{ statementDialogStatement.card.display }}
            </span>
          </span>
        </div>
        <q-markup-table class="q-mt-md">
          <thead>
            <tr>
              <th>Date</th>
              <th>Item</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in statementDialogStatement.items" :key="item.pk">
              <td>{{ readableDateNEW(item.date) }}</td>
              <td>{{ item.description }}</td>
              <td>${{ item.amount }}</td>
            </tr>
          </tbody>
        </q-markup-table>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Close" color="primary" v-close-popup />
        <q-btn
          v-if="!purchaseStore.expenseMonthLocked"
          flat
          label="Delete"
          color="primary"
          @click="showDeleteStatementDialog(statementDialogStatement)"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- Delete Statement Dialog -->
  <q-dialog v-model="deleteDialogVisible">
    <q-card>
      <q-card-section>
        <div class="row items-center">
          <q-avatar
            icon="book"
            color="primary"
            text-color="white"
          />
          <span class="q-ml-sm">
            Are you sure you want to delete this statement?
          </span>
        </div>
        <div
          v-if="deleteDialogStatementNumber"
          class="row justify-center text-center"
        >
          Number: {{ deleteDialogStatementNumber }}
        </div>
        <div class="row justify-center text-center">
          Month: {{ purchaseStore.monthDisplay }}
        </div>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn
          flat
          label="Yes, delete it"
          color="primary"
          @click="deleteStatement()"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

</div>
</template>

<style scoped lang="scss"></style>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { onMounted, Ref, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import FileUploader from 'src/components/FileUploader.vue'
import { readableDateNEW, readableDateTime } from 'src/filters'
import { handlePromiseError } from 'src/stores'
import { usePurchaseStore } from 'src/stores/purchase';
import { ExpenseMonth, ExpenseStatement } from 'src/types';

const quasar = useQuasar()
const router = useRouter()
const purchaseStore = usePurchaseStore()

let sendNotificationDialogVisible = ref(false)
let lockMonthDialogVisible = ref(false)

let statementDialogVisible = ref(false)
let statementDialogStatement = ref({}) as Ref<ExpenseStatement>

let deleteDialogVisible = ref(false)
let statementPkToDelete = ref(-1)
let deleteDialogStatementNumber = ref('')

let selectedFiles = ref(new File([''], ''))

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
  },
  {
    name: 'date', label: 'Date', align: 'center'
  },
  {
    name: 'approved', label: 'Fiscal Approved', field: 'approved',
    sortable: true, align: 'center'
  }
]

const statementCols = [
  {
    name: 'card', required: true, label: 'Card', field: 'card', sortable: true,
    align: 'center'
  },
  {
    name: 'allCleared', label: 'All Cleared', field: 'all_cleared',
    align: 'center'
  },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
]

function viewingThisMonth() {
  return purchaseStore.firstOfSelectedMonth.getTime() ===
    purchaseStore.firstOfThisMonth.getTime()
}

function selectedMonthExpenseMonths() {
  return purchaseStore.fiscalExpenseMonths[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function selectedMonthExpensesLoaded() {
  return purchaseStore.fiscalExpenseMonths[purchaseStore.yearInt] &&
    purchaseStore.fiscalExpenseMonths[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function selectedMonthStatements() {
  return purchaseStore.expenseStatements[purchaseStore.yearInt] &&
    purchaseStore.expenseStatements[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function selectedMonthStatementsLoaded() {
  return purchaseStore.expenseStatements[purchaseStore.yearInt] &&
    purchaseStore.expenseStatements[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function expenseMonthFiscalApproved(expenseMonth: ExpenseMonth) {
  return expenseMonth.status == 'fiscal_approved'
}

function expenseMonthFiscalDenied(expenseMonth: ExpenseMonth) {
  return expenseMonth.status == 'fiscal_denied'
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
      return 'Submitted'
    case 'approver_denied':
      return 'Manager Denied'
    case 'approver_approved':
      return 'Manager Approved'
    case 'fiscal_denied':
      return 'Fiscal Denied'
    case 'fiscal_approved':
      return 'Fiscal Approved'
    default:
      return 'Unknown'
  }
}

function progressBarColor(status: string) {
  switch (status) {
    case 'draft':
    case 'submitted':
    case 'approver_denied':
      return 'blue'
    case 'fiscal_denied':
      return 'red'
    case 'approver_approved':
      return 'warning'
    case 'fiscal_approved':
      return 'green'
    default:
      return 'grey'
  }
}

function dateLabel(row: ExpenseMonth) {
  switch (row.status) {
    case 'draft':
      return ''
    case 'submitted':
      return `Submitted on ${readableDateTime(row.submitted_at)}`
    case 'approver_denied':
      return `Denied by ${row.denier_name} on ${readableDateTime(row.approved_as_of)}`
    case 'fiscal_denied':
      return `Denied by ${row.fiscal_approver_name} on ${readableDateTime(row.fiscal_approved_at)}`
    case 'approver_approved':
      return `Approved as of ${readableDateTime(row.approved_as_of)}`
    case 'fiscal_approved':
      return `Approved by ${row.fiscal_approver_name} on ${readableDateTime(row.fiscal_approved_at)}`
    default:
      return ''
  }
}

function canViewDetail(status: string) {
  return status !== 'draft'
}

function retrieveMonthEMs(year: number, month: number): Promise<void> {
  if (
    purchaseStore.fiscalExpenseMonths[year] &&
    purchaseStore.fiscalExpenseMonths[year][month]
  ) {
    return Promise.resolve()
  }
  // Get a month of EMs 
  return new Promise((resolve, reject) => {
    purchaseStore.getFiscalMonthEMs(year, month)
      .then(() => {
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving fiscal EMs', error)
        reject()
      })
  })
}

function retrieveMonthStatements(year: number, month: number, refresh=false): Promise<void> {
  if (
    !refresh && purchaseStore.expenseStatements[year] &&
    purchaseStore.expenseStatements[year][month]
  ) {
    return Promise.resolve()
  }
  return new Promise((resolve, reject) => {
    purchaseStore.getExpenseStatements(year, month)
      .then(() => {
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving expense statements', error)
        reject()
      })
  })
}

function navigateToDetail(expenseMonthPK: number) {
  router.push({
    name: 'fiscal-approve-expenses-detail',
    params: {
      expenseMonthPK: expenseMonthPK.toString()
    }
  })
  .catch(e => {
    console.error('Error navigating to time off request detail:', e)
  })
}

function sendNotifications() {
  purchaseStore.sendExpenseStatementNotifications()
    .then(() => {
      quasar.notify('Sent notifications to card holders.')
    })
    .catch(e => {
      console.error(e)
    })
}

function showStatmentDialog(statement: any) {
  statementDialogStatement.value = statement
  statementDialogVisible.value = true
}

function showDeleteStatementDialog(statement: any) {
  deleteDialogStatementNumber.value = statement.card.display
  statementPkToDelete.value = statement.pk
  deleteDialogVisible.value = true
}

function deleteStatement(): void {
  purchaseStore.deleteExpenseStatement(statementPkToDelete.value)
    .then(() => {
      statementDialogVisible.value = false
      quasar.notify('Deleted a statement.')
      retrieveMonthStatements(
        purchaseStore.yearInt, purchaseStore.monthInt, true
      )
    })
    .catch(e => {
      console.error(e)
    })
}

function toggleLockCurrentExpenseMonth() {
  const lock = !purchaseStore.expenseMonthLocked
  purchaseStore.lockCurrentExpenseMonth(
    lock, {'year': purchaseStore.yearInt, 'month': purchaseStore.monthInt}
  )
    .then(() => {
      quasar.notify(lock ? 'Locked the month.' : 'Unlocked the month.')
      purchaseStore.getExpenseMonthLocks()
    })
    .catch(e => {
      console.error(e)
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
  retrieveMonthStatements(purchaseStore.yearInt, purchaseStore.monthInt)
})

watch(() => purchaseStore.firstOfSelectedMonth, (newVal) => {
  if (viewingThisMonth()) return // Never do this on pageload
  const year = newVal.getFullYear()
  const month = newVal.getMonth()
  retrieveMonthEMs(year, month + 1)
  retrieveMonthStatements(year, month + 1)
})

</script>

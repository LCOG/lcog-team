<template>
<div class="q-mt-md">
  <!-- Statement -->
  <div v-if="statement">
    <div class="row items-center justify-between q-mt-md">
      <div class="text-h5">
        Statement for {{ card?.display }}
        in {{ purchaseStore.monthDisplay }}
      </div>
      <div>
        <q-btn v-if="!totalsMatch()" flat class="no-pointer-events">
          <div>Expenses total does not match statement</div>
          <q-icon color="orange" name="warning" size="md" />
        </q-btn>
        <q-btn v-if="!numExpensesMatch()" flat class="no-pointer-events">
          <div>Number of expenses does not match statement</div>
          <q-icon color="orange" name="warning" size="md" />
        </q-btn>
        <q-btn v-if="expensesMatchStatment()" flat class="no-pointer-events">
          <div>Statement and expenses seem to match</div>
          <q-icon color="green" name="check" size="md" />
        </q-btn>
      </div>
    </div>
    <StatementTable :statement="statement" />
  </div>
  <div v-else>
    <div class = "text-h5">
      No card selected in {{ purchaseStore.monthDisplay }}
    </div>
  </div>
  
  <!-- Expense Months -->
  <q-spinner-grid
    v-if="!thisMonthLoaded"
    class="spinner"
    color="primary"
    size="xl"
  />
  <div v-else-if="selectedMonthCardExpenseMonths().length">
    <div class="text-h6 q-mt-lg">Submitted Total: ${{ expensesTotal() }}</div>
    <div v-for="em of selectedMonthCardExpenseMonths()" :key="em.pk">
      <div class="text-bold q-mt-sm">
        Submitted Total: ${{ expenseMonthTotal(em) }}
      </div>
      <div class="q-mt-sm">
        <div v-if="largeExpense(em)" class="text-h6 text-warning">
          Take Note! Expense of $1000 or more
        </div>
        <q-table
          flat bordered
          :title="tableTitleDisplay(em)"
          :rows="em.expenses"
          :columns="columns"
          :dense="$q.screen.lt.lg"
          :grid="$q.screen.lt.md"
          row-key="name"
          binary-state-sort
          :pagination="pagination"
          class="expense-table"
          no-data-label="No expenses entered this month"
        >
          <template v-slot:body-cell-name="props">
            <q-td key="name" :props="props" style="white-space: normal;">
              {{ props.row.name }}
            </q-td>
          </template>
          <template v-slot:body-cell-date="props">
            <q-td key="date" :props="props">
              {{ readableDateNEW(props.row.date) }}
            </q-td>
          </template>
          <template v-slot:body-cell-vendor="props">
            <q-td key="vendor" :props="props" style="white-space: normal;">
              {{ props.row.vendor }}
            </q-td>
          </template>
          <template v-slot:body-cell-amount="props">
            <q-td
              key="expense_amount"
              :props="props"
              style="white-space: normal;"
              :class="props.row.amount >= 1000 ? 'bg-yellow' : ''"
            >
              ${{ props.row.amount }}
            </q-td>
          </template>
          <template v-slot:body-cell-gls="props">
            <q-td key="gls" :props="props">
              <div
                class="text-pre-wrap"
                v-for="gl in props.row.gls"
                :key="props.row.gls.indexOf(gl)"
              >
                <div>
                  <span>{{ gl.code }} (Job: {{ gl.job }}</span>
                  <span v-if="gl.activity">, Activity: {{ gl.activity }}</span>
                  <span>): ${{ gl.amount }}</span>
                </div>
                <div v-if="gl.approved_at">
                  Approved by {{ gl.approver.name }}
                  ({{ readableDateTime(gl.approved_at) }})
                </div>
                <div v-else class="text-bold">
                  Not yet approved by {{ gl.approver.name }}
                </div>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-receipt="props">
            <q-td key="receipt" :props="props">
              <DocumentViewer
                v-if="props.row.receipt"
                :documentUrl="props.row.receipt"
                iconButton
                flat
              />
            </q-td>
          </template>
          <!-- GRID MODE -->
          <template v-slot:item="props">
            <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3">
              <q-card class="q-py-sm">
                <q-list dense>
                  <q-item v-for="col in props.cols" :key="col.name">
                    <div class="q-table__grid-item-row">
                      <div class="q-table__grid-item-title">
                        {{ col.label }}
                      </div>
                      <div
                        class="q-table__grid-item-value"
                        v-if="col.name == 'date'"
                      >
                        {{ readableDateNEW(col.value) }}
                      </div>
                      <div
                        class="q-table__grid-item-value"
                        v-else-if="col.name == 'amount'"
                        :class="props.row.amount >= 1000 ? 'bg-yellow' : ''"
                      >
                        ${{ col.value }}
                      </div>
                      <div
                        class="q-table__grid-item-value"
                        v-else-if="col.name == 'gls'"
                      >
                        <div
                          class="text-pre-wrap"
                          v-for="gl in props.row.gls"
                          :key="props.row.gls.indexOf(gl)"
                        >
                          <div>
                            <span>{{ gl.code }} (Job: {{ gl.job }}</span>
                            <span v-if="gl.activity">, Activity: {{ gl.activity }}</span>
                            <span>): ${{ gl.amount }}</span>
                          </div>
                          <div v-if="gl.approved_at">
                            Approved by {{ gl.approver.name }}
                            ({{ readableDateTime(gl.approved_at) }})
                          </div>
                          <div v-else class="text-bold">
                            Not yet approved by {{ gl.approver.name }}
                          </div>
                        </div>
                      </div>
                      <div
                        class="q-table__grid-item-value"
                        v-else-if="col.label == 'Receipt'"
                      >
                        <DocumentViewer
                          v-if="col.value"
                          :documentUrl="col.value"
                          iconButton
                          flat
                        />
                      </div>
                      <div class="q-table__grid-item-value" v-else>
                        {{ col.value }}
                      </div>
                    </div>
                  </q-item>
                </q-list>
              </q-card>
            </div>
          </template>
        </q-table>

        <div v-if="em.submitter_note">
          <div id="submitter-note" class="q-mt-md q-pa-sm bg-info font-bold">
            <div>Submitter Note:</div>
            <div>{{ em.submitter_note }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-h5">No such expense month.</div>

</div>
</template>

<style scoped lang="scss">
#submitter-note {
  font-size: 1.2em;
  font-weight: bold;
}
</style>

<script setup lang="ts">
import { onMounted, Ref, ref } from 'vue'
import { useRoute } from 'vue-router'

import DocumentViewer from 'src/components/DocumentViewer.vue'
import StatementTable from 'src/components/purchases/StatementTable.vue'
import { readableDateNEW, readableDateTime } from 'src/filters'
import { handlePromiseError } from 'src/stores'
import { usePurchaseStore } from 'src/stores/purchase'
import { ExpenseCard, ExpenseMonth, ExpenseStatement } from 'src/types'
import { getRouteParam } from 'src/utils'


const route = useRoute()
const purchaseStore = usePurchaseStore()

let card = ref(null) as Ref<ExpenseCard | null>
let statement = ref(null) as Ref<ExpenseStatement | null>

let expenseMonthPK = ref(-1)
let thisMonthLoaded = ref(false)

const pagination = {
  rowsPerPage: '50'
}

const columns = [
  {
    name: 'name', field: 'name', label: 'Item', required: true, align: 'left',
    sortable: true
  },
  {
    name: 'date', field: 'date', label: 'Date', align: 'center', sortable: true
  },
  {
    name: 'vendor', field: 'vendor', label: 'Vendor', align: 'center',
    sortable: true
  },
  {
    name: 'amount', field: 'amount', label: 'Amount', align: 'center',
    sortable: true
  },
  {
    name: 'gls', field: 'gls', label: 'GL Codes', align: 'center',
    sortable: true, style: 'width: 10px'
  },
  { name: 'receipt', field: 'receipt', label: 'Receipt', align: 'center' }
]

function tableTitleDisplay(em: ExpenseMonth): string {
  return `${ purchaseStore.monthDisplay } expenses for ${ em.purchaser.name }`
}

function selectedMonthCardExpenseMonths(): Array<ExpenseMonth> {
  let currentCard = null
  let currentStatement = null
  const allEMs = purchaseStore.directorEMsDetails.filter(em => {
    return em.month === purchaseStore.monthInt &&
    em.year === purchaseStore.yearInt
  })
  let ems: Array<ExpenseMonth> = []
  if (allEMs.length) {
    const selectedEmployeeEM = allEMs.filter(em => {
      return em.pk === expenseMonthPK.value
    })[0]
    if (selectedEmployeeEM) {
      currentCard = selectedEmployeeEM.card
      currentStatement = selectedEmployeeEM.statement
      ems = allEMs.filter(em => {
        return em.card.pk === selectedEmployeeEM.card.pk
      })
    }
  }
  card.value = currentCard
  statement.value = currentStatement
  return ems
}

function retrieveExpenseMonthCardExpenseMonths(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!expenseMonthPK.value) {
      return
    }
    purchaseStore.getDirectorEMDetail(expenseMonthPK.value)
      .then((ems) => {
        purchaseStore.setMonth(ems[0].month, ems[0].year)
        thisMonthLoaded.value = true
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving expenses', error)
        reject()
      })
  })
}

function expenseMonthTotal(em: ExpenseMonth) {
  return em.expenses.reduce(
    (acc, expense) => {
      const amt = expense.amount ? parseFloat(expense.amount) : 0
      return acc + amt
    }, 0
  ).toFixed(2)
}

function largeExpense(em: ExpenseMonth) {
  return em.expenses.some(expense => parseFloat(expense.amount) >= 1000)
}

function expensesTotal() {
  let total = 0
  for (let em of selectedMonthCardExpenseMonths()) {
    total += em.expenses.reduce(
      (acc, expense) => {
        const amt = expense.amount ? parseFloat(expense.amount) : 0
        return acc + amt
      }, 0
    )
  }
  return total.toFixed(2)
}

function totalsMatch() {
  const statementTotal = statement.value?.items?.reduce(
    (acc, item) => acc + parseFloat(item.amount), 0
  ).toFixed(2)
  return statementTotal == expensesTotal()
}

function numExpensesMatch() {
  const expenses = []
  for (let em of selectedMonthCardExpenseMonths()) {
    expenses.push(...em.expenses)
  }
  return expenses.length == statement.value?.items?.length
}

function expensesMatchStatment(): boolean {
  return totalsMatch() && numExpensesMatch()
}

onMounted(() => {
  const pk = getRouteParam(route, 'expenseMonthPK')
  expenseMonthPK.value = parseInt(pk ? pk : '-1')
  retrieveExpenseMonthCardExpenseMonths()
})

</script>

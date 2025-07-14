<template>
  <div class="q-py-sm">
    <q-spinner-grid
      v-if="!reviewsLoaded"
      class="spinner q-mt-lg"
      color="primary"
      size="xl"
    />
    <q-table
      v-else
      :rows="performanceReviews()"
      :columns="columns()"
      :dense="$q.screen.lt.lg"
      :grid="$q.screen.lt.md"
      :no-data-label="noDataLabel()"
      row-key="name"
      :rows-per-page-options="[0]"
    >
      <!-- Slots for body cells: Show dates in a familiar format; make sure
        status can wrap, and display action buttons -->
      <template v-slot:body-cell-employeeName="props">
        <q-td key="employeeName" :props="props">
          <q-btn
            @click="navigateToEmployeeDetail(props)"
            class="employee-name"
            flat
            rounded
            no-caps
          >
            {{ props.row.employee_name }}
          </q-btn>
        </q-td>
      </template>
      <template v-slot:body-cell-performancePeriod="props">
        <q-td key="performancePeriod" :props="props">
          {{ readableDateNEW(props.row.period_start_date) }} -
          {{ readableDateNEW(props.row.period_end_date) }}
        </q-td>
      </template>
      <template v-slot:body-cell-daysUntilReview="props">
        <q-td
          key="daysUntilReview"
          :props="props"
          :class="lateReviewClass(props.value)"
        >
          {{props.value}}
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td style="white-space: normal;" :props="props">
          {{ props.row.status }}
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <div class="row items-center justify-center q-gutter-xs">
            <!-- Edit/detail button -->
            <q-btn
              dense
              round
              flat
              color="grey"
              @click="editEvaluation(props)"
              icon="assignment"
            >
              <q-tooltip content-style="font-size: 16px">
                View Performance Review
              </q-tooltip>
            </q-btn>
            <!-- Feedback link button: Only show to managers -->
            <q-btn
              v-if="managerPk && props.row.manager_pk == managerPk"
              class="feedback-link"
              dense
              round
              flat
              color="grey"
              @click="copyFeedbackLinkToClipboard(props)"
              icon="link"
            >
              <q-tooltip content-style="font-size: 16px">
                Copy feedback link to clipboard
              </q-tooltip>
            </q-btn>
            <!-- Print button: Only show to managers -->
            <q-btn
              v-if="managerPk"
              dense
              round
              flat
              color="grey"
              @click="printEvaluation(props)"
              icon="print"
            >
              <q-tooltip content-style="font-size: 16px">
                Print Performance Review Form
              </q-tooltip>
            </q-btn>
            <!-- Alert icon: Show if employee action is required -->
            <q-icon
              v-if="props.row.employee_action_required[0]"
              color="orange"
              name="warning"
              size="md"
            >
              <q-tooltip content-style="font-size: 16px">
                <div>{{ props.row.employee_action_required[1]}}</div>
              </q-tooltip>
            </q-icon>
          </div>
        </q-td>
      </template>
      <!-- For grid mode, we need to specify everything in order for our action
        buttons to render -->
      <template v-slot:item="props">
        <div
          class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3
            grid-style-transition"
        >
          <q-card class="q-py-sm">
            <q-list dense>
              <q-item v-for="col in props.cols" :key="col.name">
                <div class="q-table__grid-item-row">
                  <div class="q-table__grid-item-title">{{ col.label }}</div>
                  <div
                    class="q-table__grid-item-value"
                    v-if="col.label == 'Employee'"
                  >
                    <q-btn
                      @click="navigateToEmployeeDetail(props)"
                      class="employee-name"
                      padding="none"
                      flat
                      no-caps
                    >
                      {{ col.value }}
                    </q-btn>
                  </div>
                  <div
                    class="q-table__grid-item-value"
                    v-else-if="col.label == 'Performance Period'"
                  >
                    {{ readableDateNEW(props.row.period_start_date) }} -
                    {{ readableDateNEW(props.row.period_end_date) }}
                  </div>
                  <div class="q-table__grid-item-value"
                    v-else-if="col.label == 'Days Until Review'"
                    :class="lateReviewClass(props.row.days_until_review)"
                  >
                    {{ props.row.days_until_review }}
                  </div>
                  <div
                    class="q-table__grid-item-value row q-gutter-sm items-center
                      justify-around"
                    v-else-if="col.label == 'Actions'"
                  >
                    <!-- Edit/detail button -->
                    <q-btn
                      dense
                      round
                      flat
                      color="grey"
                      @click="editEvaluation(props)"
                      icon="assignment"
                    >
                      <q-tooltip content-style="font-size: 16px">
                        View Performance Review
                      </q-tooltip>
                    </q-btn>
                    <!-- Feedback link button: Only show to managers -->
                    <q-btn
                      v-if="managerPk && props.row.manager_pk == managerPk"
                      dense
                      round
                      flat
                      color="grey"
                      @click="copyFeedbackLinkToClipboard(props)"
                      icon="link"
                    >
                      <q-tooltip content-style="font-size: 16px">
                        Copy feedback link to clipboard
                      </q-tooltip>
                    </q-btn>
                    <!-- Print button: Only show to managers -->
                    <q-btn
                      v-if="managerPk"
                      dense
                      round
                      flat
                      color="grey"
                      @click="printEvaluation(props)"
                      icon="print"
                    >
                      <q-tooltip content-style="font-size: 16px">
                        Print Performance Review Form
                      </q-tooltip>
                    </q-btn>
                    <!-- Alert icon: Show if employee action is required -->
                    <q-icon
                      v-if="props.row.employee_action_required[0]"
                      color="orange"
                      name="warning"
                      size="md"
                    >
                      <q-tooltip content-style="font-size: 16px">
                        <div>{{ props.row.employee_action_required[1]}}</div>
                      </q-tooltip>
                    </q-icon>
                  </div>
                  <div
                    class="q-table__grid-item-value"
                    v-else
                  >
                    {{ col.value }}
                  </div>
                </div>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </template>
    </q-table>
  </div>
</template>

<style lang="scss">
.q-table tbody td.td-status {
    min-width: 135px;
    white-space: normal;
}
.q-table tbody td.wide-actions {
    min-width: 200px;
    white-space: normal;
}
</style>

<script setup lang="ts">
import { Notify, QTable, QTableProps } from 'quasar'
import { onMounted, onUpdated, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import useEventBus from 'src/eventBus'
import { readableDateNEW } from 'src/filters'
import { useReviewStore } from 'src/stores/review'
import { ReviewRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface QuasarReviewTableRowClickActionProps {
  evt: MouseEvent;
  row: ReviewRetrieve;
}

const props = defineProps<{
  // Provide either employeePk or managerPk
  employeePk?: number, // If provided, show PRs for this employee
  
  managerPk?: number, // If provided, show direct report PRs for this manager
  // If managerPk is provided, provide either complete or incomplere
  complete?: boolean, // Show only completed PRs
  incomplete?: boolean, // Show only incomplete PRs
}>()

const router = useRouter()
const { bus } = useEventBus()
const reviewStore = useReviewStore()
let reviewsLoaded = ref(false)

// let lastPk = ref(-1)

function performanceReviews(): Array<ReviewRetrieve> {
  let prs = [] as Array<ReviewRetrieve>
  if (props.employeePk) {
    if (props.complete && props.complete === true) {
      prs = reviewStore.employeePRs.filter(pr => pr.complete === true)
    } else if (props.incomplete && props.incomplete === true) {
      prs = reviewStore.employeePRs.filter(pr => pr.complete === false)
    }
  } else if (props.managerPk) {
    if (props.complete && props.complete === true) {
      prs = reviewStore.completePRs
    } else if (props.incomplete && props.incomplete === true) {
      prs = reviewStore.incompletePRs
    }
  }
  let sorted_by_days = prs.sort((a, b) => {
    return a.days_until_review - b.days_until_review
  })
  let sorted_by_action_required = sorted_by_days.sort((a, b) => {
    // Sort by employee action required first
    if (a.employee_action_required[0] && !b.employee_action_required[0]) {
      return -1
    } else if (!a.employee_action_required[0] && b.employee_action_required[0]) {
      return 1
    }
    // If both have the same action required status, sort by days until review
    return a.days_until_review - b.days_until_review
  })
  return sorted_by_action_required
}

function columns() {
  if (props.managerPk) {
    return managerColumns
  } else {
    return employeeColumns
  }
}

const managerColumns: QTableProps['columns'] = [
  {
    name: 'employeeName', label: 'Employee', align: 'center',
    field: 'employee_name', sortable: true
  },
  {
    name: 'performancePeriod', align: 'center', label: 'Performance Period',
    field: 'performance_period'
  },
  {
    name: 'daysUntilReview', align: 'center', label: 'Days Until Review',
    field: 'days_until_review', sortable: true
  },
  {
    name: 'status', align: 'center', label: 'Status', field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: ''},
]

const employeeColumns: QTableProps['columns'] = [
  {
    name: 'performancePeriod', align: 'center', label: 'Performance Period',
    field: 'performance_period'
  },
  {
    name: 'daysUntilReview', align: 'center', label: 'Days Until Review',
    field: 'days_until_review', sortable: true
  },
  {
    name: 'status', align: 'center', label: 'Status', field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: ''},
]

function lateReviewClass(daysUntilReview: number): string {
  if (daysUntilReview < 0) {
    return 'bg-negative text-white'
  } else if (daysUntilReview < 7) {
    return 'bg-warning text-black'
  } else {
    return 'bg-white text-black'
  }
}

function noDataLabel(): string {
  // if (props.actionRequired) {
  //   return 'Great work! All done here.'
  // } else {
  //   return 'Nothing to show.'
  // }
  return 'Nothing to show.'
}

function retrievePerformanceReviews(): void {
  // Only get PRs if we haven't done it before
  // TODO: Fix this
  // if (props.pk == lastPk.value) {
  //   return
  // }
  // lastPk.value = props.pk

  if (props.employeePk) {
    reviewStore.getEmployeePRs(props.employeePk)
      .then(() => {
        reviewsLoaded.value = true
      })
      .catch(e => {
        console.error('Error retrieving employee PRs:', e)
      })
  }
  else if (props.managerPk) {
    if (props.complete) {
      reviewStore.getCompletePRs(props.managerPk)
        .then(() => {
          reviewsLoaded.value = true
        })
        .catch(e => {
          console.error(
            'Error retrieving getCompletePRs:',
            e
          )
        })
    } else if (props.incomplete) {
      reviewStore.getIncompletePRs(props.managerPk)
        .then(() => {
          reviewsLoaded.value = true
        })
        .catch(e => {
          console.error(
            'Error retrieving getIncompletePRs:',
            e
          )
        })
    }
  }
}

function navigateToEmployeeDetail(
  props: QuasarReviewTableRowClickActionProps
): void {
  router.push({ name: 'profile', params: { pk: props.row.employee_pk } })
    .catch(e => {
      console.error('Error navigating to employee PRs:', e)
    })
}

function editEvaluation(
  props: QuasarReviewTableRowClickActionProps
): void {
  router.push({ name: 'pr-details', params: { pk: props.row.pk } })
    .catch(e => {
      console.error('Error navigating to PR detail:', e)
    })
}

function copyFeedbackLinkToClipboard(
  props: QuasarReviewTableRowClickActionProps
): void {
  const origin = window.location.origin
  const url = `${origin}/note/new?employee=${props.row.employee_pk}`
  navigator.clipboard.writeText(url)
    .then(() => {
      console.log('Feedback link copied to clipboard:', url)
      Notify.create({
        message: 'Feedback link copied to clipboard',
        color: 'green',
        position: 'top',
        timeout: 2000,
      })
    })
    .catch(e => {
      console.error('Error copying feedback link to clipboard:', e)
    })
}

function printEvaluation(
  props: QuasarReviewTableRowClickActionProps
): void {
  router.push({ name: 'pr-print', params: { pk: props.row.pk } })
    .catch(e => {
      console.error('Error printing PR:', e)
    })
}

// function printEvaluationPositionDescription(
//   props: QuasarReviewTableRowClickActionProps
// ): void {
//   window.location.href = props.row.signed_position_description
// }

watch(() => bus.value.get('updateTeleworkApplicationTables'), () => {
  retrievePerformanceReviews()
})

onUpdated(() => {
  // retrievePerformanceReviews();
})

onMounted(() => {
  getCurrentUser()
    .then(() => {
      retrievePerformanceReviews()
    })
})

</script>

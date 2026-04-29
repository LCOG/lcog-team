<template>
<q-page class="q-pa-md">
  <div class="row items-center justify-between">
    <div class="text-h4 q-mb-md">Reports</div>
    <q-toggle
      v-model="showJunk"
      label="Show junk"
      color="primary"
      dense
      class="q-mb-md"
    />
  </div>
  
  <!-- PROCESSED, JUNK -->
  <q-card flat bordered class="q-mb-md" v-if="showJunk">
    <q-card-section>
      <div class="text-h6 q-mb-md">Junk</div>
      <q-table
        :rows="processedJunk()"
        :columns="processedColumns"
        row-key="pk"
        @row-click="onRowClick"
        :pagination="processedPagination"
        flat
      >
        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            {{ formatDate(props.value) }}
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>

  <!-- UNPROCESSED -->
  <q-card flat bordered class="q-mb-md">
    <q-card-section>
      <div class="text-h6 q-mb-md">Submitted Reports</div>
      <q-table
        :rows="submittedReports"
        :columns="submittedColumns"
        row-key="pk"
        @row-click="onRowClick"
        :pagination="submittedPagination"
        flat
      >
        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            {{ formatDate(props.value) }}
          </q-td>
        </template>

        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-chip
              text-color="white"
              :color="getStatusDisplay(props.value).color"
              :icon="getStatusDisplay(props.value).icon"
            >
              {{ getStatusDisplay(props.value).label }}
            </q-chip>
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>

  <!-- PROCESSED, PHISH -->
  <q-card flat bordered>
    <q-card-section>
      <div class="text-h6 q-mb-md">Processed Reports</div>
      <q-table
        :rows="processedPhish()"
        :columns="processedColumns"
        row-key="pk"
        @row-click="onRowClick"
        :pagination="processedPagination"
        flat
      >
        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            {{ formatDate(props.value) }}
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>
    
  <q-dialog v-model="showMessageDialog">
    <q-card style="min-width: 50vw; max-width: 90vw;">
      <q-card-section class="row">
        <div class="col">
          <div class="text-h6">Phish Report Message</div>
          <div class="text-subtitle2">
            Employee: {{ dialogReport?.employee?.name || '' }} — Submitted:
            {{ dialogReport?.created_at ? formatDate(dialogReport.created_at) : '' }}
          </div>
          <div
            v-if="dialogReport?.additional_info"
            class="text-body2 q-mt-sm"
          >
            <span class="text-bold">Message from User:</span>
            <span class="text-italic">"{{ dialogReport.additional_info }}"</span>
          </div>
        </div>
        <q-toggle
          class="col col-3"
          v-model="showRawJson"
          label="Raw JSON"
          color="primary"
          dense
        />
        <q-btn
          class="col col-2"
          label="Copy URL"
          color="primary"
          icon="content_copy"
          dense
          @click="copyReportUrl"
        />
      </q-card-section>

      <q-separator />

      <q-card-section>
        <phish-report-message-viewer
          :message="dialogMessage"
          :show-raw-json="showRawJson"
        />
      </q-card-section>

      <q-card-section v-if="dialogReport?.status === 'phish'">
        <div class="text-h6">Phish Checklist</div>
        <div v-if="phishTasks.length === 0" class="text-grey-7 q-mt-sm">
          No checklist tasks configured for your organization.
        </div>
        <div v-for="task in phishTasks" :key="task.pk">
          <q-checkbox
            :model-value="isTaskCompleted(task.pk)"
            :label="task.name"
            :disable="loading || checklistLoading[task.pk] === true"
            @update:model-value="(value) => onTaskToggle(task.pk, !!value)"
          />
        </div>
      </q-card-section>

      <q-card-actions align="center" class="q-mb-sm">
        <q-btn
          v-if="['reported', 'not_phish'].indexOf(dialogReport?.status || '') !== -1"
          label="It's a Phish!"
          color="negative"
          size="xl"
          unelevated
          @click="markAsPhish"
          :loading="loading"
        />
        <q-btn
          v-if="['reported', 'phish'].indexOf(dialogReport?.status || '') !== -1"
          label="Just junk"
          color="warning"
          text-color="black"
          size="xl"
          unelevated
          @click="markAsNotPhish"
          :loading="loading"
        />
        <q-btn
          v-if="['phish'].indexOf(dialogReport?.status || '') !== -1"
          label="Processed"
          color="primary"
          size="xl"
          unelevated
          @click="markAsProcessed"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</q-page>
</template>

<style lang="scss">
.q-table tbody tr {
  cursor: pointer;
}
</style>

<script setup lang="ts">
import { QTableProps } from 'quasar'
import PhishReportMessageViewer from
  'src/components/phish/PhishReportMessageViewer.vue'
import { usePhishStore } from 'src/stores/phish'
import { PhishReport, PhishTask } from 'src/types'
import { computed, ref, onMounted, Ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const phishStore = usePhishStore()

const submittedColumns: QTableProps['columns'] = [
  {
    name: 'employee_name',
    label: 'Employee Name',
    field: 'employee_name',
    align: 'left',
    sortable: true
  },
  {
    name: 'created_at',
    label: 'Date of Submission',
    field: 'created_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'left',
    sortable: true
  }
]

const processedColumns: QTableProps['columns'] = [
  {
    name: 'employee_name',
    label: 'Employee Name',
    field: 'employee_name',
    align: 'left',
    sortable: true
  },
  {
    name: 'created_at',
    label: 'Date of Submission',
    field: 'created_at',
    align: 'left',
    sortable: true
  }
]

const submittedPagination = ref({
  sortBy: 'created_at',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

const processedPagination = ref({
  sortBy: 'created_at',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

const submittedReports = ref([]) as Ref<Array<PhishReport>>
const processedReports = ref([]) as Ref<Array<PhishReport>>
const loading = ref(false)

const showJunk = ref(false)
const showMessageDialog = ref(false)
const showRawJson = ref(false)
const dialogMessage = ref<unknown | null>(null)
const dialogReport = ref<PhishReport | null>(null)
const checklistLoading = ref<{ [taskPk: number]: boolean }>({})

const phishTasks = computed<Array<PhishTask>>(() => phishStore.allPhishTasks)
const currentReportTasks = computed(() => {
  if (!dialogReport.value?.pk) return []
  return phishStore.getReportTasks(dialogReport.value.pk)
})

interface StatusDisplay {
  label: string
  icon: string
  color: string
}

function getStatusDisplay(status?: string): StatusDisplay {
  switch ((status || '').toLowerCase()) {
    case 'reported':
      return { label: 'New', icon: 'new_releases', color: 'primary' }
    case 'phish':
      return {
        label: 'Phish - Ready for Processing',
        icon: 'report_problem',
        color: 'negative'
      }
    default:
      return {
        label: status || 'Unknown',
        icon: 'info',
        color: 'grey-7'
      }
  }
}

function processedJunk(): PhishReport[] {
  return processedReports.value.filter(r => r.status === 'not_phish')
}

function processedPhish(): PhishReport[] {
  return processedReports.value.filter(r => r.status === 'phish')
}

function formatDate(date: Date | string): string {
  if (!date) return ''
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function isTaskCompleted(taskPk: number): boolean {
  return currentReportTasks.value.some((reportTask) => reportTask.task_pk === taskPk)
}

async function loadChecklistDataForReport(reportPk: number) {
  await phishStore.getPhishTasks()
  await phishStore.getPhishReportTasks(reportPk, true)
}

async function refreshReports() {
  loading.value = true
  try {
    await phishStore.getAllReports()
    submittedReports.value = phishStore.submittedReports.map((r: any) =>
      ({ ...r, employee_name: r.employee?.name || '' }))
    processedReports.value = phishStore.processedReports.map((r: any) =>
      ({ ...r, employee_name: r.employee?.name || '' }))
  } finally {
    loading.value = false
  }
}

async function onRowClick(_evt: Event, row: PhishReport) {
  dialogReport.value = row
  dialogMessage.value = row.message
  showRawJson.value = false
  showMessageDialog.value = true
  if (row.status === 'phish' && row.pk) {
    await loadChecklistDataForReport(row.pk)
  }
  if (row.pk) {
    window.history.replaceState(null, '', `/phish/admin/reports/${row.pk}`)
  }
}

async function onTaskToggle(taskPk: number, checked: boolean) {
  if (!dialogReport.value?.pk) return
  const reportPk = dialogReport.value.pk
  checklistLoading.value[taskPk] = true

  try {
    if (checked) {
      await phishStore.createPhishReportTask(reportPk, taskPk)
      return
    }

    const reportTask = currentReportTasks.value.find(
      (item) => item.task_pk === taskPk
    )
    if (reportTask) {
      await phishStore.deletePhishReportTask(reportTask.pk, reportPk)
    }
  } finally {
    checklistLoading.value[taskPk] = false
  }
}

async function markAsPhish() {
  if (!dialogReport.value?.pk) return
  const reportPk = dialogReport.value.pk
  loading.value = true
  try {
    await phishStore.markReportVerdict(dialogReport.value.pk, 'phish')
    dialogReport.value = {
      ...dialogReport.value,
      status: 'phish',
      processed: false
    }
    await refreshReports()
    const refreshedDialogReport = submittedReports.value.find(
      (report) => report.pk === reportPk
    )
    if (refreshedDialogReport) {
      dialogReport.value = refreshedDialogReport
    }
    await loadChecklistDataForReport(reportPk)
  } finally {
    loading.value = false
  }
}

async function markAsNotPhish() {
  if (!dialogReport.value?.pk) return
  loading.value = true
  try {
    await phishStore.markReportVerdict(dialogReport.value.pk, 'not_phish')
    showMessageDialog.value = false
    await refreshReports()
  } finally {
    loading.value = false
  }
}

async function markAsProcessed() {
  if (!dialogReport.value?.pk) return
  loading.value = true
  try {
    await phishStore.markReportProcessed(dialogReport.value.pk)
    showMessageDialog.value = false
    await refreshReports()
  } finally {
    loading.value = false
  }
}

function launchDialogWithReportPk(reportPk: number) {
  const report = submittedReports.value.find(r => r.pk === reportPk) ||
    processedReports.value.find(r => r.pk === reportPk)
  if (report) {
    onRowClick(new Event('click'), report)
  }
}

function copyReportUrl() {
  if (!dialogReport.value?.pk) return
  const url =
    `${window.location.origin}/phish/admin/reports/${dialogReport.value.pk}`
  navigator.clipboard.writeText(url)
    .then(() => {
      // Optionally show a success message
      console.log('Report URL copied to clipboard')
    })
    .catch((err) => {
      // Optionally show an error message
      console.error('Failed to copy report URL: ', err)
    })
}

onMounted(() => {
  refreshReports().then(() => {
    // Open dialog for report if there's a route param
    if (route.params.pk) {
      const reportPk = parseInt(route.params.pk as string, 10)
      if (!isNaN(reportPk)) {
        launchDialogWithReportPk(reportPk)
      }
    }
  })
})

</script>

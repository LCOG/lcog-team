<template>
<q-page class="q-pa-md">
  <div class="text-h4 q-mb-md">Reports</div>
  
  <q-card flat bordered class="q-mb-md">
    <q-card-section>
      <div class="text-h6 q-mb-md">Submitted Reports</div>
      
      <div class="row items-center justify-between q-mb-md">
        <q-btn 
          label="Mark Selected Complete" 
          color="primary" 
          :disable="selected.length === 0" 
          @click="markSelectedComplete"
          unelevated
        />
        <div v-if="selected.length > 0" class="text-body2 text-grey-7">
          {{ selected.length }} selected
        </div>
      </div>

      <q-table
        :rows="submittedReports"
        :columns="submittedColumns"
        row-key="pk"
        selection="multiple"
        v-model:selected="selected"
        @row-click="onRowClick"
        :pagination="submittedPagination"
        flat
      >
        <template v-slot:body-cell-timestamp="props">
          <q-td :props="props">
            {{ formatDate(props.value) }}
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>

  <q-card flat bordered>
    <q-card-section>
      <div class="text-h6 q-mb-md">Processed Reports</div>
      
      <q-table
        :rows="processedReports"
        :columns="processedColumns"
        row-key="pk"
        @row-click="onRowClick"
        :pagination="processedPagination"
        flat
      >
        <template v-slot:body-cell-timestamp="props">
          <q-td :props="props">
            {{ formatDate(props.value) }}
          </q-td>
        </template>
      </q-table>
    </q-card-section>
  </q-card>
    
  <q-dialog v-model="showMessageDialog">
    <q-card style="min-width: 50vw; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Phish Report Message</div>
        <div class="text-subtitle2">Employee: {{ dialogReport?.employee?.name || '' }} — Submitted: {{ dialogReport?.timestamp ? formatDate(dialogReport.timestamp) : '' }}</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <pre style="white-space: pre-wrap; word-break: break-word;" v-html="highlightedMessage"></pre>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</q-page>
</template>

<style lang="scss">
.json-key { color: #9c27b0; font-weight: 600; }
.json-string { color: #1976d2; }
.json-number { color: #d32f2f; }
.json-boolean { color: #ff9800; font-weight: 600; }
.json-null { color: #757575; font-style: italic; }
pre { background: #f6f8fa; padding: 12px; border-radius: 4px; }

.q-table tbody tr {
  cursor: pointer;
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed, Ref } from 'vue'
import { usePhishStore } from 'src/stores/phish'
import { PhishReport } from 'src/types'
import { QTableProps } from 'quasar'

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
    name: 'timestamp',
    label: 'Date of Submission',
    field: 'timestamp',
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
    name: 'timestamp',
    label: 'Date of Submission',
    field: 'timestamp',
    align: 'left',
    sortable: true
  }
]

const submittedPagination = ref({
  sortBy: 'timestamp',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

const processedPagination = ref({
  sortBy: 'timestamp',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

const submittedReports = ref([]) as Ref<Array<PhishReport>>
const processedReports = ref([]) as Ref<Array<PhishReport>>
const selected = ref([]) as Ref<Array<PhishReport>>
const loading = ref(false)

const showMessageDialog = ref(false)
const dialogMessage = ref<JSON | null>(null)
const dialogReport = ref<PhishReport | null>(null)

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

function escapeHtml(unsafe: string) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function syntaxHighlight(json: any) {
  let str = typeof json !== 'string' ? JSON.stringify(json, undefined, 2) : json
  str = escapeHtml(str)
  return str.replace(/("(\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match: string) => {
    let cls = 'number'
    if (/^"/.test(match)) {
      cls = /:$/.test(match) ? 'key' : 'string'
    } else if (/true|false/.test(match)) {
      cls = 'boolean'
    } else if (/null/.test(match)) {
      cls = 'null'
    }
    return `<span class="json-${cls}">${match}</span>`
  })
}

const highlightedMessage = computed(() => dialogMessage.value ? syntaxHighlight(dialogMessage.value) : '')

async function refreshReports() {
  loading.value = true
  try {
    await phishStore.getReports()
    submittedReports.value = phishStore.submittedReports.map((r: any) => ({ ...r, employee_name: r.employee?.name || '' }))
    processedReports.value = phishStore.processedReports.map((r: any) => ({ ...r, employee_name: r.employee?.name || '' }))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshReports()
})

async function markSelectedComplete() {
  if (!selected.value.length) return
  loading.value = true
  try {
    await phishStore.markReportsProcessed(selected.value)
    selected.value = []
    await refreshReports()
  } finally {
    loading.value = false
  }
}

function onRowClick(evt: Event, row: PhishReport) {
  dialogReport.value = row
  dialogMessage.value = row.message
  showMessageDialog.value = true
}



</script>

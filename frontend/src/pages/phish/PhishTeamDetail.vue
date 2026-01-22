<template>
<q-page class="q-pa-md">
  <div class="text-h4">Phishing Reports</div>
  <div class="q-mt-md">
    <div class="row items-center justify-between q-mb-sm">
      <q-btn label="Mark Selected Complete" color="primary" :disable="selected.length === 0" @click="markSelectedComplete" />
    </div>

    <q-table
      title="Submitted Reports"
      :rows="submittedReports"
      :columns="columns"
      row-key="pk"
      selection="multiple"
      v-model:selected="selected"
      @row-click="onRowClick"
      flat
      dense
    >
    </q-table>

    <div class="q-mt-lg">
      <div class="text-subtitle2 q-mb-sm">Completed Reports</div>
      <q-table
        :rows="processedReports"
        :columns="columns"
        row-key="id"
        @row-click="onRowClick"
        flat
        dense
      />
    </div>
    
    <q-dialog v-model="showMessageDialog">
      <q-card style="min-width: 50vw; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">Phish Report Message</div>
          <div class="text-subtitle2">Employee: {{ dialogReport?.employee?.name || '' }} — Submitted: {{ dialogReport?.timestamp ? new Date(dialogReport.timestamp).toLocaleString() : '' }}</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <pre style="white-space: pre-wrap; word-break: break-word;" v-html="highlightedMessage"></pre>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup @click="showMessageDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</q-page>
</template>

<style lang="scss">
.json-key { color: #9c27b0; font-weight: 600; }
.json-string { color: #1976d2; }
.json-number { color: #d32f2f; }
.json-boolean { color: #ff9800; font-weight: 600; }
.json-null { color: #757575; font-style: italic; }
pre { background: #f6f8fa; padding: 12px; border-radius: 4px; }
</style>

<script setup lang="ts">
import { ref, onMounted, computed, Ref } from 'vue'
import { usePhishStore } from 'src/stores/phish'
import { PhishReport } from 'src/types'

const phishStore = usePhishStore()

const columns = [
  {
    name: 'employee_name', label: 'Employee Name', field: 'employee_name', sortable: true
  },
  {
    name: 'timestamp', label: 'Date of Submission', field: 'timestamp', sortable: true,
    format: (ts: string) => ts ? new Date(ts).toLocaleString() : ''
  }
]

const submittedReports = ref([]) as Ref<Array<PhishReport>>
const processedReports = ref([]) as Ref<Array<PhishReport>>
const selected = ref([]) as Ref<Array<PhishReport>>
const loading = ref(false)

const showMessageDialog = ref(false)
const dialogMessage = ref<JSON | null>(null)
const dialogReport = ref<PhishReport | null>(null)

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

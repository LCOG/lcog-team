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
        <template v-slot:body-cell-created_at="props">
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
        </div>
        <q-toggle
          class="col col-3"
          v-model="showRawJson"
          label="Show raw JSON"
          color="primary"
          dense
        />
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div v-if="showRawJson" class="raw-json-panel">
          <pre class="raw-json-content">{{ prettyRawJson }}</pre>
        </div>

        <div v-else class="email-panel">
          <div class="email-meta-row">
            <span class="email-meta-label">Subject</span>
            <span class="email-meta-value">
              {{ selectedMessage?.subject || '(No subject)' }}
            </span>
          </div>
          <div class="email-meta-row">
            <span class="email-meta-label">From</span>
            <span class="email-meta-value">{{ fromDisplay }}</span>
          </div>
          <div class="email-meta-row">
            <span class="email-meta-label">To</span>
            <span class="email-meta-value">{{ toDisplay }}</span>
          </div>
          <div v-if="ccDisplay" class="email-meta-row">
            <span class="email-meta-label">CC</span>
            <span class="email-meta-value">{{ ccDisplay }}</span>
          </div>
          <div v-if="bccDisplay" class="email-meta-row">
            <span class="email-meta-label">BCC</span>
            <span class="email-meta-value">{{ bccDisplay }}</span>
          </div>
          <div class="email-meta-row">
            <span class="email-meta-label">Received</span>
            <span class="email-meta-value">{{ receivedDisplay }}</span>
          </div>

          <q-separator class="q-my-md" />

          <div class="email-body" v-html="renderedBodyHtml"></div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</q-page>
</template>

<style lang="scss">
.email-panel {
  background: #f8fafc;
  border-radius: 6px;
  padding: 12px;
}

.raw-json-panel {
  background: #f8fafc;
  border-radius: 6px;
  padding: 12px;
}

.raw-json-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px;
  font-family: monospace;
  font-size: 12px;
}

.email-meta-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.email-meta-label {
  min-width: 82px;
  font-weight: 600;
  color: #4b5563;
}

.email-meta-value {
  color: #111827;
  overflow-wrap: anywhere;
}

.email-id {
  font-family: monospace;
  font-size: 12px;
}

.email-body {
  background: white;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px;
  overflow-wrap: anywhere;
}

.email-body img {
  max-width: 100%;
  height: auto;
}

.email-body .email-link-callout {
  display: inline;
  color: #b45309;
  background: #fffbeb;
  border: 1px dashed #f59e0b;
  border-radius: 4px;
  padding: 1px 4px;
  font-weight: 600;
}

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
    name: 'created_at',
    label: 'Date of Submission',
    field: 'created_at',
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
const selected = ref([]) as Ref<Array<PhishReport>>
const loading = ref(false)

const showMessageDialog = ref(false)
const showRawJson = ref(false)
const dialogMessage = ref<unknown | null>(null)
const dialogReport = ref<PhishReport | null>(null)

interface EmailAddress {
  name?: string
  address?: string
}

interface RecipientEntry {
  emailAddress?: EmailAddress
}

interface OutlookBody {
  contentType?: string
  content?: string
}

interface OutlookMessage {
  subject?: string
  sender?: RecipientEntry
  from?: RecipientEntry
  toRecipients?: RecipientEntry[]
  ccRecipients?: RecipientEntry[]
  bccRecipients?: RecipientEntry[]
  sentDateTime?: string
  receivedDateTime?: string
  internetMessageId?: string
  bodyPreview?: string
  body?: OutlookBody
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

function escapeHtml(unsafe: string) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function normalizeMessage(value: unknown): OutlookMessage | null {
  if (!value) return null

  if (typeof value === 'string') {
    try {
      return JSON.parse(value) as OutlookMessage
    } catch {
      return {
        body: {
          contentType: 'text',
          content: value
        }
      }
    }
  }

  if (typeof value === 'object') {
    return value as OutlookMessage
  }

  return null
}

function formatAddress(recipient?: RecipientEntry): string {
  const name = recipient?.emailAddress?.name || ''
  const address = recipient?.emailAddress?.address || ''

  if (name && address) return `${name} <${address}>`
  if (address) return address
  if (name) return name
  return ''
}

function formatRecipients(recipients?: RecipientEntry[]): string {
  if (!recipients?.length) return ''
  return recipients
    .map(formatAddress)
    .filter(Boolean)
    .join(', ')
}

function sanitizeAndAnnotateHtml(html: string): string {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const urlRegex = /https?:\/\/[^\s<>")]+/gi
  const explicitColorRegex = /(^|;)\s*color\s*:/i
  const darkColorRegex = /#(?:000|000000|111|111111|222|222222)|\bblack\b|rgb\(\s*(?:\d|[1-4]\d|5[0-9])\s*,\s*(?:\d|[1-4]\d|5[0-9])\s*,\s*(?:\d|[1-4]\d|5[0-9])\s*\)/i

  const appendStyle = (element: Element, declaration: string) => {
    const currentStyle = (element.getAttribute('style') || '').trim()
    const joiner = currentStyle && !currentStyle.endsWith(';') ? '; ' : ''
    element.setAttribute('style', `${currentStyle}${joiner}${declaration}`)
  }

  doc.querySelectorAll(
    'script, style, iframe, object, embed, link, meta, base, form, input, \
    button, textarea, select'
  ).forEach((node) => {
    node.remove()
  })

  doc.querySelectorAll('*').forEach((el) => {
    Array.from(el.attributes).forEach((attr) => {
      const name = attr.name.toLowerCase()
      const value = attr.value.trim()

      if (name.startsWith('on')) {
        el.removeAttribute(attr.name)
        return
      }

      if ((name === 'href' || name === 'src') && /^javascript:/i.test(value)) {
        el.removeAttribute(attr.name)
      }
    })

    const style = (el.getAttribute('style') || '').toLowerCase()
    const bgColorAttr = (el.getAttribute('bgcolor') || '').toLowerCase()
    const hasDarkBackground = darkColorRegex.test(style) ||
      darkColorRegex.test(bgColorAttr)

    if (hasDarkBackground && !explicitColorRegex.test(style)) {
      appendStyle(el, 'color: #ffffff;')
    }
  })

  doc.querySelectorAll('a').forEach((anchor) => {
    const href = anchor.getAttribute('href') || ''
    const text = (anchor.textContent || '').trim() || href || 'Link'
    const span = doc.createElement('span')
    span.className = 'email-link-callout'
    span.textContent = `${text} (${href || 'no href'})`
    anchor.replaceWith(span)
  })

  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT)
  const nodes: Text[] = []
  let current = walker.nextNode()

  while (current) {
    nodes.push(current as Text)
    current = walker.nextNode()
  }

  nodes.forEach((textNode) => {
    const source = textNode.nodeValue || ''
    if (!urlRegex.test(source)) return

    urlRegex.lastIndex = 0
    const fragment = doc.createDocumentFragment()
    let lastIndex = 0
    let match = urlRegex.exec(source)

    while (match) {
      const matchStart = match.index
      const url = match[0]

      if (matchStart > lastIndex) {
        fragment.appendChild(
          doc.createTextNode(source.slice(lastIndex, matchStart))
        )
      }

      const span = doc.createElement('span')
      span.className = 'email-link-callout'
      span.textContent = url
      fragment.appendChild(span)

      lastIndex = matchStart + url.length
      match = urlRegex.exec(source)
    }

    if (lastIndex < source.length) {
      fragment.appendChild(doc.createTextNode(source.slice(lastIndex)))
    }

    textNode.parentNode?.replaceChild(fragment, textNode)
  })

  return doc.body.innerHTML
}

const selectedMessage = computed(() => normalizeMessage(dialogMessage.value))

const fromDisplay = computed(() => {
  if (!selectedMessage.value) return '(Unknown sender)'
  return formatAddress(selectedMessage.value.from) ||
    formatAddress(selectedMessage.value.sender) || '(Unknown sender)'
})

const toDisplay = computed(() => {
  if (!selectedMessage.value) return '(No recipients)'
  return formatRecipients(selectedMessage.value.toRecipients) ||
    '(No recipients)'
})

const ccDisplay = computed(() => selectedMessage.value ?
  formatRecipients(selectedMessage.value.ccRecipients) : '')
const bccDisplay = computed(() => selectedMessage.value ?
  formatRecipients(selectedMessage.value.bccRecipients) : '')
const sentDisplay = computed(() => selectedMessage.value?.sentDateTime ?
  formatDate(selectedMessage.value.sentDateTime) : '(Unknown)')
const receivedDisplay = computed(() => selectedMessage.value?.receivedDateTime ?
  formatDate(selectedMessage.value.receivedDateTime) : '(Unknown)')

const renderedBodyHtml = computed(() => {
  if (!selectedMessage.value) {
    return '<div class="text-grey-7">No message available.</div>'
  }

  const body = selectedMessage.value.body
  const bodyContent = body?.content || selectedMessage.value.bodyPreview || ''

  if (!bodyContent) {
    return '<div class="text-grey-7">No message content provided.</div>'
  }

  if ((body?.contentType || '').toLowerCase() === 'html') {
    return sanitizeAndAnnotateHtml(bodyContent)
  }

  return `<div style="white-space: pre-wrap;">${escapeHtml(bodyContent)}</div>`
})

const prettyRawJson = computed(() => {
  if (dialogMessage.value == null) return ''

  if (typeof dialogMessage.value === 'string') {
    try {
      return JSON.stringify(JSON.parse(dialogMessage.value), null, 2)
    } catch {
      return dialogMessage.value
    }
  }

  try {
    return JSON.stringify(dialogMessage.value, null, 2)
  } catch {
    return String(dialogMessage.value)
  }
})

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
  showRawJson.value = false
  showMessageDialog.value = true
}



</script>

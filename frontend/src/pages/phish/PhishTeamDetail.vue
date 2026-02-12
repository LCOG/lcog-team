<template>
<q-page class="q-pa-md">
  <q-spinner-grid
    v-if="loading"
    class="spinner q-mt-lg"
    color="primary"
    size="xl"
  />
  
  <div v-else>
    <!-- Header with back button -->
    <div class="row items-center q-mb-md">
      <q-btn 
        flat 
        dense 
        round 
        icon="arrow_back" 
        @click="goBack"
        class="q-mr-md"
      >
        <q-tooltip>Back to Team List</q-tooltip>
      </q-btn>
      <div class="text-h4">{{ teamMember?.employeeName }}</div>
    </div>

    <!-- Main info cards -->
    <div class="row q-col-gutter-md q-mb-md">
      <!-- Profile card -->
      <div class="col-xs-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Profile</div>
            
            <div class="q-mb-sm">
              <div class="text-caption text-grey-7">Employee Name</div>
              <div class="text-body1">{{ teamMember?.employeeName }}</div>
            </div>

            <div class="q-mb-sm">
              <div class="text-caption text-grey-7">Risk Level</div>
              <q-select
                v-model="teamMember.riskLevel"
                :options="riskLevelOptions"
                @update:model-value="updateRiskLevel"
                outlined
                dense
                class="q-mt-xs"
              >
                <template v-slot:selected>
                  <q-badge 
                    :color="getRiskColor(teamMember.riskLevel)" 
                    :label="teamMember.riskLevel"
                  />
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-badge 
                        :color="getRiskColor(scope.opt)" 
                        :label="scope.opt"
                      />
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>

            <div>
              <div class="text-caption text-grey-7 q-mb-xs">Groups</div>
              <q-select
                v-model="teamMember.groups"
                :options="availableGroups"
                @update:model-value="updateGroups"
                multiple
                outlined
                dense
                use-chips
                new-value-mode="add-unique"
              >
                <template v-slot:selected-item="scope">
                  <q-chip
                    removable
                    @remove="scope.removeAtIndex(scope.index)"
                    :tabindex="scope.tabindex"
                    color="primary"
                    text-color="white"
                    size="sm"
                  >
                    {{ scope.opt }}
                  </q-chip>
                </template>
              </q-select>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Statistics cards -->
      <div class="col-xs-12 col-sm-6 col-md-8">
        <div class="row q-col-gutter-md">
          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Organic Reports</div>
                <div class="text-h5 text-primary">{{ teamMember?.organicReports }}</div>
                <div class="text-caption">Total reports made</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Synthetic Phishes</div>
                <div class="text-h5 text-orange">{{ syntheticReportedCount }} / {{ syntheticTests.length }}</div>
                <div class="text-caption">Reported / Received</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Educational Resources</div>
                <div class="text-h5 text-green">{{ educationalResourcesCompleted }} / {{ educationalResources.length }}</div>
                <div class="text-caption">Completed / Assigned</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs for detailed views -->
    <q-card flat bordered>
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="left"
      >
        <q-tab name="organic" label="Organic Reports" />
        <q-tab name="synthetic" label="Synthetic Phishes" />
        <q-tab name="resources" label="Educational Resources" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated>
        <!-- Organic Reports Tab -->
        <q-tab-panel name="organic">
          <div class="text-h6 q-mb-md">Organic Reports</div>
          
          <q-table
            :rows="organicReports"
            :columns="organicReportColumns"
            row-key="pk"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-created_at="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>
            
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn 
                  flat 
                  dense 
                  round 
                  icon="visibility" 
                  @click="viewReportDetails(props.row)"
                >
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- Synthetic Phishes Tab -->
        <q-tab-panel name="synthetic">
          <div class="text-h6 q-mb-md">Synthetic Phishing Tests</div>
          
          <q-table
            :rows="syntheticTests"
            :columns="syntheticTestColumns"
            row-key="id"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-reported="props">
              <q-td :props="props">
                <q-icon 
                  :name="props.value ? 'check_circle' : 'cancel'" 
                  :color="props.value ? 'positive' : 'negative'"
                  size="sm"
                />
              </q-td>
            </template>

            <template v-slot:body-cell-sentDate="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>

            <template v-slot:body-cell-reportedDate="props">
              <q-td :props="props">
                {{ props.value ? formatDate(props.value) : '-' }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- Educational Resources Tab -->
        <q-tab-panel name="resources">
          <div class="text-h6 q-mb-md">Educational Resources</div>
          
          <q-table
            :rows="educationalResources"
            :columns="resourceColumns"
            row-key="id"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-badge 
                  :color="props.value === 'completed' ? 'positive' : 'grey'" 
                  :label="props.value"
                />
              </q-td>
            </template>

            <template v-slot:body-cell-assignedDate="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>

            <template v-slot:body-cell-completedDate="props">
              <q-td :props="props">
                {{ props.value ? formatDate(props.value) : '-' }}
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn 
                  v-if="props.row.status === 'completed'"
                  flat 
                  dense 
                  label="Reassign" 
                  color="primary"
                  @click="reassignResource(props.row)"
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <!-- Report details dialog -->
    <q-dialog v-model="showReportDialog">
      <q-card style="min-width: 50vw; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">Report Details</div>
          <div class="text-subtitle2">
            Submitted: {{ selectedReport?.created_at ? formatDate(selectedReport.created_at) : '' }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="text-subtitle2 q-mb-sm">Report Type</div>
          <!-- <q-badge 
            :label="selectedReport?.organic ? 'Organic' : 'Synthetic'" 
            :color="selectedReport?.organic ? 'primary' : 'orange'"
          /> -->

          <div class="text-subtitle2 q-mt-md q-mb-sm">Message Content</div>
          <pre style="white-space: pre-wrap; word-break: break-word; background: #f6f8fa; padding: 12px; border-radius: 4px;" v-html="highlightedMessage"></pre>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
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
</style>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePhishStore } from 'src/stores/phish'
import { PhishReport } from 'src/types'
import { QTableProps } from 'quasar'

const router = useRouter()
const route = useRoute()
const phishStore = usePhishStore()

const loading = ref(false)
const activeTab = ref('organic')
const showReportDialog = ref(false)
const selectedReport = ref<PhishReport | null>(null)

const riskLevelOptions = ['low', 'med', 'high']
const availableGroups = ['Sales', 'Engineering', 'HR', 'Finance', 'Operations', 'Management']

interface TeamMember {
  pk: number
  employeeName: string
  riskLevel: 'low' | 'med' | 'high'
  organicReports: number
  groups: string[]
}

interface SyntheticTest {
  id: number
  sentDate: Date
  reported: boolean
  reportedDate: Date | null
  testName: string
}

interface EducationalResource {
  id: number
  title: string
  assignedDate: Date
  completedDate: Date | null
  status: 'pending' | 'completed'
}

// Mock data - replace with API calls
const teamMember = ref<TeamMember>({
  pk: Number(route.params.id),
  employeeName: 'Loading...',
  riskLevel: 'med',
  organicReports: 0,
  groups: []
})

const organicReports = ref<PhishReport[]>([])
const syntheticTests = ref<SyntheticTest[]>([])
const educationalResources = ref<EducationalResource[]>([])

const organicReportColumns: QTableProps['columns'] = [
  {
    name: 'created_at',
    label: 'Date',
    field: 'created_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'processed',
    label: 'Status',
    field: (row: PhishReport) => row.processed ? 'Processed' : 'Pending',
    align: 'center',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Actions',
    field: '',
    align: 'center'
  }
]

const syntheticTestColumns: QTableProps['columns'] = [
  {
    name: 'testName',
    label: 'Test Name',
    field: 'testName',
    align: 'left',
    sortable: true
  },
  {
    name: 'sentDate',
    label: 'Sent Date',
    field: 'sentDate',
    align: 'left',
    sortable: true
  },
  {
    name: 'reported',
    label: 'Reported',
    field: 'reported',
    align: 'center',
    sortable: true
  },
  {
    name: 'reportedDate',
    label: 'Reported Date',
    field: 'reportedDate',
    align: 'left',
    sortable: true
  }
]

const resourceColumns: QTableProps['columns'] = [
  {
    name: 'title',
    label: 'Resource Title',
    field: 'title',
    align: 'left',
    sortable: true
  },
  {
    name: 'assignedDate',
    label: 'Assigned Date',
    field: 'assignedDate',
    align: 'left',
    sortable: true
  },
  {
    name: 'completedDate',
    label: 'Completed Date',
    field: 'completedDate',
    align: 'left',
    sortable: true
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'center',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Actions',
    field: '',
    align: 'center'
  }
]

function formatDate(date: Date | string): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getRiskColor(riskLevel: string): string {
  switch (riskLevel) {
    case 'high':
      return 'red'
    case 'med':
      return 'orange'
    case 'low':
      return 'green'
    default:
      return 'grey'
  }
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

const highlightedMessage = computed(() => 
  selectedReport.value?.message ? syntaxHighlight(selectedReport.value.message) : ''
)

const syntheticReportedCount = computed(() => 
  syntheticTests.value.filter(test => test.reported).length
)

const educationalResourcesCompleted = computed(() =>
  educationalResources.value.filter(resource => resource.status === 'completed').length
)

async function loadTeamMemberData() {
  loading.value = true
  try {
    const memberId = Number(route.params.pk)
    
    // Load all reports for this employee
    await phishStore.getReports()
    
    // Mock data - replace with actual API calls
    // Filter reports for this specific employee
    organicReports.value = phishStore.processedReports.filter(
      (r: PhishReport) => r.employee.pk === memberId
    )
    
    // Load team member details from list (in real app, fetch from API)
    const mockMembers = [
      { pk: 5, employeeName: 'Dan Wilson', riskLevel: 'high' as const, organicReports: 2, groups: ['Engineering', 'Management'] },
      { pk: 2, employeeName: 'Bob Smith', riskLevel: 'low' as const, organicReports: 12, groups: ['Sales'] },
      { pk: 3, employeeName: 'Carol Williams', riskLevel: 'med' as const, organicReports: 5, groups: ['HR'] },
      { pk: 4, employeeName: 'David Brown', riskLevel: 'high' as const, organicReports: 1, groups: ['Finance'] },
      { pk: 1, employeeName: 'Emma Davis', riskLevel: 'med' as const, organicReports: 7, groups: ['Operations', 'Engineering'] }
    ]
    
    const member = mockMembers.find(m => m.pk === memberId)
    if (member) {
      teamMember.value = member
    }
    
    // Mock synthetic tests
    syntheticTests.value = [
      { id: 1, testName: 'CEO Fraud Test #1', sentDate: new Date('2025-12-01'), reported: true, reportedDate: new Date('2025-12-01') },
      { id: 2, testName: 'Invoice Scam Test', sentDate: new Date('2025-12-15'), reported: false, reportedDate: null },
      { id: 3, testName: 'Password Reset Phish', sentDate: new Date('2026-01-05'), reported: true, reportedDate: new Date('2026-01-05') }
    ]
    
    // Mock educational resources
    educationalResources.value = [
      { id: 1, title: 'Phishing Awareness Training', assignedDate: new Date('2025-11-01'), completedDate: new Date('2025-11-15'), status: 'completed' },
      { id: 2, title: 'Email Security Best Practices', assignedDate: new Date('2025-12-01'), completedDate: null, status: 'pending' },
      { id: 3, title: 'Spotting Social Engineering', assignedDate: new Date('2026-01-01'), completedDate: null, status: 'pending' }
    ]
    
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/phish/team')
}

function updateRiskLevel(newLevel: string) {
  console.log('Updating risk level to:', newLevel)
  // TODO: API call to update risk level
}

function updateGroups(newGroups: string[]) {
  console.log('Updating groups to:', newGroups)
  // TODO: API call to update groups
}

function viewReportDetails(report: PhishReport) {
  selectedReport.value = report
  showReportDialog.value = true
}

function reassignResource(resource: EducationalResource) {
  resource.status = 'pending'
  resource.completedDate = null
  resource.assignedDate = new Date()
  teamMember.value.resourcesCompleted--
  // TODO: API call to mark resource reassigned
}

onMounted(() => {
  loadTeamMemberData()
})
</script>

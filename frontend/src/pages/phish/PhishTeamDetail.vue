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
                <div class="text-h5 text-primary">{{ organicReports().length }}</div>
                <div class="text-caption">Total reports made</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Synthetic Phishes</div>
                <div class="text-h5 text-orange">{{ phishAssignmentsReported }} / {{ phishAssignments().length }}</div>
                <div class="text-caption">Reported / Received</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Educational Resources</div>
                <div class="text-h5 text-green">{{ trainingAssignmentsCompleted }} / {{ trainingAssignments().length }}</div>
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
            :rows="organicReports()"
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
          
          <!-- Send New Synthetic Phish -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="row items-center q-gutter-md">
              <div class="text-subtitle2">Send New:</div>
              <phish-template-select
                :label="'Select Template'"
                :read-only="false"
                @input="template => selectedPhishTemplate = template"
                style="width: 250px;"
              />
              <q-btn 
                label="Send Test Phish"
                color="primary"
                unelevated
                :disable="!selectedPhishTemplate"
                @click="createPhishAssignment()"
              />
            </q-card-section>
          </q-card>

          <!-- Synthetic Phishes Sent -->
          <q-table
            :rows="phishAssignments()"
            :columns="syntheticTestColumns"
            row-key="id"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-clicked="props">
              <q-td :props="props">
                <q-icon 
                  :name="props.value ? 'check_circle' : 'cancel'" 
                  :color="props.value ? 'positive' : 'negative'"
                  size="sm"
                />
              </q-td>
            </template>  
            <template v-slot:body-cell-reported="props">
              <q-td :props="props">
                <q-icon 
                  :name="props.value ? 'check_circle' : 'cancel'" 
                  :color="props.value ? 'positive' : 'negative'"
                  size="sm"
                />
              </q-td>
            </template>

            <template v-slot:body-cell-sentAt="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>

            <template v-slot:body-cell-reportedAt="props">
              <q-td :props="props">
                {{ props.value ? formatDate(props.value) : '-' }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- Educational Resources Tab -->
        <q-tab-panel name="resources">
          <div class="text-h6 q-mb-md">Educational Resources</div>
          
          <!-- Assign new Training  -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="row items-center q-gutter-md">
              <div class="text-subtitle2">Assign New:</div>
              <training-template-select
                :label="'Select Training Module'"
                :read-only="false"
                @input="template => selectedTrainingTemplate = template"
                style="width: 250px;"
              />
              <q-btn 
                label="Assign Training"
                color="primary"
                unelevated
                :disable="!selectedTrainingTemplate"
                @click="createTrainingAssignment()"
              />
            </q-card-section>
          </q-card>

          <phish-training-assignments-table
            :training-assignments="trainingAssignments()"
            :admin="true"
            @reassign="reassignResource"
          />
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
import PhishTemplateSelect from 'src/components/phish/PhishTemplateSelect.vue'
import TrainingTemplateSelect from 
  'src/components/phish/TrainingTemplateSelect.vue'
import PhishTrainingAssignmentsTable from 
  'src/components/phish/PhishTrainingAssignmentsTable.vue'
import { usePhishStore } from 'src/stores/phish'
import { usePeopleStore } from 'src/stores/people'
import { PhishReport, SyntheticPhishTemplate, TrainingTemplate, TrainingAssignment } from 'src/types'
import { QTableProps } from 'quasar'

const router = useRouter()
const route = useRoute()
const phishStore = usePhishStore()
const peopleStore = usePeopleStore()

const loading = ref(false)
const activeTab = ref('organic')
const showReportDialog = ref(false)
const selectedReport = ref<PhishReport | null>(null)
const selectedPhishTemplate = ref<SyntheticPhishTemplate | null>(null)
const selectedTrainingTemplate = ref<TrainingTemplate | null>(null)

const riskLevelOptions = ['low', 'med', 'high']
const availableGroups = ['Sales', 'Engineering', 'HR', 'Finance', 'Operations', 'Management']

interface TeamMember {
  pk: number
  employeeName: string
  riskLevel: 'low' | 'med' | 'high'
  groups: string[]
}

const teamMember = ref<TeamMember>({
  pk: Number(route.params.id),
  employeeName: 'Loading...',
  riskLevel: 'med',
  groups: []
})

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
    field: 'template_name',
    align: 'left'
  },
  {
    name: 'sentAt',
    label: 'Sent Date',
    field: 'sent_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'clicked',
    label: 'Clicked',
    field: 'clicked',
    align: 'center',
    sortable: true
  },
  {
    name: 'reported',
    label: 'Reported',
    field: 'reported_at',
    align: 'center',
    sortable: true
  },
  {
    name: 'reportedAt',
    label: 'Reported Date',
    field: 'reportedAt',
    align: 'left'
  }
]

function organicReports() {
  return phishStore.phishReports[teamMember.value.pk] || []
}

function phishAssignments() {
  return phishStore.phishAssignments[teamMember.value.pk] || []
}

const phishAssignmentsReported = computed(() => 
  phishAssignments().filter(phish => phish.reported).length
)

function trainingAssignments() {
  return phishStore.trainingAssignments[teamMember.value.pk] || []
}

const trainingAssignmentsCompleted = computed(() =>
  trainingAssignments().filter(assignment => assignment.completed).length
)

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

async function loadTeamMemberData() {
  loading.value = true
  try {
    const employeePk = Number(route.params.pk)
    
    peopleStore.getSimpleEmployeeDetail({pk: employeePk}).then(member => {
      teamMember.value = {
        pk: member.pk,
        employeeName: member.name,
        riskLevel: 'med', // Default risk level - replace with actual data
        groups: member.groups || []
      }
    })

    // Load all reports for this employee
    await phishStore.getReportsForEmployee(employeePk)
    await phishStore.getPhishAssignmentsForEmployee(employeePk)
    await phishStore.getTrainingAssignmentsForEmployee(employeePk)
    
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/phish/admin/team')
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

function reassignResource(assignment: TrainingAssignment) {
  console.log('Reassigning training:', assignment)
  // TODO: API call to mark training reassigned
  // After API call succeeds, refresh the training assignments
  loadTeamMemberData()
}

function createPhishAssignment() {
  if (!selectedPhishTemplate.value) {
    console.error('No template selected for synthetic phish')
    return
  }
  phishStore.createPhishAssignment(
    teamMember.value.pk, selectedPhishTemplate.value.pk
  )
    .then(() => {
      // Refresh synthetic tests list after sending
      loadTeamMemberData()
    })
    .catch((e) => {
      console.error('Error sending synthetic phish:', e)
    })
}

function createTrainingAssignment() {
  if (!selectedTrainingTemplate.value) {
    console.error('No template selected for training assignment')
    return
  }
  phishStore.createTrainingAssignment(
    teamMember.value.pk, selectedTrainingTemplate.value.pk
  )
    .then(() => {
      // Refresh educational resources list after assigning
      loadTeamMemberData()
    })
    .catch((e) => {
      console.error('Error assigning training:', e)
    })
}

onMounted(() => {
  loadTeamMemberData()
})
</script>

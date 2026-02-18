<template>
<q-page class="q-pa-md">
  <div class="text-h4">Team</div>
  <div class="q-mt-md">
    <q-table
      :rows="teamMembers"
      :columns="columns"
      :filter="tableFilter"
      :filter-method="tableFilterMethod"
      row-key="pk"
      :pagination="pagination"
      @row-click="onRowClick"
      flat
      :loading="loading"
    >
      <template v-slot:top-right>
        <q-input
          borderless
          dense
          clearable
          debounce="300"
          v-model="tableFilter"
          placeholder="Filter by name"
        >
          <template v-slot:prepend>
            <q-icon name="search">
              <q-tooltip>
                Filter by employee name
              </q-tooltip>
            </q-icon>
          </template>
        </q-input>
      </template>
      
      <template v-slot:body-cell-riskLevel="props">
        <q-td key="riskLevel" :props="props">
          <q-badge 
            :color="getRiskColor(props.row.riskLevel)" 
            :label="props.row.riskLevel"
          />
        </q-td>
      </template>
      
      <template v-slot:body-cell-phishAssignments="props">
        <q-td key="phishAssignments" :props="props">
          <q-badge 
            :color="getSyntheticPhishColor(props.row)" 
            :label="`${calculatePercentage(
              props.row.syntheticReported, props.row.syntheticReceived
            )}%`"
            text-color="white"
          />
          <span class="q-ml-xs text-grey-7">
            ({{ props.row.syntheticReported }} /
            {{ props.row.syntheticReceived }})
          </span>
        </q-td>
      </template>
      
      <template v-slot:body-cell-educationalResources="props">
        <q-td key="educationalResources" :props="props">
          <q-badge 
            :color="getEducationalResourceColor(props.row)" 
            :label="`${calculatePercentage(
              props.row.trainingCompleted, props.row.trainingAssigned
            )}%`"
            text-color="white"
          />
          <span class="q-ml-xs text-grey-7">
            ({{ props.row.trainingCompleted }} /
            {{ props.row.trainingAssigned }})
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</q-page>
</template>

<style lang="scss">
.q-table tbody tr {
  cursor: pointer;
}
</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { QTableProps } from 'quasar'
import { usePhishStore } from 'src/stores/phish'

const router = useRouter()
const phishStore = usePhishStore()

interface TeamMember {
  pk: number
  name: string
  riskLevel: 'low' | 'med' | 'high'
  phishReports: number
  syntheticReceived: number
  syntheticReported: number
  trainingAssigned: number
  trainingCompleted: number
}

const tableFilter = ref('')
const loading = ref(false)
const teamMembers = ref<TeamMember[]>([])

const columns: QTableProps['columns'] = [
  {
    name: 'name',
    label: 'Employee Name',
    field: 'name',
    align: 'left',
    sortable: true
  },
  {
    name: 'riskLevel',
    label: 'Risk Level',
    field: 'riskLevel',
    align: 'center',
    sortable: true,
    sort: (a: string, b: string) => {
      const riskOrder: { [key: string]: number } = { high: 3, med: 2, low: 1 }
      return riskOrder[a] - riskOrder[b]
    }
  },
  {
    name: 'phishReports',
    label: '# Organic Reports Made',
    field: 'phishReports',
    align: 'center',
    sortable: true
  },
  {
    name: 'phishAssignments',
    label: '# Synthetic Phishes Reported/Received',
    field: (row: TeamMember) =>
      calculatePercentage(row.syntheticReported, row.syntheticReceived),
    align: 'center',
    sortable: true,
    sort: (a: number, b: number) => a - b
  },
  {
    name: 'educationalResources',
    label: '# Educational Resources Completed/Assigned',
    field: (row: TeamMember) =>
      calculatePercentage(row.trainingCompleted, row.trainingAssigned),
    align: 'center',
    sortable: true,
    sort: (a: number, b: number) => a - b
  }
]

const pagination = ref({
  sortBy: 'riskLevel',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

function calculateRiskLevel(row: TeamMember): 'low' | 'med' | 'high' {
  // Calculate risk based on synthetic phish reporting rate
  const reportingRate = row.syntheticReceived > 0 
    ? (row.syntheticReported / row.syntheticReceived)
    : 0
  
  if (reportingRate >= 0.8) return 'low'
  if (reportingRate >= 0.5) return 'med'
  return 'high'
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

function calculatePercentage(completed: number, total: number): number {
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

function getAdaptiveColor(
  percentage: number, allPercentages: number[]
): string {
  // Filter out any invalid percentages
  const validPercentages = allPercentages.filter(p => !isNaN(p))
  
  if (validPercentages.length === 0) return 'grey-7'
  
  const minPercent = Math.min(...validPercentages)
  const maxPercent = Math.max(...validPercentages)
  
  // If all percentages are the same, use green
  if (minPercent === maxPercent) {
    return 'green-8'
  }
  
  // Calculate position in range (0 to 1)
  const position = (percentage - minPercent) / (maxPercent - minPercent)
  
  // Map to color gradient with accessible contrast
  // Using Quasar's color palette with good contrast against white text
  if (position <= 0.2) {
    return 'red-9'       // Darkest red for accessibility
  } else if (position <= 0.4) {
    return 'deep-orange-8'
  } else if (position <= 0.6) {
    return 'orange-8'
  } else if (position <= 0.8) {
    return 'light-green-8'
  } else {
    return 'green-9'     // Darkest green for accessibility
  }
}

function getSyntheticPhishColor(row: TeamMember): string {
  const percentage = calculatePercentage(
    row.syntheticReported, row.syntheticReceived
  )
  const allPercentages = teamMembers.value.map(m => 
    calculatePercentage(m.syntheticReported, m.syntheticReceived)
  )
  return getAdaptiveColor(percentage, allPercentages)
}

function getEducationalResourceColor(row: TeamMember): string {
  const percentage = calculatePercentage(
    row.trainingCompleted, row.trainingAssigned
  )
  const allPercentages = teamMembers.value.map(m => 
    calculatePercentage(m.trainingCompleted, m.trainingAssigned)
  )
  return getAdaptiveColor(percentage, allPercentages)
}

function tableFilterMethod(
  rows: readonly TeamMember[], term: string
): TeamMember[] {
  if (!term) {
    return rows as TeamMember[]
  }
  
  const lowerTerm = term.toLowerCase()
  return rows.filter(row => 
    row.name.toLowerCase().includes(lowerTerm)
  ) as TeamMember[]
}

function onRowClick(evt: Event, row: TeamMember): void {
  router.push({ path: `/phish/admin/team/${row.pk}` })
    .catch(e => {
      console.error('Error navigating to team member detail:', e)
    })
}

async function loadTeamStats() {
  loading.value = true
  try {
    const stats = await phishStore.getTeamStats()
    // Transform stats to match TeamMember interface
    teamMembers.value = stats.map((stat: any) => ({
      pk: stat.pk,
      name: stat.name,
      riskLevel: calculateRiskLevel({
        pk: stat.pk,
        name: stat.name,
        riskLevel: 'low' as const,
        phishReports: stat.phish_reports_count,
        syntheticReceived: stat.synthetic_phishes_sent,
        syntheticReported: stat.synthetic_phishes_reported,
        trainingAssigned: stat.training_assigned,
        trainingCompleted: stat.training_completed
      }),
      phishReports: stat.phish_reports_count,
      syntheticReceived: stat.synthetic_phishes_sent,
      syntheticReported: stat.synthetic_phishes_reported,
      trainingAssigned: stat.training_assigned,
      trainingCompleted: stat.training_completed
    }))
  } catch (error) {
    console.error('Error loading team stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTeamStats()
})
</script>

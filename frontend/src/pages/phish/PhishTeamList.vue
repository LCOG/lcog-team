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
      
      <template v-slot:body-cell-syntheticPhishes="props">
        <q-td key="syntheticPhishes" :props="props">
          {{ props.row.syntheticReported }} / {{ props.row.syntheticReceived }}
        </q-td>
      </template>
      
      <template v-slot:body-cell-educationalResources="props">
        <q-td key="educationalResources" :props="props">
          {{ props.row.resourcesCompleted }} / {{ props.row.resourcesAssigned }}
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { QTableProps } from 'quasar'

const router = useRouter()

interface TeamMember {
  pk: number
  employeeName: string
  riskLevel: 'low' | 'med' | 'high'
  organicReports: number
  syntheticReceived: number
  syntheticReported: number
  resourcesAssigned: number
  resourcesCompleted: number
}

const tableFilter = ref('')

const columns: QTableProps['columns'] = [
  {
    name: 'employeeName',
    label: 'Employee Name',
    field: 'employeeName',
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
    name: 'organicReports',
    label: '# Organic Reports Made',
    field: 'organicReports',
    align: 'center',
    sortable: true
  },
  {
    name: 'syntheticPhishes',
    label: '# Synthetic Phishes Reported/Received',
    field: (row: TeamMember) => `${row.syntheticReported}/${row.syntheticReceived}`,
    align: 'center',
    sortable: true,
    sort: (a: string, b: string, rowA: TeamMember, rowB: TeamMember) => {
      return rowA.syntheticReported - rowB.syntheticReported
    }
  },
  {
    name: 'educationalResources',
    label: '# Educational Resources Completed/Assigned',
    field: (row: TeamMember) => `${row.resourcesCompleted}/${row.resourcesAssigned}`,
    align: 'center',
    sortable: true,
    sort: (a: string, b: string, rowA: TeamMember, rowB: TeamMember) => {
      return rowA.resourcesCompleted - rowB.resourcesCompleted
    }
  }
]

const pagination = ref({
  sortBy: 'riskLevel',
  descending: true,
  page: 1,
  rowsPerPage: 10
})

// Dummy data - 5 team members
const teamMembers: TeamMember[] = [ 
  {
    pk: 5,
    employeeName: 'Dan Wilson',
    riskLevel: 'high',
    organicReports: 2,
    syntheticReceived: 15,
    syntheticReported: 8,
    resourcesAssigned: 10,
    resourcesCompleted: 4
  },
  {
    pk: 2,
    employeeName: 'Bob Smith',
    riskLevel: 'low',
    organicReports: 12,
    syntheticReceived: 10,
    syntheticReported: 10,
    resourcesAssigned: 8,
    resourcesCompleted: 8
  },
  {
    pk: 3,
    employeeName: 'Carol Williams',
    riskLevel: 'med',
    organicReports: 5,
    syntheticReceived: 12,
    syntheticReported: 9,
    resourcesAssigned: 6,
    resourcesCompleted: 5
  },
  {
    pk: 4,
    employeeName: 'David Brown',
    riskLevel: 'high',
    organicReports: 1,
    syntheticReceived: 18,
    syntheticReported: 5,
    resourcesAssigned: 12,
    resourcesCompleted: 3
  },
  {
    pk: 1,
    employeeName: 'Emma Davis',
    riskLevel: 'med',
    organicReports: 7,
    syntheticReceived: 14,
    syntheticReported: 11,
    resourcesAssigned: 9,
    resourcesCompleted: 7
  }
]

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

function tableFilterMethod(rows: readonly TeamMember[], term: string): TeamMember[] {
  if (!term) {
    return rows as TeamMember[]
  }
  
  const lowerTerm = term.toLowerCase()
  return rows.filter(row => 
    row.employeeName.toLowerCase().includes(lowerTerm)
  ) as TeamMember[]
}

function onRowClick(evt: Event, row: TeamMember): void {
  router.push({ path: `/phish/team/${row.pk}` })
    .catch(e => {
      console.error('Error navigating to team member detail:', e)
    })
}
</script>

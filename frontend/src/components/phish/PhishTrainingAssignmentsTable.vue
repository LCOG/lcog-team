<template>
  <q-table
    :rows="trainingAssignments"
    :columns="columns"
    row-key="pk"
    flat
    :pagination="{ rowsPerPage: 10 }"
  >
    <template v-slot:body-cell-completed="props">
      <q-td :props="props">
        <q-icon 
          :name="props.value ? 'check_circle' : 'cancel'" 
          :color="props.value ? 'positive' : 'negative'"
          size="sm"
        />
      </q-td>
    </template>

    <template v-slot:body-cell-assignedAt="props">
      <q-td :props="props">
        {{ formatDate(props.value) }}
      </q-td>
    </template>

    <template v-slot:body-cell-completedAt="props">
      <q-td :props="props">
        {{ props.value ? formatDate(props.value) : '-' }}
      </q-td>
    </template>

    <template v-slot:body-cell-actions="props">
      <q-td :props="props">
        <q-btn 
          v-if="!admin"
          flat 
          dense 
          :label="props.row.completed ? 'Review' : 'Begin'" 
          color="primary"
          @click="openAssignment(props.row)"
        />
        <q-btn 
          v-if="admin && props.row.completed"
          flat 
          dense 
          label="Reassign" 
          color="primary"
          @click="$emit('reassign', props.row)"
        />
      </q-td>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { QTableProps } from 'quasar'
import { TrainingAssignment } from 'src/types'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Props {
  trainingAssignments: TrainingAssignment[]
  admin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  admin: false
})

defineEmits<{
  (e: 'reassign', assignment: TrainingAssignment): void
}>()

const columns: QTableProps['columns'] = [ 
  {
    name: 'name',
    label: 'Name',
    field: 'training_name',
    align: 'left',
  },
  {
    name: 'assignedAt',
    label: 'Assigned',
    field: 'assigned_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'completed',
    label: 'Completed',
    field: 'completed',
    align: 'center',
    sortable: true
  },
  {
    name: 'completedAt',
    label: 'Completed Date',
    field: 'completed_at',
    align: 'left',
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

function openAssignment(assignment: TrainingAssignment) {
  router.push(`/phish/training/${assignment.pk}`)
}
</script>

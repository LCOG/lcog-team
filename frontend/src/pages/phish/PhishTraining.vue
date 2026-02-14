<template>
  <q-page class="q-pa-md">
    <q-spinner-grid
      v-if="loading"
      class="spinner q-mt-lg"
      color="primary"
      size="xl"
    />

    <div v-else-if="error" class="text-center q-mt-lg">
      <q-icon name="error" color="negative" size="xl" />
      <div class="text-h6 q-mt-md">{{ error }}</div>
      <q-btn
        flat
        label="Return to Dashboard"
        color="primary"
        @click="router.push({ name: 'phish-dashboard' })"
        class="q-mt-md"
      />
    </div>

    <div v-else-if="trainingAssignment">
      <!-- Header -->
      <div class="row items-center q-mb-md">
        <q-btn 
          flat 
          dense 
          round 
          icon="arrow_back" 
          @click="router.push({ name: 'phish-dashboard' })"
          class="q-mr-md"
        >
          <q-tooltip>Back to Dashboard</q-tooltip>
        </q-btn>
        <div class="text-h4">{{ trainingAssignment.template.name }}</div>
      </div>

      <!-- Completion badge if already completed -->
      <q-banner v-if="trainingAssignment.completed" class="bg-positive text-white q-mb-md" rounded>
        <template v-slot:avatar>
          <q-icon name="check_circle" size="md" />
        </template>
        <div class="text-subtitle1">
          Training completed on {{ formatDate(trainingAssignment.completed_at) }}
        </div>
      </q-banner>

      <!-- Training content card -->
      <q-card flat bordered class="q-mb-md">
        <q-card-section>
          <div 
            class="training-content"
            v-html="trainingAssignment.template.content"
          ></div>
        </q-card-section>
      </q-card>

      <!-- Certification button -->
      <div class="row justify-center q-mt-lg">
        <q-btn
          v-if="!trainingAssignment.completed"
          unelevated
          color="primary"
          size="lg"
          label="I certify that I have read this training"
          @click="completeTraining"
          :loading="completing"
          class="q-px-xl"
        />
        <q-btn
          v-else
          flat
          color="primary"
          label="Return to Dashboard"
          @click="router.push({ name: 'phish-dashboard' })"
        />
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.training-content {
  line-height: 1.6;
  font-size: 16px;
}

.training-content :deep(h1) {
  font-size: 2em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.training-content :deep(h2) {
  font-size: 1.5em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.training-content :deep(h3) {
  font-size: 1.25em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.training-content :deep(p) {
  margin-bottom: 1em;
}

.training-content :deep(ul),
.training-content :deep(ol) {
  margin-bottom: 1em;
  padding-left: 2em;
}

.training-content :deep(li) {
  margin-bottom: 0.5em;
}

.training-content :deep(img) {
  max-width: 100%;
  height: auto;
}

.training-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.training-content :deep(table td),
.training-content :deep(table th) {
  border: 1px solid #ddd;
  padding: 8px;
}

.training-content :deep(table th) {
  background-color: #f5f5f5;
  font-weight: bold;
}
</style>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useQuasar } from 'quasar'

import { usePhishStore } from 'src/stores/phish'
import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'
import { TrainingAssignment } from 'src/types'

const router = useRouter()
const route = useRoute()
const $q = useQuasar()
const phishStore = usePhishStore()
const userStore = useUserStore()

const loading = ref(true)
const completing = ref(false)
const error = ref<string | null>(null)
const trainingAssignment = ref<TrainingAssignment | null>(null)

function formatDate(date: Date | string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadTraining() {
  loading.value = true
  error.value = null

  try {
    // Make sure user is authenticated
    await getCurrentUser()
    
    const assignmentPk = Number(route.params.pk)
    if (!assignmentPk || isNaN(assignmentPk)) {
      error.value = 'Invalid training assignment'
      return
    }

    // Fetch the training assignment
    const assignment = await phishStore.getTrainingAssignment(assignmentPk)
    
    // Verify the current user is the assignee
    const currentEmployeePk = userStore.getEmployeeProfile.employee_pk
    if (assignment.employee.pk !== currentEmployeePk) {
      error.value = 'You do not have permission to view this training'
      return
    }

    trainingAssignment.value = assignment
  } catch (e) {
    console.error('Error loading training:', e)
    error.value = 'Failed to load training assignment'
  } finally {
    loading.value = false
  }
}

async function completeTraining() {
  if (!trainingAssignment.value) return

  completing.value = true
  
  try {
    await phishStore.completeTrainingAssignment(trainingAssignment.value.pk)
    
    $q.notify({
      type: 'positive',
      message: 'Training completed successfully',
      position: 'top'
    })

    // Redirect to dashboard
    router.push({ name: 'phish-dashboard' })
  } catch (e) {
    console.error('Error completing training:', e)
    $q.notify({
      type: 'negative',
      message: 'Failed to complete training. Please try again.',
      position: 'top'
    })
  } finally {
    completing.value = false
  }
}

onMounted(() => {
  loadTraining()
})
</script>

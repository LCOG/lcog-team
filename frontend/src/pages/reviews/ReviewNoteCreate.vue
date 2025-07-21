<template>
  <q-page>
    <div class="q-px-md">
      <h4 class="q-my-lg">Add Feedback</h4>
      <div v-if="employeeFullName">
        <p>You are invited to submit feedback for {{ employeeFullName }}’s upcoming performance evaluation.  Feel free to respond with freeform comments or answer the following questions.</p>
        <ol>
          <li>What in your judgement are {{ employeeFirstName }}’s strongest performance characteristics?</li>
          <li>Are there any characteristics of {{ employeeFirstName }}’s performance that need strengthening?</li>
          <li>Please share any additional feedback that you think would be helpful.</li>
        </ol>
    
        <p>Thank you for your contribution to supporting {{ employeeFirstName }}’s success at LCOG,</p>
      </div>
      <p class="text-bold">
        Notes are visible ONLY to you and the employee's manager. They are never visible to the employee, or to anyone else.
      </p>
      <EmployeeSelect
        name="employee"
        label="Employee"
        :employeePk="employeePkFromRoute()"
        :useLegalName="false"
        v-on:input="employee=$event"
        :readOnly=!!employeePkFromRoute()
        :fooBar="100"
      />
      <q-editor
        id="review-note-editor"
        v-model="note"
        :toolbar="editorToolbar"
        class="q-my-md"
      />
      <q-btn
        id="review-note-create-button"
        color="white"
        text-color="black"
        label="Create"
        :disabled="!formIsFilled()"
        @click="createReviewNote()"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { Notify, useQuasar } from 'quasar'
import { onMounted, ref, Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import EmployeeSelect from 'src/components/EmployeeSelect.vue'
import { usePeopleStore } from 'src/stores/people'
import { useReviewStore } from 'src/stores/review'
import { emptyEmployee, SimpleEmployee } from 'src/types'
import { getRouteQuery } from 'src/utils'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const peopleStore = usePeopleStore()
const reviewStore = useReviewStore()

// From route query
let employeeFullName = ref('')
let employeeFirstName = ref('')

// From form
let employee = ref(emptyEmployee) as Ref<SimpleEmployee>
let note = ref('')

let editorToolbar = [
  [
    {
      label: $q.lang.editor.align,
      icon: $q.iconSet.editor.align,
      fixedLabel: true,
      options: ['left', 'center', 'right', 'justify']
    }
  ],
  ['bold', 'italic', 'underline', 'removeFormat'],
  ['hr', 'link'],
  ['fullscreen'],
  ['quote', 'unordered', 'ordered', 'outdent', 'indent'],
  ['undo', 'redo']
]

function employeePkFromRoute() {
  const employeePk = getRouteQuery(route, 'employee')
  if (employeePk) {
    employee.value.pk = parseInt(employeePk)
    return parseInt(employeePk)
  }
  return undefined
}

function getEmployeeName(): void {
  const pk = employeePkFromRoute()
  if (pk) {
    peopleStore.getSimpleEmployeeDetail({ pk })
      .then((employee) => {
        employeeFullName.value = employee.name
        employeeFirstName.value = employee.name.split(' ')[0]
      })
      .catch(e => {
        console.error('Error getting employee:', e)
      })
  }
}

function formIsFilled(): boolean {
  if (employee.value.pk !== -1 && !!note.value) {
    return true
  } else {
    return false
  }
}

function createReviewNote(): void {
  reviewStore.createReviewNote({
    employee_pk: employee.value.pk,
    note: note.value,
  })
    .then(() => {
      router.push({ name: 'reviews' })
        .then(() => {
          Notify.create('Created a review note.')
        })
        .catch(e => {
          console.error(
            'Error navigating to dashboard after creating review note:', e
          )
        })
    })
    .catch(e => {
      console.error('Error creating review note:', e)
    })
}

onMounted(() => {
  getEmployeeName()
})
</script>

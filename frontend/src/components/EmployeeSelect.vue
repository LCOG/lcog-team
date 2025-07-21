<template>
<q-select
  class="employee-select"
  v-model="selectedEmployee"
  :options="employees()"
  option-value="pk"
  :option-label="selectOptionLabel()"
  :label="label"
  :readonly = "readOnly"
  use-input
  hide-selected
  fill-input
  input-debounce="500"
  @filter="filterFn"
  @update:model-value="emit('input', selectedEmployee)"
>
  <template v-slot:no-option>
    <q-item>
      <q-item-section class="text-grey">
        No results
      </q-item-section>
    </q-item>
  </template>
  <template v-if="!readOnly && selectedEmployeeName()" v-slot:append>
    <q-icon
      name="cancel"
      @click.stop="clearEmployee()"
      class="cursor-pointer"
    />
  </template>
</q-select>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref, Ref } from 'vue'

import { handlePromiseError } from 'src/stores'
import { usePeopleStore } from 'src/stores/people'
import { emptyEmployee, SimpleEmployee } from 'src/types'

const peopleStore = usePeopleStore()

const props = defineProps<{
  label: string,
  employee?: SimpleEmployee,
  employeePk?: number,
  useLegalName: boolean,
  readOnly: boolean,
  employeeFilterFn?: (employee: SimpleEmployee) => boolean
}>()

const emit = defineEmits<{
  (e: 'clear'): void
  (e: 'input', arg: SimpleEmployee): void
}>()

let needle = ref('') // For filtering employee list
let selectedEmployee: Ref<SimpleEmployee> = ref(emptyEmployee)

function selectOptionLabel(): string {
  if (props.useLegalName) {
    return 'legal_name'
  } else {
    return 'name'
  }
}

function selectedEmployeeName(): string {
  if (props.useLegalName) {
    return selectedEmployee.value?.legal_name
  } else {
    return selectedEmployee.value?.name
  }
}

function retrieveSimpleEmployeeList(): Promise<void> {
  return new Promise((resolve, reject) => {
    peopleStore.getSimpleEmployeeList()
      .then(() => {
        resolve()
      })
      .catch((e) => {
        handlePromiseError(reject, 'Error retrieving simple employee list', e)
      })
  })
}

function employees() {    
  let employeesList = peopleStore.simpleEmployeeList
  if (props.employeeFilterFn) {
    employeesList = employeesList.filter(props.employeeFilterFn)
  }
  return employeesList.filter((employee) => {
    if (props.useLegalName) {
      return employee.legal_name.toLowerCase().indexOf(needle.value) != -1
    } else {
      return employee.name.toLowerCase().indexOf(needle.value) != -1
    }
  })
}

function filterFn (val: string, update) {
  update(() => {
    needle.value = val.toLowerCase()
  })
}

function setEmployee() {
  if (props.employee) {
    selectedEmployee.value = props.employee
  }
  if (props.employeePk) {
    selectedEmployee.value = peopleStore.simpleEmployeeList.find(
      (employee) => employee.pk == props.employeePk
    ) || emptyEmployee
  }
}

function clearEmployee() {
  selectedEmployee.value = emptyEmployee
  emit('clear')
}

onMounted(() => {
  if (!employees().length) {
    retrieveSimpleEmployeeList().then(() => {
      setEmployee()
    })
  }
})

onUpdated(() => {
  setEmployee()
})
</script>

<template>
  <div class="q-py-sm">
    <q-table
      :rows="reviewStore.allReviewNotes"
      :columns="columns"
      row-key="name"
    >
      <template v-slot:body-cell-created_at="props">
        <q-td key="created_at" :props="props">
          {{ readableDateTimeNEW(props.row.created_at).split(' ')[0] }}
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense round flat color="grey" class="edit-note" @click="editNote(props)" icon="edit"></q-btn>
          <q-btn dense round flat color="grey" class="delete-note" @click="showDeleteDialog(props)" icon="delete"></q-btn>
        </q-td>
      </template>
      <template v-slot:bottom-row>
        <q-tr @click="clickAddNote()" class="cursor-pointer">
          <q-td colspan="100%">
            <q-icon name="addchart" size="md" class="q-pr-sm"/>Add a note
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="deleteDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="insert_chart_outlined" color="primary" text-color="white" />
            <span class="q-ml-sm">Are you sure you want to delete this note?</span>
          </div>
          <div class="row justify-center text-center">{{ deleteDialogEmployeeName }}</div>
          <div class="row justify-center text-center read-only-text-area" v-html="deleteDialogNoteText"></div>
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Yes, delete it" color="primary" @click="deleteRow()" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss">
.read-only-text-area {
  white-space: pre-line;
}
</style>

<script setup lang="ts">
import { Notify, QTable, QTableProps } from 'quasar'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { readableDateTimeNEW } from 'src/filters'
import { useReviewStore } from 'src/stores/review'
import { ReviewNoteRetrieve } from 'src/types'

interface QuasarReviewNoteTableRowClickActionProps {
  evt: MouseEvent;
  row: ReviewNoteRetrieve;
}

const router = useRouter()
const reviewStore = useReviewStore()

let columns: QTableProps['columns'] = [
  {
    name: 'employeeName', label: 'Colleague Name', align: 'left',
    field: 'employee_name', sortable: true
  },
  { name: 'created_at', label: 'Date', field: 'created_at', sortable: true },
  { name: 'actions', label: 'Actions', field: '' },
]
let deleteDialogVisible = ref(false)
let deleteDialogEmployeeName = ref('')
let deleteDialogNoteText = ref('')
let rowPkToDelete = ref(-1)

function editNote(props: QuasarReviewNoteTableRowClickActionProps): void {
  router.push(`/note/${ props.row.pk }`)
    .catch(e => {
      console.error('Error navigating to note detail', e)
    })
}

function showDeleteDialog(props: QuasarReviewNoteTableRowClickActionProps): void {
  rowPkToDelete.value = props.row.pk
  deleteDialogEmployeeName.value = props.row.employee_name
  deleteDialogNoteText.value = props.row.note
  deleteDialogVisible.value = true;
}

function deleteRow(): void {
  reviewStore.deleteReviewNote(rowPkToDelete.value)
    .then(() => {
      Notify.create('Deleted a review note.')
    })
}

function clickAddNote(): void {
  router.push({ name: 'note-create' })
    .catch(e => {
      console.error('Error navigating to new note page', e)
    })
}

onMounted(() => {
  reviewStore.getAllReviewNotes()
})
</script>

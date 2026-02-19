<template>
<q-select
  class="template-select"
  v-model="selectedTemplate"
  :options="templates()"
  option-value="pk"
  option-label="name"
  :label="label"
  :readonly = "readOnly"
  use-input
  hide-selected
  fill-input
  input-debounce="500"
  @filter="filterFn"
  @update:model-value="emit('input', selectedTemplate)"
>
  <template v-slot:no-option>
    <q-item>
      <q-item-section class="text-grey">
        No results
      </q-item-section>
    </q-item>
  </template>
  <template v-if="!readOnly && selectedTemplate?.name" v-slot:append>
    <q-icon
      name="cancel"
      @click.stop="clearTemplate()"
      class="cursor-pointer"
    />
  </template>
</q-select>
</template>

<script setup lang="ts">
import { onMounted, onUpdated, ref, Ref } from 'vue'

import { handlePromiseError } from 'src/stores'
import { usePhishStore } from 'src/stores/phish'
import { emptyPhishTemplate, SyntheticPhishTemplate } from 'src/types'

const phishStore = usePhishStore()

const props = defineProps<{
  label: string,
  template?: SyntheticPhishTemplate,
  templatePk?: number,
  readOnly: boolean,
  templateFilterFn?: (template: SyntheticPhishTemplate) => boolean
}>()

const emit = defineEmits<{
  (e: 'clear'): void
  (e: 'input', arg: SyntheticPhishTemplate): void
}>()

let needle = ref('') // For filtering template list
let selectedTemplate: Ref<SyntheticPhishTemplate> = ref(emptyPhishTemplate)

function retrievePhishTemplateList(): Promise<void> {
  return new Promise((resolve, reject) => {
    phishStore.getPhishTemplates()
      .then(() => {
        resolve()
      })
      .catch((e) => {
        handlePromiseError(reject, 'Error retrieving phish template list', e)
      })
  })
}

function templates() {    
  let templatesList = phishStore.phishTemplates
  if (props.templateFilterFn) {
    templatesList = templatesList.filter(props.templateFilterFn)
  }
  return templatesList.filter((template) => {
    return template.name.toLowerCase().indexOf(needle.value) != -1
  })
}

function filterFn(val: string, update) {
  update(() => {
    needle.value = val.toLowerCase()
  })
}

function setTemplate() {
  if (props.template) {
    selectedTemplate.value = props.template
  }
  if (props.templatePk) {
    selectedTemplate.value = phishStore.phishTemplates.find(
      (template) => template.pk == props.templatePk
    ) || emptyPhishTemplate
  }
}

function clearTemplate() {
  selectedTemplate.value = emptyPhishTemplate
  emit('clear')
}

onMounted(() => {
  if (!templates().length) {
    retrievePhishTemplateList().then(() => {
      setTemplate()
    })
  }
})

onUpdated(() => {
  setTemplate()
})
</script>

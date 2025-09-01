<template>
<q-page class="q-pa-md">
  <div v-html="message"></div>
  <form>
    <div class="row items-center q-gutter-sm" v-if="!hasViewedCurrentSecurityMessage()">
      <q-checkbox v-model="acknowledge" />
      <span>I acknowledge I have read and understood this notification</span>
    </div>
    <div class="row items-center q-gutter-sm">
      <q-btn v-if="!hasViewedCurrentSecurityMessage()" :disabled="!acknowledge" @click="submitAcknowledgement()">Submit</q-btn>
      <span class="thanks q-ml-sm q-mt-sm" :hidden="!hasViewedCurrentSecurityMessage()"><strong>Thank you! Your response has already been recorded.</strong></span>
    </div>
  </form>
</q-page>
</template>

<style scoped lang="scss">
.thanks {
    color: green;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useSecurityMessageStore } from 'src/stores/securitymessage'
import { useUserStore } from 'src/stores/user'

const securityMessageStore = useSecurityMessageStore()
const userStore = useUserStore()

let message = ref('')
let securityMessagePk = ref(-1)
let acknowledge = ref(false)

function currentUserPk(): number {
  return userStore.getEmployeeProfile.employee_pk
}

function hasViewedCurrentSecurityMessage(): boolean {
  return securityMessageStore.viewedLatestSecurityMessage
}

function retrieveLatestSecurityMessage(): void {
  securityMessageStore.getLatestSecurityMessage()
    .then(securityMessage => {
      message.value = securityMessage.content
    })
    .catch(e => {
      console.error('Error retrieving latest security message from API:', e)
    })
}

function submitAcknowledgement(): void {
  securityMessageStore.setViewedSecurityMessage({
    employee_pk: currentUserPk(), security_message_pk: securityMessagePk.value
  })
    .then(() => {
      securityMessageStore.getViewedLatestSecurityMessage()
        .catch(e => {
          console.error('Error getting viewed security message from store:', e)
        })
    })
    .catch(e => {
      console.error('Error marking security message as viewed:', e)
    })
}

onMounted(() => {
  retrieveLatestSecurityMessage()
})
</script>

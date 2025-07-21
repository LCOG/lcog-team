<template>
<q-page class="q-pa-md">
  <div class="row items-center justify-between">
    <div class="text-h4">Credit Card Expenses</div>
    <q-icon
      name="help"
      color="primary"
      size=48px
      class="cursor-pointer"
      @click="showHelp = true"
    />
  </div>
  <div class="q-my-md" v-if="hasMultipleRoles()">
    <q-btn-group rounded>
      <q-btn
        v-if="isExpenseSubmitter()"
        :to="{ name: 'submit-expenses' }"
        unelevated
        rounded
        color="primary"
        icon="book"
        :label="$q.screen.xs ? 'Submit' : 'Submit Expenses'"
      >
        <q-badge v-if="numEMsToResubmit()" rounded color="red" floating>
          {{ numEMsToResubmit() }}
        </q-badge>
      </q-btn> 
      <q-btn
        v-if="isExpenseApprover()"
        :to="{ name: 'approve-expenses' }"
        unelevated
        rounded
        color="primary"
        icon="bookmark_added"
        :label="$q.screen.xs ? 'Approve' : 'Approve Expenses'"
      >
        <q-badge v-if="numExpenseGLsToApprove()" rounded color="red" floating>
          {{ numExpenseGLsToApprove() }}
        </q-badge>
      </q-btn>
      <q-btn
        v-if="isDirector()"
        :to="{ name: 'director-approve-expenses' }"
        unelevated
        rounded
        color="primary"
        icon="library_add_check"
        label="Director Approve"
      >
        <q-badge
          v-if="numExpensesDirectorToApprove()"
          rounded
          color="red"
          floating
        >
          {{ numExpensesDirectorToApprove() }}
        </q-badge>
      </q-btn>
      <q-btn
        v-if="isFiscal()"
        :to="{ name: 'fiscal-approve-expenses' }"
        unelevated
        rounded
        color="primary"
        icon="library_add_check"
        label="Fiscal Approve"
      >
        <q-badge
          v-if="numExpensesFiscalToApprove()"
          rounded
          color="red"
          floating
        >
          {{ numExpensesFiscalToApprove() }}
        </q-badge>
      </q-btn>
    </q-btn-group>  
  </div>
  <div v-if="route.meta.allowMonthNav" class="q-gutter-md q-pt-sm">
    <q-btn @click="purchaseStore.setThisMonth()">This Month</q-btn>
    <q-btn-group>
      <q-btn
        color="secondary" icon="west" @click="purchaseStore.monthBackward()"
      />
      <q-btn
        color="secondary" icon="east" @click="purchaseStore.monthForward()"
      />
    </q-btn-group>
  </div>
  <div>
    <router-view />
  </div>
  <q-dialog v-model="showHelp">
    <q-card id="help-dialog">
      <q-card-section class="q-ma-lg">
        <div class="row items-center q-gutter-lg">
          <q-avatar
            icon="credit_card"
            size="60px"
            font-size="36px"
            color="primary"
            text-color="white"
          />
          <div class="text-h6">
            <div v-if="router.currentRoute.value.name == 'submit-expenses'">
              <div>1) Click "Get Started" to start a new month.</div>
              <div>2) Select a credit card statement from the dropdown.</div>
              <div>3) Enter expenses by clicking "New Expense".</div>
              <div>4) Once you're ready, click "Submit for Approval".</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name == 'approve-expenses'"
            >
              <div>1) Approve or deny all pending expenses.</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name?.toString()
                .indexOf('director-approve-expenses') != -1"
            >
              <div>1) Approve or deny all pending expense months.</div>
              <div>Note: there may be multiple people using the same card!</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name?.toString()
                .indexOf('fiscal-approve-expenses') != -1"
            >
              <div>1) Each month, upload bank statements.</div>
              <div>2) Approve or deny all pending expense months.</div>
              <div>Note: there may be multiple people using the same card!</div>
            </div>
            <div class="row justify-center">
              <q-btn
                class="q-mt-sm"
                color="primary"
                @click="router.push({ name: 'help-cc-expenses' })"
              >
                More help
              </q-btn>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</q-page>
</template>

<style scoped lang="scss">
#help-dialog {
  max-width: 700px;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { usePurchaseStore } from 'src/stores/purchase'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from 'src/stores/user'

const purchaseStore = usePurchaseStore()
const userStore = useUserStore()

const router = useRouter()
const route = useRoute()

let showHelp = ref(false)

function isExpenseSubmitter() {
  return userStore.isExpenseSubmitter
}

function isExpenseApprover() {
  return userStore.isExpenseApprover
}

function isDirector() {
  return userStore.isDivisionDirector
}

function isFiscal() {
  return userStore.isFiscal
}

function hasMultipleRoles(): boolean {
  let sum = 0
  if (userStore.isExpenseSubmitter) sum++
  if (userStore.isExpenseApprover) sum++
  if (userStore.isDivisionDirector) sum++
  if (userStore.isFiscal) sum++
  return sum > 1
}

function numEMsToResubmit(): number {
  return purchaseStore.numEMsToResubmit
}

function numExpenseGLsToApprove(): number {
  return purchaseStore.numExpenseGLsToApprove
}

function numExpensesDirectorToApprove(): number {
  return purchaseStore.numExpensesDirectorToApprove
}

function numExpensesFiscalToApprove(): number {
  return purchaseStore.numExpensesFiscalToApprove
}

onMounted(() => {
  purchaseStore.initializeDates()
  purchaseStore.getExpenseMonthLocks()
})

</script>

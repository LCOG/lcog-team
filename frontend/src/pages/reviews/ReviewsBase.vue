<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h4">Performance Reviews</div>
      <q-icon
        name="help"
        color="primary"
        size=48px
        class="cursor-pointer"
        @click="showHelp = true"
      />
    </div>
    <div v-if="userHasWorkflowRoles()">
      <router-view />
    </div>
    <q-dialog v-model="showHelp">
      <q-card id="help-dialog">
        <q-card-section class="q-ma-lg">
          <div class="row items-center q-gutter-xs">
            <q-avatar
              icon="assignment_ind"
              size="60px"
              font-size="36px"
              color="primary"
              text-color="white"
            />
            <div class="text-h6">
              <ul v-if="router.currentRoute.value.name == 'reviews-dashboard'">
                <li>View your next review by clicking the clipboard icon.</li>
                <li>Add or edit peer feedback for your colleagues' reviews.</li>
                <hr />
                <li>
                  MANAGERS: Reviews requiring your signature are at<br />
                  the top. View and complete reviews for direct reports<br />
                  in the "Current Reviews" section.
                </li>
              </ul>
              <ul
                v-else-if="router.currentRoute.value.name == 'reviews-complete'"
              >
                <li>View your past reviews by clicking the clipboard icon.</li>
                <hr />
                <li>
                  MANAGERS: View past reviews for direct reports<br />
                  in the "Complete Reviews" section.
                </li>
              </ul>
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
import { useRouter } from 'vue-router'

// import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
// const userStore = useUserStore()

let showHelp = ref(false)

function userHasWorkflowRoles() {
  // return userStore.getEmployeeProfile.workflow_roles.length > 0
  return true
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasWorkflowRoles()) {
        router.push({ name: 'dashboard' })
      }
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

</script>

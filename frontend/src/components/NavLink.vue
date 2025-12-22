<template>
  <q-item
    clickable
    :to="link"
    :id="id"
    v-if="isVisible()"
  >
    <q-item-section
      v-if="icon"
      avatar
    >
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useUserStore } from 'src/stores/user'

export default defineComponent({
  name: 'NavLink',
  props: {
    title: {
      type: String,
      required: true
    },
    link: {
      type: String,
      required: false,
      default: '#'
    },
    icon: {
      type: String,
      required: false,
      default: ''
    },
    id: {
      type: String,
      required: false
    },
    isManager: {
      type: Boolean,
      required: false,
      default: false
    },
    isISEmployee: {
      type: Boolean,
      required: false,
      default: false
    },
    isFiscalEmployee: {
      type: Boolean,
      required: false,
      default: false
    },
    eligibleForTeleworkApplicationOnly: {
      type: Boolean,
      required: false,
      default: false
    },
    hasWorkflowRoles: {
      type: Boolean,
      required: false,
      default: false
    },
    canViewExpenses: {
      type: Boolean,
      required: false,
      default: false
    },
    canViewPhish: {
      type: Boolean,
      required: false,
      default: false
    },
    canViewReviews: {
      type: Boolean,
      required: false,
      default: false
    },
    canViewMOWRoutes: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  methods: {
    isVisible (): boolean {
      const shouldNotViewBecauseNotManager =
        this.isManager && !this.userStore.getEmployeeProfile.is_manager
      const shouldNotViewBecauseNotISEmployee =
        this.isISEmployee && !this.userStore.getEmployeeProfile.is_is_employee
      const shouldNotViewBecauseNotFiscalEmployee =
        this.isFiscalEmployee &&
        !this.userStore.getEmployeeProfile.is_fiscal_employee
      const shouldNotViewBecauseNotEligibleForTeleworkApplication =
        this.eligibleForTeleworkApplicationOnly &&
        !this.userStore.getEmployeeProfile.is_eligible_for_telework_application
      const shouldNotViewBecauseNoWorkflowRoles =
        this.hasWorkflowRoles && !this.userStore.hasWorkflowRoles
      const shouldNotViewBecauseNoExpenseRoles = this.canViewExpenses && (
        !this.userStore.getEmployeeProfile.is_expense_submitter &&
        !this.userStore.getEmployeeProfile.is_expense_approver &&
        !this.userStore.getEmployeeProfile.is_division_director &&
        !this.userStore.getEmployeeProfile.is_fiscal_employee
      )
      const shouldNotViewBecauseNoPhishRole =
        this.canViewPhish &&
        !this.userStore.getEmployeeProfile.can_view_phish
      const shouldNotViewBecauseNoReviewRoles =
        this.canViewReviews &&
        !this.userStore.getEmployeeProfile.can_view_reviews
      const cannotViewMealsOnWheelsRoutes =
        this.canViewMOWRoutes &&
        !this.userStore.getEmployeeProfile.can_view_mow_routes
      if (
        shouldNotViewBecauseNotManager ||
        shouldNotViewBecauseNotISEmployee ||
        shouldNotViewBecauseNotFiscalEmployee ||
        shouldNotViewBecauseNotEligibleForTeleworkApplication ||
        shouldNotViewBecauseNoWorkflowRoles ||
        shouldNotViewBecauseNoExpenseRoles ||
        shouldNotViewBecauseNoPhishRole ||
        shouldNotViewBecauseNoReviewRoles ||
        cannotViewMealsOnWheelsRoutes
      ) {
        return false
      } else {
        return true
      }
    }
  },
  setup () {
    const userStore = useUserStore()

    return {
      userStore
    }
  }
})
</script>

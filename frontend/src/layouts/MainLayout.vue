<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          <div v-if="emplayeeName()">
            Hi {{ emplayeeName() }}
          </div>
        </q-toolbar-title>

        <q-btn flat no-caps :to="{ name: 'release-notes'}">
          {{ appVersionTag() }}
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
      :width="210"
    >
      <q-list>
        <q-item
          clickable
          :to="{ name: 'dashboard' }"
          v-if="isAuthenticated()"
        >
          <q-item-section avatar>
            <q-img
              id="lcog-logo"
              src="../assets/lcog-logo.png"
              style="width: 30px;"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>LCOG Team App</q-item-label>
          </q-item-section>
        </q-item>
        <q-item
          clickable
          @click='loginWithMicrosoft'
          v-if="!isAuthenticated()"
        >
          <q-item-section avatar>
            <q-img
              id="ms-logo"
              src="../assets/microsoft-logo.png"
              style="width: 24px;"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>Sign in with Microsoft</q-item-label>
          </q-item-section>
        </q-item>
        <div v-if="isAuthenticated()">
          <NavLink
            v-for="link in navLinks"
            :key="link.title"
            v-bind="link"
            :id="link.id"
          />
        </div>
        <q-item
          clickable
          @click='logout'
          v-if="isAuthenticated()"
        >
          <q-item-section avatar>
            <q-icon name='west' />
          </q-item-section>
          <q-item-section>
            <q-item-label>Log Out</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<style scoped lang="scss">
</style>

<script setup lang="ts">
import { Configuration } from 'electron-builder'
import { UserAgentApplication } from 'msal'
import { Notify } from 'quasar'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import NavLink from 'components/NavLink.vue'
import useEventBus from 'src/eventBus'
import { useAuthStore } from 'src/stores/auth'
import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'

const authStore = useAuthStore()
const userStore = useUserStore()
const router = useRouter()
const bus = useEventBus()

let leftDrawerOpen = ref(false)

interface LinkData {
  title: string
  icon: string
  link: string
  id?: string
  isManager?: boolean
  isISEmployee?: boolean
  isFiscalEmployee?: boolean
  eligibleForTeleworkApplicationOnly?: boolean
  hasWorkflowRoles?: boolean
  canViewExpenses?: boolean
  canViewReviews?: boolean
  canViewMOWRoutes?: boolean
}

const navLinks: Array<LinkData> = [
  {
    title: 'Time Off',
    icon: 'schedule',
    link: '/timeoff',
    id: 'nav-timeoff',
    isISEmployee: true
  },
  {
    title: 'Responsibilities',
    icon: 'hardware',
    link: '/responsibilities',
    id: 'nav-responsibilities',
    isISEmployee: true
  },
  {
    title: 'Workflows',
    icon: 'double_arrow',
    link: '/workflows',
    hasWorkflowRoles: true
  },
  {
    title: 'Credit Card Expenses',
    icon: 'credit_card',
    link: '/expenses',
    canViewExpenses: true
  },
  {
    title: 'Performance Reviews',
    icon: 'assignment_turned_in',
    link: '/reviews',
    canViewReviews: true
  },
  {
    title: 'Schaefers Desk Reservation',
    icon: 'laptop',
    link: '/desk-reservation/schaefers/1',
    id: 'nav-schaefers-desk-reservation',
  },
  {
    title: 'Meals on Wheels Map',
    icon: 'map',
    link: '/mow-map',
    id: 'nav-mow',
    canViewMOWRoutes: true
  },
  // {
  //   title: 'My Telework Application',
  //   icon: 'home_work',
  //   link: '/telework-application',
  //   eligibleForTeleworkApplicationOnly: true
  // },
  // {
  //   title: 'Telework Policy',
  //   icon: 'computer',
  //   link: '/telework'
  // },
  // {
  //   title: 'Security Message',
  //   icon: 'security',
  //   link: '/security-message'
  // },
  {
    title: 'Organization',
    icon: 'diversity_3',
    link: '/organization',
    id: 'nav-organization',
    isManager: true
  },
  {
    title: 'My Profile',
    icon: 'person',
    link: '/profile',
    id: 'nav-profile'
  },
]

// For msal.js Azure/AD SSO
const msalConfig: Configuration = {
  auth: {
    clientId: '2c4ec8a0-6be9-4c9c-a6b6-6a40392b8e3e',
    authority:
      'https://login.microsoftonline.com/9a80ddb7-1790-4782-a634-ef32f273169c',
    redirectUri: process.env.DASHBOARD_URL,
  },
  cache: {
    cacheLocation: 'sessionStorage', // Configures where cache will be stored
    storeAuthStateInCookie: false, // Set to true if having issues on IE11/Edge
  }
}

const myMSALObj = new UserAgentApplication(msalConfig)

const loginRequest = {
  scopes: ['openid', 'profile', 'User.Read']
}

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function appVersionTag() {
  return process.env.APP_VERSION_TAG
}

function isAuthenticated(): boolean {
  return authStore['isAuthenticated']
}

function emplayeeName(): string {
  return userStore['getEmployeeProfile'].name
}

// Configured with Microsoft Entra ID
function loginWithMicrosoft(): void {
  myMSALObj.loginPopup(loginRequest)
    .then(() => {
      if (myMSALObj.getAccount()) {
        let account = myMSALObj.getAccount()
        let firstName = account.name.split(' ')[1][0].toUpperCase() +
          account.name.split(' ')[1].substring(1).toLowerCase()
        let lastName = account.name.split(' ')[0][0].toUpperCase() +
          account.name.split(' ')[0].substring(1).toLowerCase()
        authStore.authWithMicrosoft({
          username: account.userName, firstName, lastName
        })
          .then(() => router.push('/'))
          .catch((err) => {
            console.log(err)
            // Show an alert
            Notify.create({
              message: 'Error logging in: ' + err.response.data.error,
              color: 'negative',
              position: 'top',
            })
          })
      }
    }).catch(function (error) {
        console.log(error)
    })
}

function logout() {
  authStore.authLogout()
    .then(() => {
      myMSALObj.logout()
    })
    .catch(e => {
      console.error('Error logging out', e)
    })
}

onMounted(() => {
  getCurrentUser().then(() => {
    bus.emit('gotUserProfile', Math.random())
  })
  .catch(e => {
    console.log(e)
  })
})

</script>

import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import { PhishReport, SyntheticPhish, SyntheticPhishTemplate } from 'src/types'

export const usePhishStore = defineStore('phish', {
  state: () => ({
    submittedReports: [] as Array<PhishReport>,
    processedReports: [] as Array<PhishReport>,
    phishTemplates: [] as Array<SyntheticPhishTemplate>,
    syntheticPhishes: {} as { [employeeId: number]: Array<SyntheticPhish> }
  }),

  getters: {},

  actions: {
    // Fetch all PhishReport objects from the Django API
    getReports() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/phishreport` })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.submittedReports = results.filter((r: PhishReport) => {
              return r.processed === false
            })
            this.processedReports = results.filter((r: PhishReport) => {
              return r.processed === true
            })
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting phish reports', e)
          })
      })
    },

    // Fetch all SyntheticPhish objects for a given employee
    getSyntheticPhishesForEmployee(employeeId: number) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/syntheticphish?employee=${ employeeId }` })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.syntheticPhishes[employeeId] = results
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting synthetic phishes', e)
          })
      })
    },

    // Mark one or more reports complete (moves them from submittedReports to processedReports)
    // Accepts an array of report ids or objects with `pk`/`id` properties.
    markReportsProcessed(reports: Array<number | { pk?: number; id?: number }>) {
      return new Promise((resolve, reject) => {
        const ids = reports.map(r => (typeof r === 'number' ? r : (r.pk ?? r.id)))
        // Find matching reports in submittedReports
        const toMove = this.submittedReports.filter((r: any) => ids.includes(r.pk ?? r.id))

        // Send PATCH requests to mark processed=true for each report
        const ops = toMove.map((r: any) => {
          const id = r.pk ?? r.id
          return axios({ url: `${ apiURL }api/v1/phishreport/${ id }`, method: 'PATCH', data: { processed: true } })
        })

        Promise.all(ops)
          .then(() => {
            // Update local state
            const moved = toMove.map((r: any) => ({ ...r, processed: true }))
            this.processedReports.push(...moved)
            this.submittedReports = this.submittedReports.filter((r: any) => !ids.includes(r.pk ?? r.id))
            resolve(moved)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error marking phish reports processed', e)
          })
      })
    },

    // Fetch all SyntheticPhishTemplate objects from the Django API
    getPhishTemplates() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/phishtemplate` })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.phishTemplates = results
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting phish templates', e)
          })
      })
    },

    sendSyntheticPhish(employeeId: number, templateId: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/syntheticphish`,
          method: 'POST',
          data: {
            employee: employeeId,
            template: templateId,
          }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error sending synthetic phish', e)
          })
      })
    }
  }
})

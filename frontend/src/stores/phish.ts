import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import { PhishReport } from 'src/types'

export const usePhishStore = defineStore('phish', {
  state: () => ({
    submittedReports: [] as Array<PhishReport>,
    processedReports: [] as Array<PhishReport>
  }),

  getters: {},

  actions: {
    // Fetch all PhishReport objects from the Django API
    getReports() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/phishreport` })
          .then(resp => {
            const results = resp.data.results || resp.data
            // We only want organic reports in submittedReports for now
            this.submittedReports = results.filter((r: PhishReport) => r.organic === true && r.processed === false)
            this.processedReports = results.filter((r: PhishReport) => r.organic === true && r.processed === true)
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting phish reports', e)
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

        // Send PATCH requests to mark organic=false for each report
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
    }
  }
})

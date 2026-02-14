import axios from 'axios'
import { create, get } from 'cypress/types/lodash'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import { PhishReport, SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment, TrainingTemplate } from 'src/types'

export const usePhishStore = defineStore('phish', {
  state: () => ({
    submittedReports: [] as Array<PhishReport>,
    processedReports: [] as Array<PhishReport>,
    phishTemplates: [] as Array<SyntheticPhishTemplate>,
    phishAssignments: {} as { [employeeId: number]: Array<SyntheticPhish> },
    trainingTemplates: [] as Array<TrainingTemplate>,
    trainingAssignments: {} as {
      [employeeId: number]: Array<TrainingAssignment>
    }
  }),

  getters: {},

actions: {
    // Fetch all PhishReport objects from the Django API
    getReports() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/phish-report` })
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
          return axios({ url: `${ apiURL }api/v1/phish-report/${ id }`, method: 'PATCH', data: { processed: true } })
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
        axios({ url: `${ apiURL }api/v1/phish-template` })
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

    createPhishAssignment(employeeId: number, templateId: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/phish-assignment`,
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
          handlePromiseError(reject, 'Error creating phish assignment', e)
        })
      })
    },

    // Fetch all SyntheticPhish objects for a given employee
    getPhishAssignmentsForEmployee(employeeId: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/phish-assignment?employee=${ employeeId }`
        })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.phishAssignments[employeeId] = results
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting phishe assignments', e)
          })
      })
    },

    getTrainingTemplates() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/training-template` })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.trainingTemplates = results
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting training templates', e)
          })
      })
    },

    createTrainingAssignment(employeeId: number, templateId: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/training-assignment`,
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
          handlePromiseError(reject, 'Error assigning training', e)
        })
      })
    },

    getTrainingAssignmentsForEmployee(employeeId: number) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/training-assignment?employee=${ employeeId }` })
          .then(resp => {
            const results = resp.data.results || resp.data
            this.trainingAssignments[employeeId] = results
            resolve(results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting training assignments', e)
          })
      })
    },

    getTrainingAssignment(assignmentId: number) {
      return new Promise<TrainingAssignment>((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/training-assignment/${ assignmentId }` })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting training assignment', e)
          })
      })
    },

    completeTrainingAssignment(assignmentId: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/training-assignment/${ assignmentId }`,
          method: 'PATCH',
          data: { completed: true }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error completing training assignment', e)
          })
      })
    }
  }
})
import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  PhishReport, SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment,
  TrainingTemplate
} from 'src/types'

export const usePhishStore = defineStore('phish', {

state: () => ({
  // Phish Admin Dashboard
  submittedReports: [] as Array<PhishReport>,
  processedReports: [] as Array<PhishReport>,
  
  phishReports: {} as { [employeeId: number]: Array<PhishReport> },
  phishTemplates: [] as Array<SyntheticPhishTemplate>,
  phishAssignments: {} as { [employeeId: number]: Array<SyntheticPhish> },
  trainingTemplates: [] as Array<TrainingTemplate>,
  trainingAssignments: {} as {
    [employeeId: number]: Array<TrainingAssignment>
  },
  teamStats: {} as {
    [employeePk: number]: {
      name: string
      riskLevel: 'low' | 'med' | 'high'
      organicReports: number
      syntheticReceived: number
      syntheticReported: number
      resourcesAssigned: number
      resourcesCompleted: number
    }
  }
}),

getters: {},

actions: {
  // Fetch all PhishReport objects from the Django API
  getAllReports() {
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

  getReportsForEmployee(employeeId: number) {
    return new Promise((resolve, reject) => {
      axios({
        url: `${ apiURL }api/v1/phishreport?employee=${ employeeId }`
      })
        .then(resp => {
          const results = resp.data.results || resp.data
          this.phishReports[employeeId] = results
          resolve(results)
        })
        .catch(e => {
          handlePromiseError(
            reject, 'Error getting phish reports for employee', e
          )
        })
    })
  },

  markReportVerdict(
    reportId: number, verdict: 'phish' | 'not_phish'
  ) {
    return new Promise((resolve, reject) => {
      let data = { status: verdict, processed: false }
      if (verdict === 'not_phish') {
        data = { status: verdict, processed: true }
      }
      axios({
        url: `${ apiURL }api/v1/phishreport/${ reportId }`,
        method: 'PATCH',
        data: data
      })
        .then(resp => {
          // Update local state
          const reportIndex = this.submittedReports.findIndex(
            (r: any) => (r.pk ?? r.id) === reportId
          )
          if (reportIndex !== -1) {
            const report = {
              ...this.submittedReports[reportIndex], status: verdict
            }
            this.submittedReports.splice(reportIndex, 1)
            this.processedReports.push(report)
          }
          resolve(resp.data)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error marking report verdict', e)
        })
    })
  },

  markReportProcessed(reportId: number) {
    return new Promise((resolve, reject) => {
      axios({
        url: `${ apiURL }api/v1/phishreport/${ reportId }`,
        method: 'PATCH',
        data: { processed: true }
      })
        .then(resp => {
          // Update local state
          const reportIndex = this.submittedReports.findIndex(
            (r: any) => (r.pk ?? r.id) === reportId
          )
          if (reportIndex !== -1) {
            const report = {
              ...this.submittedReports[reportIndex], processed: true
            }
            this.submittedReports.splice(reportIndex, 1)
            this.processedReports.push(report)
          }
          resolve(resp.data)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error marking report processed', e)
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
          handlePromiseError(reject, 'Error getting phish assignments', e)
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
      axios({
        url: `${ apiURL }api/v1/training-assignment?employee=${ employeeId }`
      })
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
    })  },

  getTeamStats() {
    return new Promise((resolve, reject) => {
      axios({ url: `${ apiURL }api/v1/phish-assignment/team_stats` })
        .then(resp => {
          const stats: any = {}
          const statsArray = resp.data.results || resp.data
          statsArray.forEach((employee: any) => {
            stats[employee.pk] = {
              name: employee.name,
              phishReports: employee.phish_reports_count,
              syntheticReceived: employee.synthetic_phishes_sent,
              syntheticReported: employee.synthetic_phishes_reported,
              trainingAssigned: employee.training_assigned,
              trainingCompleted: employee.training_completed
            }
          })
          this.teamStats = stats
          resolve(statsArray)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting team stats', e)
        })
    })  }
}
})
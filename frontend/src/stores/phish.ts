import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  PhishReport, PhishReportTask, PhishTask, SyntheticPhish,
  SyntheticPhishTemplate, TrainingAssignment, TrainingTemplate
} from 'src/types'

export const usePhishStore = defineStore('phish', {

state: () => ({
  // Phish Admin Dashboard
  submittedReports: [] as Array<PhishReport>,
  processedReports: [] as Array<PhishReport>,
  phishTasks: [] as Array<PhishTask>,
  reportTasks: {} as { [reportId: number]: Array<PhishReportTask> },
  
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

getters: {
  allPhishTasks: (state) => {
    return [...state.phishTasks].sort((a, b) => {
      if (a.order === b.order) {
        return a.name.localeCompare(b.name)
      }
      return a.order - b.order
    })
  },

  getReportTasks: (state) => {
    return (reportId: number): Array<PhishReportTask> => {
      return state.reportTasks[reportId] || []
    }
  }
},

actions: {
  getPhishTasks(forceRefresh = false) {
    return new Promise<Array<PhishTask>>((resolve, reject) => {
      if (!forceRefresh && this.phishTasks.length > 0) {
        resolve(this.phishTasks)
        return
      }

      axios({ url: `${ apiURL }api/v1/phishtask` })
        .then(resp => {
          const results = resp.data.results || resp.data
          this.phishTasks = results
          resolve(results)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting phish tasks', e)
        })
    })
  },

  getPhishReportTasks(reportId: number, forceRefresh = false) {
    return new Promise<Array<PhishReportTask>>((resolve, reject) => {
      if (!forceRefresh && this.reportTasks[reportId]) {
        resolve(this.reportTasks[reportId])
        return
      }

      axios({
        url: `${ apiURL }api/v1/phish-report-task?report=${ reportId }`
      })
        .then(resp => {
          const results = resp.data.results || resp.data
          this.reportTasks[reportId] = results
          resolve(results)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting phish report tasks', e)
        })
    })
  },

  createPhishReportTask(reportId: number, taskId: number) {
    return new Promise<PhishReportTask>((resolve, reject) => {
      axios({
        url: `${ apiURL }api/v1/phish-report-task`,
        method: 'POST',
        data: {
          report: reportId,
          task: taskId
        }
      })
        .then(resp => {
          const reportTask = resp.data
          const existingTasks = this.reportTasks[reportId] || []
          const hasTask = existingTasks.some(
            (item) => item.task_pk === taskId
          )

          if (hasTask) {
            this.reportTasks[reportId] = existingTasks.map(item => {
              if (item.task_pk === taskId) {
                return reportTask
              }
              return item
            })
          } else {
            this.reportTasks[reportId] = [...existingTasks, reportTask]
          }
          resolve(reportTask)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error creating phish report task', e)
        })
    })
  },

  deletePhishReportTask(reportTaskId: number, reportId: number) {
    return new Promise((resolve, reject) => {
      axios({
        url: `${ apiURL }api/v1/phish-report-task/${ reportTaskId }`,
        method: 'DELETE'
      })
        .then(() => {
          const existingTasks = this.reportTasks[reportId] || []
          this.reportTasks[reportId] = existingTasks.filter(
            (item) => item.pk !== reportTaskId
          )
          resolve(true)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error deleting phish report task', e)
        })
    })
  },

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
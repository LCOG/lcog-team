import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  EmployeeEmailRetrieve, EmployeeRetrieve, EmployeeUpdatePartial,
  SimpleEmployeeRetrieve, Title, Unit
} from 'src/types'

export const usePeopleStore = defineStore('people', {
  state: () => ({
    simpleEmployeeList: [] as Array<SimpleEmployeeRetrieve>,
    directReports: [] as Array<EmployeeRetrieve>,
    simpleEmployeeDetail: { pk: -1, name: '' } as SimpleEmployeeRetrieve,
    fullEmployeeDetail: {} as EmployeeRetrieve,
    employeeEmailList: [] as Array<string>,
    titleList: [] as Array<Title>,
    unitList: [] as Array<Unit>
  }),

  getters: {},

  actions: {
    // Simple list of all employees
    getSimpleEmployeeList() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/employee/simple_list`})
          .then(resp => {
            this.simpleEmployeeList = resp.data.sort(
              (a: SimpleEmployeeRetrieve, b: SimpleEmployeeRetrieve) => {
                if (a.name < b.name) return -1
                if (a.name > b.name) return 1
                return 0
              }
            )
            resolve('Successfully got simple employee list')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting simple employee list', e)
          })
      })
    },
    // Simple list of all employee emails
    getEmployeeEmailList() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/employee/email_list`})
          .then(resp => {
            this.employeeEmailList = resp.data.map(
              (e: EmployeeEmailRetrieve) => e.email
            )
            resolve('Successfully got employee email list')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting employee email list', e)
          })
      })
    },
    // Simple detail of one employee
    getSimpleEmployeeDetail(
      data: {pk: number}
    ): Promise<SimpleEmployeeRetrieve> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/employee/${ data.pk }/simple_detail`})
          .then(resp => {
            this.simpleEmployeeDetail = resp.data as SimpleEmployeeRetrieve
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting simple employee detail', e
            )
          })
      })
    },
    // Full detail of one employee
    getFullEmployeeDetail(data: {pk: number}): Promise<EmployeeRetrieve> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/employee/${ data.pk }`})
          .then(resp => {
            this.fullEmployeeDetail = resp.data as EmployeeRetrieve
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting full employee detail', e)
          })
      })
    },
    // Get employee direct reports
    getDirectReports(pk: number): Promise<Array<SimpleEmployeeRetrieve>> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/employee/${ pk }/direct_reports` })
          .then(resp => {
            this.directReports = resp.data
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting direct reports', e)
          })
      })
    },
    updatePartialEmployee(
      pk: string, data: EmployeeUpdatePartial
    ): Promise<EmployeeRetrieve> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/employee/${ pk }`,
          method: 'PATCH',
          data: data
        })
        .then(resp => {
          resolve(resp.data)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error updating employee', e)
        })
      })
    },
    getTitleList() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/jobtitle`})
        .then(resp => {
          this.titleList = resp.data.results.sort((a: Title, b: Title) => {
            if (a.name < b.name) { return -1 }
            if (a.name > b.name) { return 1 }
            return 0
          })
          resolve('Successfully got title list')
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting title list', e)
        })
      })
    },
    getUnitList() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/unit`})
        .then(resp => {
          this.unitList = resp.data.results
          resolve('Successfully got unit list')
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting unit list', e)
        })
      })
    },
    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    }
  }
})

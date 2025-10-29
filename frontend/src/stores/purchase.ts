import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  Expense, ExpenseCreate, ExpenseMonth, ExpenseMonthCreate, ExpenseMonthLock,
  ExpenseMonthLockCreate, ExpenseStatement, GL, SimpleEmployeeRetrieve
} from 'src/types'

export const usePurchaseStore = defineStore('purchase', {
  state: () => ({
    firstOfThisMonth: new Date(),
    firstOfSelectedMonth: new Date(),
    expenseMonths: [] as Array<ExpenseMonth>,
    selectedExpenseMonth: undefined as ExpenseMonth | undefined,
    expenseMonthLocks: [] as Array<ExpenseMonthLock>,
    myExpenses: [] as Array<Expense>,
    approvalExpenseGLs: [] as Array<GL>,
    directorExpenseMonths: {} as {
      [year: number]: {
        [month: number]: Array<ExpenseMonth>
      }
    },
    directorEMsDetails: [] as Array<ExpenseMonth>,
    fiscalExpenseMonths: {} as {
      [year: number]: {
        [month: number]: Array<ExpenseMonth>
      }
    },
    fiscalEMsDetails: [] as Array<ExpenseMonth>,
    
    expenseStatements: {} as {
      [year: number]: {
        [month: number]: Array<ExpenseStatement>
      }
    },
    expenseStatementDetails: [] as Array<ExpenseStatement>,
    
    numEMsToResubmit: 0,
    numExpenseGLsToApprove: 0,
    numExpensesDirectorToApprove: 0,
    numExpensesFiscalToApprove: 0
  }),

  getters: {
    dayInt: () => new Date().getDate(),
    monthInt: (state) => state.firstOfSelectedMonth.getMonth() + 1,
    yearInt: (state) => state.firstOfSelectedMonth.getFullYear(),
    monthDisplay: (state) => {
      const m = state.firstOfSelectedMonth.toLocaleDateString(
        'en-us', { month: 'long' }
      )
      const y = state.firstOfSelectedMonth.getFullYear()
      return `${m} ${y}`
    },
    expenseMonthLocked(): boolean {
      return this.expenseMonthLocks.some(eml => {
        return eml.month === this.monthInt && eml.year === this.yearInt
      })
    }
  },

  actions: {
    initializeDates() {
      const theFirst = new Date()
      theFirst.setDate(1)
      theFirst.setHours(0, 0, 0, 0)
      this.firstOfThisMonth = theFirst
      this.firstOfSelectedMonth = theFirst
    },
    monthBackward() {
      if (!this.firstOfSelectedMonth) return
      const m = this.firstOfSelectedMonth.getMonth()
      const y = this.firstOfSelectedMonth.getFullYear()
      this.firstOfSelectedMonth = m === 0
        ? new Date(y - 1, 11, 1)
        : new Date(y, m - 1, 1)
    },
    monthForward() {
      if (!this.firstOfSelectedMonth) return
      const m = this.firstOfSelectedMonth.getMonth()
      const y = this.firstOfSelectedMonth.getFullYear()
      this.firstOfSelectedMonth = m === 11
        ? new Date(y + 1, 0, 1)
        : new Date(y, m + 1, 1)
    },
    setThisMonth() {
      this.firstOfSelectedMonth = this.firstOfThisMonth
    },
    setMonth(month: number, year: number) {
      this.firstOfSelectedMonth = new Date(year, month - 1, 1)
    },
    getExpenseMonthLocks(): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-month-lock`
        })
          .then(resp => {
            this.expenseMonthLocks = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting expense month locks', e)
          })
      })
    },

    ////////////////
    /// Expenses ///
    ////////////////

    createExpense(data: ExpenseCreate): Promise<Expense> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/expense`, method: 'POST', data })
          .then((resp) => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating expense', e)
          })
      })
    },
    updateExpense(data: Expense): Promise<Expense> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense/${ data.pk }`, method: 'PUT', data
        })
          .then((resp) => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating expense', e)
          })
      })
    },
    deleteExpense(pk: number): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense/${ pk }`, method: 'DELETE'
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error deleting expense', e)
          })
      })
    },
    createExpenseMonth(data: ExpenseMonthCreate): Promise<ExpenseMonth> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/expense-month`, method: 'POST', data })
          .then((resp) => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating expense month', e)
          })
      })
    },

    //////////////////
    /// Statements ///
    //////////////////

    getExpenseStatements(
      yearInt: number, monthInt: number
    ): Promise<ExpenseStatement[]> {
      return new Promise((resolve, reject) => {
        const params = `?year=${ yearInt }&month=${ monthInt }`
        axios({
          url: `${ apiURL }api/v1/expense-statement${ params }`
        })
          .then(resp => {
            const statements: ExpenseStatement[] = resp.data.results
            if (!this.expenseStatements[yearInt]) {
              this.expenseStatements[yearInt] = {}
            }
            this.expenseStatements[yearInt][monthInt] = statements
            resolve(statements)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting expense statements', e)
          })
      })
    },

    getExpenseStatementDetails(
      yearInt: number | null = null, monthInt: number | null = null
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        let params = ''
        if (!!yearInt && !!monthInt) {
          params = `?year=${ yearInt }&month=${ monthInt }`
        }
        axios({
          url: `${ apiURL }api/v1/expense-statement${ params }`
        })
          .then(resp => {
            this.expenseStatements = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting expense statements', e)
          })
      })
    },

    deleteExpenseStatement(pk: number): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-statement/${ pk }`, method: 'DELETE'
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error deleting expense statement', e)
          })
      })
    },
    
    /////////////////
    /// Submitter ///
    /////////////////

    getExpenseMonths(
      yearInt: number | null = null, monthInt: number | null = null
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        let params = ''
        if (!!yearInt && !!monthInt) {
          params = `?year=${ yearInt }&month=${ monthInt }`
        }
        axios({
          url: `${ apiURL }api/v1/expense-month${ params }`
        })
          .then(resp => {
            let ems = resp.data.results as Array<ExpenseMonth>
            this.expenseMonths = ems
            if (!!yearInt && !!monthInt) {
              // Set active month: The first month that is not yet submitted
              // or has been denied.
              ems = ems.sort(
                (a: ExpenseMonth, b: ExpenseMonth) => {
                  if (a.year !== b.year) return a.year - b.year
                  return a.month - b.month
                }
              ).reverse()
              if (ems.length) {
                let activeMonth = ems[0]
                for (const em of ems) {
                  if ([
                      'draft', 'approver_denied', 'director_denied',
                      'fiscal_denied'
                    ].indexOf(em.status) != -1) {
                    activeMonth = em
                  }
                }
                this.setMonth(activeMonth.month, activeMonth.year)
              }
            }

            let expenses = [] as Array<Expense>
            let numRejectedEMs = 0
            for (const em of ems) {
              expenses = expenses.concat(em.expenses)
              if ([
                'approver_denied', 'director_denied', 'fiscal_denied'
              ].indexOf(em.status) != -1) {
                numRejectedEMs += 1
              }
            }
            this.numEMsToResubmit = numRejectedEMs
            this.myExpenses = expenses
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting expense months', e)
          })
      })
    },
    clearExpenseGLApprovals(pk: number): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense/${ pk }/clear_approvals`,
          method: 'PUT'
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error clearing GL approvals', e)
          })
      })
    },
    setExpenseMonthCard(
      pk: number, cardPk: number
    ): Promise<ExpenseMonth> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-month/${ pk }/set_card`,
          method: 'PUT',
          data: { cardPk: cardPk }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error setting expense month card', e)
          })
      })
    },
    submitExpenseMonth(
      data: {
        yearInt: number, monthInt: number, cardPK: number, note?: string,
        unsubmit?: boolean
      }
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-month/submit`,
          data: data,
          method: 'POST'
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              `Error ${ data['unsubmit'] ? 'un' : ''}submitting expense month`,
              e
            )
          })
      })
    },
    setDefaultSelectedExpenseMonth(): Promise<null> {
      return new Promise((resolve) => {
        this.selectedExpenseMonth = this.expenseMonths.find(em => {
          return em.month === this.monthInt && em.year === this.yearInt
        })
        resolve(null)
      })
    },
    setSelectedExpenseMonth(pk: number): Promise<null> {
      return new Promise((resolve) => {
        this.selectedExpenseMonth = this.expenseMonths.find(em => em.pk === pk)
        resolve(null)
      })
    },
    updateSelectedExpenseMonth(): Promise<null> {
      return new Promise((resolve) => {
        this.selectedExpenseMonth = this.expenseMonths.find(
          em => em.pk === this.selectedExpenseMonth?.pk
        )
        resolve(null)
      })
    },

    ////////////////
    /// Approver ///
    ////////////////

    getApprovalGLs(
      yearInt: number | null = null,
      monthInt: number | null = null
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        let params = '?approve=true'
        if (!!yearInt && !!monthInt) {
          params = `?year=${ yearInt }&month=${ monthInt }&approve=true`
        }
        axios({
          url: `${ apiURL }api/v1/expense-gl${ params }`
        })
          .then(resp => {
            const expGLs = resp.data.results as Array<GL>
            const expenseGLs = [] as Array<GL>
            let unapprovedGLs = [] as Array<GL>
            for (const gl of expGLs) {
              if (!gl.approved_at) {
                unapprovedGLs.push(gl)
              }
              expenseGLs.push(gl)
            }
            
            // Set active month: The first month that has unapproved GLs
            unapprovedGLs = unapprovedGLs.sort(
              (a: GL, b: GL) => {
                if (a.em_year !== b.em_year) return a.em_year - b.em_year
                return a.em_month - b.em_month
              }
            )
            if (unapprovedGLs.length > 0) {
              this.setMonth(unapprovedGLs[0].em_month, unapprovedGLs[0].em_year)
            }
            
            this.approvalExpenseGLs = expenseGLs
            this.numExpenseGLsToApprove = unapprovedGLs.length
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting approval expense GLs', e)
          })
      })
    },

    updateGL(
      pk: number,
      field: 'name' | 'date' | 'vendor' | 'gl',
      val: string | {
        'code': string, 'job': string, 'activity': string,
        'approver': SimpleEmployeeRetrieve
      }
    ): Promise<Expense> {
      // Approver updates an expense from a GL row
      const data = { field, val }
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-gl/${ pk }`, method: 'PUT', data
        })
          .then((resp) => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating expense GL', e)
          })
      })
    },

    approveGL(
      pk: number, approve: boolean, deny_note: string
    ): Promise<Expense> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-gl/${ pk }/approver_approve`,
          method: 'PUT',
          data: { approve, deny_note }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error approving expense', e)
          })
      })
    },

    /////////////////////////
    /// Division Director ///
    /////////////////////////

    getDirectorMonthEMs(
      yearInt: number, monthInt: number
    ): Promise<ExpenseMonth[]> {
      return new Promise((resolve, reject) => {
        const params = `?director=true&detail=false&year=${ yearInt }&month=${ monthInt }`
        axios({
          url: `${ apiURL }api/v1/expense-month${ params }`
        })
          .then(resp => {
            const ems: ExpenseMonth[] = resp.data.results
            if (!this.directorExpenseMonths[yearInt]) {
              this.directorExpenseMonths[yearInt] = {}
            }
            this.directorExpenseMonths[yearInt][monthInt] = ems
            resolve(ems)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting director expense months', e)
          })
      })
    },

    getDirectorEMDetail(
      expenseMonthPK: number | null = null
    ): Promise<ExpenseMonth[]> {
      return new Promise((resolve, reject) => {
        const params = `?director=true&detail=true&em=${ expenseMonthPK }`
        axios({
          url: `${ apiURL }api/v1/expense-month${ params }`
        })
          .then(resp => {
            const ems: ExpenseMonth[] = resp.data.results
            this.directorEMsDetails = ems
            resolve(ems)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting director EM detail', e)
          })
      })
    },

    //////////////
    /// Fiscal ///
    //////////////

    getFiscalMonthEMs(
      yearInt: number, monthInt: number
    ): Promise<ExpenseMonth[]> {
      return new Promise((resolve, reject) => {
        const params = `?fiscal=true&detail=false&year=${ yearInt }&month=${ monthInt }`
        axios({
          url: `${ apiURL }api/v1/expense-month${ params }`
        })
          .then(resp => {
            const ems: ExpenseMonth[] = resp.data.results
            
            // Set active month if any ems this month are unapproved.
            const emsFiscalToApprove = ems.filter(
              em => {
                return em.status == 'approver_approved'
              }
            )
            if (emsFiscalToApprove.length > 0) {
              this.setMonth(monthInt, yearInt)
            }
            
            if (!this.fiscalExpenseMonths[yearInt]) {
              this.fiscalExpenseMonths[yearInt] = {};
            }
            this.fiscalExpenseMonths[yearInt][monthInt] = ems;

            this.numExpensesFiscalToApprove = emsFiscalToApprove.length
            resolve(ems)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting fiscal expense months', e)
          })
      })
    },

    getFiscalEMDetail(
      expenseMonthPK: number | null = null
    ): Promise<ExpenseMonth[]> {
      return new Promise((resolve, reject) => {
        const params = `?fiscal=true&detail=true&em=${ expenseMonthPK }`
        axios({
          url: `${ apiURL }api/v1/expense-month${ params }`
        })
          .then(resp => {
            const ems: ExpenseMonth[] = resp.data.results
            this.fiscalEMsDetails = ems
            resolve(ems)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting fiscal EM detail', e)
          })
      })
    },

    approveExpenseMonth(
      pk: number, approve: boolean, deny_note?: string
    ): Promise<ExpenseMonth> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-month/${ pk }/fiscal_approve`,
          method: 'PUT',
          data: { approve, deny_note }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error approving expense month', e)
          })
      })
    },

    uploadExpenseStatement(
      yearInt: number, monthInt: number, file: File
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        const formData = new FormData()
        formData.append('year', yearInt.toString())
        formData.append('month', monthInt.toString())
        formData.append('statement', file)
        axios({
          url: `${ apiURL }api/v1/expense-statement`,
          method: 'POST',
          data: formData,
          headers: { 'Content-Type': 'multipart/form-data' }
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error uploading expense statements', e)
          })
      })
    },

    sendExpenseStatementNotifications(): Promise<null> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-statement/send_notifications`,
          method: 'GET'
        })
          .then(() => {
            resolve(null)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error sending expense statement notifications', e
            )
          })
      })
    },

    downloadReceipts(pk: number): Promise<ExpenseMonth> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/expense-month/${ pk }/download_receipts`,
          method: 'GET',
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error downloading receipts', e)
          })
      })
    },

    lockCurrentExpenseMonth(
      lock: boolean, data?: ExpenseMonthLockCreate
    ): Promise<null> {
      return new Promise((resolve, reject) => {
        if (lock) {
          axios({
            url: `${ apiURL }api/v1/expense-month-lock`,
            method: 'POST',
            data
          })
            .then(() => {
              resolve(null)
            })
            .catch(e => {
              handlePromiseError(reject, 'Error locking expense month', e)
            })
        } else {
          axios({
            url: `${ apiURL }api/v1/expense-month-lock/unlock`,
            method: 'DELETE',
            data
          })
            .then(() => {
              resolve(null)
            })
            .catch(e => {
              handlePromiseError(reject, 'Error unlocking expense month', e)
            })
        }
        
        
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

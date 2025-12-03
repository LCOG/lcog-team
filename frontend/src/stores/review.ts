import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import { useUserStore } from 'src/stores/user'
import {
  ReviewRetrieve, PerformanceReviewUpdate,
  PerformanceReviewUpdatePartial, ReviewNoteCreate, ReviewNoteRetrieve,
  ReviewNoteUpdate, SignatureCreate
} from 'src/types'


export const useReviewStore = defineStore('review', {
  state: () => ({
    // Your next PR
    myNextPR: {} as ReviewRetrieve,
    // The PR detail we're looking at
    currentPR: {} as ReviewRetrieve,
    // PRs requiring your signature
    signaturePRs: [] as Array<ReviewRetrieve>,
    // Incomplete PRs for your direct reports
    incompletePRs: [] as Array<ReviewRetrieve>,
    // Complete PRs for your direct reports
    completePRs: [] as Array<ReviewRetrieve>,
    // All PRs for a given employee
    employeePRs: [] as Array<ReviewRetrieve>,
    allReviewNotes: [] as Array<ReviewNoteRetrieve>
  }),

  getters: {},

  actions: {

    /////////////////////////
    // Performance Reviews //
    /////////////////////////

    getMyNextPR(employeePk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/employee/${ employeePk }/` +
            'employee_next_performance_review'
        })
          .then(resp => {
            this.myNextPR = resp.data
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting next performance review', e
            )
          })
      })
    },

    getCurrentPR(pk: string): Promise<ReviewRetrieve> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/review/${ pk }` })
          .then(resp => {
            this.currentPR = resp.data
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting performance review', e)
          })
      })
    },

    getSignaturePRs() {
      return new Promise((resolve, reject) => {
        axios(
          { url: `${ apiURL }api/v1/review?signature=True` }
        )
          .then(resp => {
            this.signaturePRs = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting signature reviews', e
            )
          })
      })
    },

    getIncompletePRs(managerPk: number) {
      return new Promise((resolve, reject) => {
        axios(
          { url: `${ apiURL }api/v1/review?incomplete=True&manager=${ managerPk }` }
        )
          .then(resp => {
            this.incompletePRs = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting incomplete reviews', e
            )
          })
      })
    },

    getCompletePRs(managerPk: number) {
      return new Promise((resolve, reject) => {
        axios(
          { url: `${ apiURL }api/v1/review?complete=True&manager=${ managerPk }` }
        )
          .then(resp => {
            this.completePRs = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting complete reviews', e
            )
          })
      })
    },

    getEmployeePRs(employeePk: number) {
      // Get all performance reviews (past and present) for an employee
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/review?employee=${ employeePk }`
        })
          .then(resp => {
            this.employeePRs = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting all employee performance reviews', e
            )
          })
      })
    },

    updatePerformanceReview(pk: string, pr: PerformanceReviewUpdate): Promise<ReviewRetrieve> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/review/${ pk }`,
          data: pr,
          method: 'PUT'
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating performance review', e)
          })
      })
    },

    updatePerformanceReviewPartial(pk: string, pr: PerformanceReviewUpdatePartial): Promise<ReviewRetrieve> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/review/${ pk }`,
          data: pr,
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating performance review partial', e)
          })
      })
    },

    createSignature(signature: SignatureCreate) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/signature`, data: signature, method: 'POST'
        })
          .then(() => {
            resolve('Successfully created a signature')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating a signature', e)
          })
      })
    },

    uploadSignedPositionDescription(formData: FormData) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/fileupload`,
          data: formData,
          method: 'POST'
        })
          .then(() => {
            resolve('Successfully uploaded signed position description')
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error uploading signed position description', e
            )
          })
      })
    },

    //////////////////
    // Review Notes //
    //////////////////

    createReviewNote(reviewNote: ReviewNoteCreate) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/reviewnote`,
          data: reviewNote,
          method: 'POST'
        })
          .then(() => {
            this.getAllReviewNotes()
              .then(() => {
                const userStore = useUserStore()
                userStore.userRequest()
                  .then(() => {
                    resolve('Successfully created a review note')
                  })
                  .catch(err => console.log(err))
              })
              .catch(e => {
                handlePromiseError(
                  reject,
                  'Error getting all review notes ater creating a review note',
                  e
                )
              })
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating a review note', e)
          })
      })
    },

    getReviewNote(pk: string): Promise<ReviewNoteRetrieve> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/reviewnote/${ pk }` })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting all review notes', e)
          })
      })
    },

    getAllReviewNotes(): Promise<Array<ReviewNoteRetrieve>> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/reviewnote` })
          .then(resp => {
            this.allReviewNotes = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting all review notes', e)
          })
      })
    },

    getAllRecentNotesForEmployee(pk: string): Promise<Array<ReviewNoteRetrieve>> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/reviewnote/${pk}/notes_for_employee` })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting all manager notes for employee', e
            )
          })
      })
    },

    updateReviewNote(reviewNote: ReviewNoteUpdate): Promise<ReviewNoteRetrieve> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/reviewnote/${ reviewNote.pk }`,
          data: reviewNote,
          method: 'PUT'
        })
          .then((resp) => {
            this.getAllReviewNotes()
              .then(() => {
                resolve(resp.data)
              })
              .catch(e => {
                handlePromiseError(
                  reject,
                  'Error getting all review notes ater updating a review note',
                  e
                )
              })
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating a review note', e)
          })
      })
    },

    deleteReviewNote(pk: number) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/reviewnote/${ pk }`, method: 'DELETE' })
          .then(() => {
            this.getAllReviewNotes()
              .then(() => {
                resolve('Successfully deleted a review note')
              })
              .catch(e => {
                handlePromiseError(
                  reject,
                  'Error getting all review notes after deleting a review note',
                  e
                )
              })
          })
          .catch(e => {
            handlePromiseError(reject, 'Error deleting a review note', e)
          })
      })
    },

    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    },
  }
})

<template>
  <q-page class="q-mt-xs" id="schaefers-2-page">
    <div class="row justify-between items-center">
      <div class="row items-center q-ml-sm">
          <q-btn-group push class="">
            <q-btn push color="primary" glossy label="1F" :to="{ name: 'schaefers-1' }" />
            <q-btn push color="secondary" glossy label="2F" :to="{ name: 'schaefers-2' }" />
            <q-btn push color="primary" glossy label="3F" :to="{ name: 'schaefers-3' }"  />
          </q-btn-group>
        </div>
      <div class="row items-center q-gutter-md">
        <q-icon name="help" color="primary" size=48px class="cursor-pointer" @click="showHelp()" />
        <q-select class="" v-model="selectedEmployee" :options="employees()" option-value="pk" option-label="name" label="Select your name" use-input hide-selected fill-input input-debounce="500" @filter="filterFn">
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey">
                No results
              </q-item-section>
            </q-item>
          </template>
          <template v-if="selectedEmployee.name" v-slot:append>
            <q-icon name="cancel" @click.stop="selectedEmployee = emptyEmployee" class="cursor-pointer" />
          </template>
        </q-select>
        <q-btn
          color="primary"
          :disabled="!canReserve()"
          @click="clickReserve()"
        >
          Reserve
          <q-tooltip
            v-if="!allowReservations"
            class="bg-warning text-black text-body2"
          >
            Reservations only available between 6AM and 5PM
          </q-tooltip>
        </q-btn>
      </div>
      <div class="row q-pa-xs" id="legend">
        <div class="col">
          <div class="row justify-center text-uppercase">Legend</div>
          <div class="row items-center q-gutter-md q-mr-sm">
            <div class="row items-center q-gutter-sm">
              <div>Drop-In</div>
              <div id="drop-in-key"></div>
            </div>
            <div class="row items-center q-gutter-sm">
              <div>Lead Drop-In</div>
              <div id="lead-drop-in-key"></div>
            </div>
            <div class="row items-center q-gutter-sm">
              <div>Ergonomic Work Station</div>
              <q-img :src=ErgoDeskImg width=35px />
            </div>
            <div class="row items-center q-gutter-sm">
              <div>Held</div>
              <div>*</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row q-gutter-md q-mt-xs">
      <FloorPlan class="floor-plan"/>
    </div>

    <!-- Dialog to cancel a reservation -->
    <q-dialog v-model="cancelDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="no_meeting_room" color="primary" text-color="white" />
            <span class="q-ml-sm"><strong>{{ selectedDeskOccupantToCancel }}</strong> checked in to desk <strong>{{ selectedDeskNumberToCancel }}</strong> at <strong>{{ selectedDeskToCancelCheckInTime }}</strong>. End this reservation?</span>
          </div>
        </q-card-section>
        <q-card-actions class="row justify-around">
          <q-btn flat label="No" color="primary" v-close-popup />
          <q-btn flat label="Yes, end reservation" color="primary" @click="deleteReservation(selectedDeskReservationToCancelPk)" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dialog to confirm moving a reservation -->
    <q-dialog v-model="moveReservationDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="no_meeting_room" color="primary" text-color="white" />
            <span class="q-ml-sm"><strong>{{ selectedEmployee.name }}</strong> has a reservation at <span v-for="(reservation, index) in activeUserReservations" :key="reservation.pk"><span v-if="index != 0"> and </span>desk <strong>{{ reservation.desk_number }}</strong></span>. Cancel this existing reservation and make a new one?</span>
          </div>
        </q-card-section>
        <q-card-actions class="row justify-around">
          <q-btn flat label="No" color="primary" v-close-popup />
          <q-btn flat label="Yes, move reservation" color="primary" @click="moveReservation()" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<style lang="scss"> 
  .floor-plan {
    width: 100%;
  }
  
  #legend {
    border: 2px black solid;
  }
  
  #drop-in-key {
    width: 35px;
    height: 35px;
    background-color: yellow;
    border: 1px black solid;
    text-align: center;
  }
  
  #lead-drop-in-key {
    width: 35px;
    height: 35px;
    background-color: orange;
    border: 1px black solid;
    text-align: center;
  }
  
  .desk-buttom-number {
    font-size: 20px;
  }

  .desk-button-ergo {
    width: 35px;
  }

  .annotation {
    position: absolute;
    background: white;
    font-size: 8px;
    text-align: center;
  }
  .annotation button {
    font-size: 10px;
  }

  .highlight {
    position: absolute;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    border: 5px solid red;
  }
</style>

<script setup lang="ts">
import { Notify, QSelect } from 'quasar'
import { onMounted, onUnmounted, ref, Ref } from 'vue'
import { useRoute } from 'vue-router'

import ErgoDeskImg from 'src/assets/floorPlans/desk-ergo.png'
import StandardDeskImg from 'src/assets/floorPlans/desk-standard.png'
import FloorPlan from 'src/assets/floorPlans/schaefers2.svg'
import useEventBus from 'src/eventBus'
import { useDeskReservationStore } from 'src/stores/deskreservation'
import { usePeopleStore } from 'src/stores/people'
import { Desk, DeskReservation, SimpleEmployeeRetrieve } from 'src/types'
import { getRouteParam } from 'src/utils'

const deskReservationStore = useDeskReservationStore()
const peopleStore = usePeopleStore()
const route = useRoute()
const bus = useEventBus()

let needle = ref('') // For filtering employee list

const ignoreList = ['UP', 'DOWN', 'DN', 'DF', 'FE']

const BUILDING = 'S'
const FLOOR = '2'
let desks = ref([]) as Ref<Array<Desk>>
let deskReservations = ref([]) as Ref<Array<DeskReservation>>

let highlightedDeskNumber = ref('')
const deskNumber = getRouteParam(route, 'deskNumber')
if (deskNumber) {
  highlightedDeskNumber.value = deskNumber
}
  
let highlightedDeskNumberX = ref(0)
let highlightedDeskNumberY = ref(0)

const emptyEmployee = {name: '', pk: -1}

let allowReservations = ref(true)
let moveReservationDialogVisible = ref(false)
let activeUserReservations = ref([]) as Ref<Array<DeskReservation>>
let selectedEmployee = ref(emptyEmployee)
let selectedDeskNumber = ref('')

let cancelDialogVisible = ref(false)
let selectedDeskReservationToCancelPk = ref(-1)
let selectedDeskNumberToCancel = ref('')
let selectedDeskOccupantToCancel = ref('')
let selectedDeskToCancelCheckInTime = ref('')

// TODO: Use Quasar colors
const primaryColor = '#1976d2'
const greyColor = '#767676'
const blackColor = '#000000'
const redColor = 'red'
const yellowColor = 'yellow'
const orangeColor = 'orange'

///////////////
// EMPLOYEES //
///////////////
function employees(): Array<SimpleEmployeeRetrieve> {    
  const employees = peopleStore.simpleEmployeeList
  return employees.filter((employee) => {
    return employee.name.toLowerCase().indexOf(needle.value) != -1
  })
}

function retrieveSimpleEmployeeList(): void {
  peopleStore.getSimpleEmployeeList()
    .catch(e => {
      console.error('Error retrieving simple employee list', e)
    })
}

function filterFn (val: string, update: (callbackFn: () => void, afterFn?: (ref: QSelect) => void) => void) {
  update(() => {
    needle.value = val.toLowerCase()
  })
}

function deselectAllRoomButtons() {
  Array.from(document.getElementsByClassName('desk-button') as HTMLCollectionOf<HTMLElement>).forEach(room => {
    if (!room.classList.contains('reserved')) {
      room.style.borderColor = greyColor
      room.style.color = blackColor
    }
  })
}

function roomClick(roomButton: HTMLElement) {
  if (roomButton.dataset.pk) {
    const buttonNumber = roomButton.dataset.pk
    if (buttonNumber == selectedDeskNumber.value) {
      // Deselect the room
      selectedDeskNumber.value = ''
      roomButton.style.borderColor = greyColor
      roomButton.style.color = blackColor
    } else {
      // Select the room (and deselect others)
      selectedDeskNumber.value = buttonNumber
      deselectAllRoomButtons()
      roomButton.style.borderColor = primaryColor
      roomButton.style.color = primaryColor
    }
  }
}

function reservedRoomClick(roomButton: HTMLElement) {
  if (roomButton.dataset.pk) {
    const buttonNumber = roomButton.dataset.pk
    selectedDeskNumberToCancel.value = buttonNumber
    const currentDeskReservation = deskReservations.value.filter(
      deskReservation => deskReservation.desk_number == buttonNumber
    )[0]
    selectedDeskReservationToCancelPk.value = currentDeskReservation.pk
    selectedDeskOccupantToCancel.value = currentDeskReservation.employee_name
    const checkInDate = new Date(currentDeskReservation.check_in)
    selectedDeskToCancelCheckInTime.value = checkInDate.toLocaleTimeString(
      'en-US', { hour: 'numeric', minute: 'numeric' }
    )

    // Open reservation cancel dialog
    cancelDialogVisible.value = true
  }
}

function deleteReservation(pk: number) {
  deskReservationStore.cancelReservation(pk)
    .then(() => {
      if (selectedDeskNumberToCancel.value) {
        Notify.create(
          {message: `Canceled reservation of desk ${selectedDeskNumberToCancel.value} for ${selectedDeskOccupantToCancel.value}`}
        )
      }
      selectedDeskReservationToCancelPk.value = -1
      selectedDeskNumberToCancel.value = ''
      selectedDeskOccupantToCancel.value = ''

      // TODO: Temporarily restoring to remove sockets for production
      initDeskReservations()
        .then(() => {
          handleSVG()
        })
        .catch(e => {
          console.error('Error initializing desk reservations:', e)
        })
      
      // Update reserved desks list everywhere with WebSocket
      // this.deskReservationSocket.send(
      //   JSON.stringify({
      //     'message': `Reserved desk ${response.data.desk_number} for ${response.data.employee_name}`
      //   })
      // )
    })
    .catch(e => {
      console.error('Error cancelling desk reservation:' ,e)
    })
}

function canReserve() {
  return selectedEmployee.value.pk != -1 && selectedDeskNumber.value != '' &&
    allowReservations.value
}

function clickReserve() {
  // Before we reserve the desk, ensure the user does not have any active
  // reservations. If so, offer to move them.
  initDeskReservations() // Get latest desk reservations in case they changed since page load
    .then(() => {
      const currentReservations = deskReservations.value
        .filter(desk => desk.employee_pk == selectedEmployee.value.pk)
      if (currentReservations.length) {
        activeUserReservations.value = currentReservations
        moveReservationDialogVisible.value = true
      } else {
        reserveDesk()
      }
    })
    .catch(e => {
      console.error('Error initializing desk reservations:', e)
    })
}

function moveReservation() {
  // Cancel all existing reservations and make the new one.
  for (let i=0; i<activeUserReservations.value.length; i++) {
    deleteReservation(activeUserReservations.value[i].pk)
  }
  reserveDesk()
}

function reserveDesk() {
  deskReservationStore.createReservation({
    employee_pk: selectedEmployee.value.pk,
    building: BUILDING,
    floor: FLOOR,
    desk_number: selectedDeskNumber.value
  })
    .then((reservation) => {
      selectedEmployee.value = emptyEmployee
      selectedDeskNumber.value = ''
      deselectAllRoomButtons()
      if (reservation.created) {
        Notify.create(`Reserved desk ${reservation.desk_number} for ${reservation.employee_name}`)  
      } else {
        if (reservation.desk_held) {
          Notify.create({message: `Sorry! Desk ${reservation.desk_number} is held today. Please choose another`, type: 'negative'})
        } else {
          Notify.create({message: `Sorry! Desk ${reservation.desk_number} is already reserved for ${reservation.employee_name}. Please choose another`, type: 'negative'})
        }
      }
      
      // TODO: Temporarily restoring to remove sockets for production
      initDeskReservations()
        .then(() => {
          handleSVG()
        })
        .catch(e => {
          console.error('Error initializing desk reservations:', e)
        })
      
      // Update reserved desks list everywhere with WebSocket
      // this.deskReservationSocket.send(
      //   JSON.stringify({
      //     'message': `Reserved desk ${response.data.desk_number} for ${response.data.employee_name}`
      //   })
      // )
    })
    .catch(e => {
      console.error('Error creating desk reservation:' ,e)
    })
}

function initDesksAndReservations() {
  return Promise.all([initDesks(), initDeskReservations()])
    .catch(e => {
      console.error('Error initializing desks and desk reservations from API:', e)
    })
}

function initDesks() {
  return new Promise((resolve, reject) => {
    deskReservationStore.getAllDesks()
      .then(() => {
        desks.value = deskReservationStore.allDesks
        resolve('Set desks')
      })
      .catch(e => {
        console.error('Error getting desks from API:', e)
        reject(e)
      })
  })
}

function initDeskReservations() {
  return new Promise((resolve, reject) => {
    deskReservationStore.getAllDeskReservations()
      .then(() => {
        deskReservations.value = deskReservationStore.allDeskReservations
        resolve(deskReservations.value)
      })
      .catch(e => {
        console.error('Error initializing desk reservations from API:', e)
        reject(e)
      })
  })
}

function handleSVG() {
  // Destroy any previously created annotation nodes
  const staleAnnotationNodes = Array.from(document.querySelectorAll('.annotation'))
  staleAnnotationNodes.forEach(node => { node.remove() })

  // Destroy any desk highlight circles
  const staleHighlightCircles = Array.from(document.querySelectorAll('.highlight'))
  staleHighlightCircles.forEach(node => { node.remove() })

  // Get horizontal and vertical offsets of svg floor plan
  const floorPlanNode = document.getElementsByClassName('floor-plan')[0]
  const floorPlanRect = floorPlanNode.getBoundingClientRect()

  const textNodes = Array.from(document.querySelectorAll('text'))

  textNodes
    .filter(it => /^\s*/.exec(it.innerHTML))
    .forEach(node => {
      if (!node.firstElementChild) {
        return
      }
      const text = node.firstElementChild.innerHTML
      
      // Ignore any text on the ignore list
      if (ignoreList.indexOf(text) != -1) {
        return
      }

      // Set the location of the highlight
      let setHighlightedXAndY = () => {
        const rect = node.getBoundingClientRect()
        highlightedDeskNumberX.value = rect.left
        highlightedDeskNumberY.value = rect.top
      }
      if (text.toLowerCase() == highlightedDeskNumber.value.toLowerCase()) {
        setHighlightedXAndY()
      } else if (['a', 'b'].indexOf(highlightedDeskNumber.value.toLowerCase().slice(-1)) != -1) {
        if (text.toLowerCase() == highlightedDeskNumber.value.slice(0, -1).toLowerCase()) {
          setHighlightedXAndY()
        }
      }

      const matchingDesks = desks.value.filter((desk: Desk) => {
        let number = ''
        if (['A', 'B'].indexOf(desk.number.slice(-1)) == -1) {
          number = desk.number
        } else {
          number = desk.number.substring(0, desk.number.length-1)
          desk.letter = desk.number.slice(-1)
        }
        return desk.building == BUILDING && desk.floor == FLOOR && number == text
      })
      if (!matchingDesks.length) {
        return
      }

      for (let desk of matchingDesks) {
        // Determine if desk is already reserved
        let deskReserved = false
        const reservations = deskReservations.value.filter((reservation: DeskReservation) => {
          return reservation.desk_building == BUILDING && reservation.desk_floor == FLOOR && reservation.desk_number == desk.number
        })
        if (reservations.length) {
          // Hide any desk labels that shouldn't be displayed
          deskReserved = true
        }

        // Determine if the desk is ergo and/or lead
        // Use correct icon based on ergonomic or not
        const deskLogo = desk.ergonomic ? ErgoDeskImg : StandardDeskImg
        const deskLead = desk.lead

        // Determine if the desk has a hold on it today
        const heldTodayText = desk.held_today ? '*' : ''
      
        // Get the rectangle around the static map label
        const rect = node.getBoundingClientRect()

        // Create an annotation element to replace the static map label
        const annotationElem = document.createElement('div')
        annotationElem.className = 'annotation'
      
        annotationElem.innerHTML = `<button class="desk-button" data-pk="${desk.number}"><div class="desk-buttom-number">${desk.number}${heldTodayText}</div><img class="desk-button-ergo" src="${ deskLogo }" /></button>`
        
        // Position the annotation directly on top of the map label
        // annotationElem.style.left = (rect.left + rect.width/2 - 88).toString() + 'px'
        // annotationElem.style.top = (rect.top + rect.height/2 - 70).toString() + 'px'
        
        // On narrower screens, the header takes up 2-4 rows, so we need to nudge the buttons down to match.
        var singleRowHeaderSpace = 76
        var rowsHeaderSpace = 76
        if (window.innerWidth < 519) {
          // If width less than 519px, there are 3 rows of header
          rowsHeaderSpace = 213
        } else if (window.innerWidth < 561) {
          // If width less that 561px, there are 2 tall rows of header
          rowsHeaderSpace = 177
        } else if (window.innerWidth < 1065) {
          // If width less that 1065px, there are 2 short rows of header
          rowsHeaderSpace = 132
        }
        var extraHeaderSpace = rowsHeaderSpace - singleRowHeaderSpace

        // Adjust A and B desks so they both show up
        let deskSplitHorizontalAdjustment = 0
        if (desk.letter) {
          if (desk.letter == 'A') {
            deskSplitHorizontalAdjustment = -34
          } else {
            deskSplitHorizontalAdjustment = 34
          }
        }

        // TODO: Finish and annotate this - can't brain today
        annotationElem.style.left = (rect.left - floorPlanRect.left - rect.width/2 + annotationElem.offsetWidth/2 + deskSplitHorizontalAdjustment).toString() + 'px'
        // TODO: Fix and annotate this - can't brain today
        annotationElem.style.top = (rect.top - floorPlanRect.top + 68 + extraHeaderSpace).toString() + 'px'

        const clickableButton = annotationElem.querySelector('button') as HTMLElement

        if (clickableButton) {
          if (deskReserved) {
            clickableButton.style.borderColor = redColor
            clickableButton.classList.add('reserved')
            clickableButton.addEventListener('click', e => {
              const target = e.target as HTMLElement
              const buttonElem = target.closest('button')
              if (buttonElem) {
                reservedRoomClick(buttonElem)
              }
            })
          } else {
            if (deskLead) {
              clickableButton.style.backgroundColor = orangeColor
            } else {
              clickableButton.style.backgroundColor = yellowColor
            }
            clickableButton.addEventListener('click', e => {
              const target = e.target as HTMLElement
              const buttonElem = target.closest('button')
              if (buttonElem) {
                roomClick(buttonElem)
              }
            })
          }
        }
        
        document.querySelector('#schaefers-2-page')?.appendChild(annotationElem)
        
        // const annotationSize = annotationElem.getBoundingClientRect()
        
        // annotationElem.style.marginLeft = `-${annotationSize.width/2}px`
        // annotationElem.style.marginTop = `-${annotationSize.height/2}px`
      }
  })

  // Draw a red circle around the highlighted desk
  if (highlightedDeskNumberX.value) {
    const map = document.querySelector('#schaefers-2-page')
    const highlightCircle = document.createElement('div')
    highlightCircle.classList.add('highlight')
    const mapPadding = map ? map.getBoundingClientRect().left : 0
    highlightCircle.style.left = (highlightedDeskNumberX.value - 36 - mapPadding).toString() + 'px'
    highlightCircle.style.top = (highlightedDeskNumberY.value - 45).toString() + 'px'
    map?.appendChild(highlightCircle)
  }
}

// WebSocket magic for sharing reservation changes
// const webSocketUrl = process.env.WEBSOCKET_URL ? process.env.WEBSOCKET_URL : 'ws://api.team.lcog.org/'
// private deskReservationSocket = new WebSocket(
//   `${ this.webSocketUrl }ws/desk-reservation/${ this.BUILDING }/${ this.FLOOR }/`
// )

function showHelp() {
  bus.emit('showReservationHelpDialog', Math.random())
}

onMounted(() => {
  window.addEventListener('resize', handleSVG)

  // When a WebSocket message is received
  // this.deskReservationSocket.onmessage = (socketMessageObj) => {
  //   const socketMessageData = JSON.parse(socketMessageObj.data) // eslint-disable-line @typescript-eslint/no-unsafe-assignment
  //   const updateMessage = socketMessageData.message // eslint-disable-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
  //   this.initDeskReservations()
  //     .then(() => {
  //       this.handleSVG()
  //       Notify.create(updateMessage)
  //     })
  //     .catch(e => {
  //       console.error('Error initializing desk reservations from socket message:', e)
  //     })
  // }

  // We do not expect the socket to ever close
  // this.deskReservationSocket.onclose = () => {
  //   console.error('Desk Reservation socket closed unexpectedly')
  // }
  
  const hourOfDay = new Date().getHours()
  if (hourOfDay < 6 || hourOfDay >= 17) {
    allowReservations.value = false
  }
  
  initDesksAndReservations()
    .then(() => {
      handleSVG()
    })
    .catch(e => {
      console.error('Error initializing desk reservations in component:', e)
    })

  if (!employees().length) {
    retrieveSimpleEmployeeList()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleSVG)
})
</script>

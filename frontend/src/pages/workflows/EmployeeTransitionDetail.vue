<template>
  <div class="q-pt-md">
    
    <!-- TRANSITION TYPE -->
    <div class="text-h6 transition-form-section-heading">Transition Type</div>
    <div class="row items-center">
      <q-radio v-model="type" val="New" id="type-new" disable label="New" />
      <q-radio
        v-model="type" val="Return" id="type-return" disable label="Return"
      />
      <q-radio
        v-model="type"
        val="Name Change"
        id="type-name-change"
        disable
        label="Name Change"
      />
      <q-radio
        v-model="type"
        val="Change/Modify"
        id="type-change"
        disable
        label="Change/Modify"
      />
      <q-radio v-model="type" val="Exit" id="type-exit" disable label="Exit" />
    </div>

    <!-- WORKER TYPE -->
    <div class="text-h6 transition-form-section-heading row">
      <div>Worker Type</div>
      <InfoTooltip :text="workerTypeTooltipText" />
    </div>
    <div class="row items-center">
      <q-radio
        v-model="workerType"
        val="Employee"
        id="worker-type-employee"
        :disable="!canEditOtherFields()"
        label="Employee"
      />
      <q-radio
        v-model="workerType"
        val="Intern"
        id="worker-type-intern"
        :disable="!canEditOtherFields()"
        label="Intern"
      />
      <q-radio
        v-model="workerType"
        val="Volunteer"
        id="worker-type-volunteer"
        :disable="!canEditOtherFields()"
        label="Volunteer"
      />
      <q-radio
        v-model="workerType"
        val="Temp Agency"
        id="worker-type-temp-agency"
        :disable="!canEditOtherFields()"
        label="Temp Agency"
      />
      <q-radio
        v-model="workerType"
        val="Temp Non-Agency"
        id="worker-type-temp-non-agency"
        :disable="!canEditOtherFields()"
        label="Temp Non-Agency"
      />
      <q-radio
        v-model="workerType"
        val="Contractor"
        id="worker-type-contractor"
        :disable="!canEditOtherFields()"
        label="Contractor"
      />
    </div>
    
    <!-- SUBMISSION INFO -->
    <div class="text-h6 transition-form-section-heading">Submission Info</div>
    <div class="row items-center">
      <div class="q-mr-md">
        <span class="text-bold">Date Submitted:</span>
        {{ readableDateTime(dateSubmitted) }}
      </div>
      <div><span class="text-bold">Submitter:</span> {{ submitterName }}</div>
    </div>

    <!-- SPECIAL INSTRUCTIONS -->
    <div class="text-h6 transition-form-section-heading">
      Notes/Special Instructions
    </div>
    <div class="row">
      <div
        v-if="props.print"
        class="print-text-area"
        v-html="specialInstructions"
      ></div>
      <q-input
        v-else
        name="special-instructions"
        v-model="specialInstructions"
        autogrow
        style="width:100%"
        :readonly="!canEditOtherFields()"
        :hint="employeeID == 'CLSD' ?
          'Please include which employee you would like this modeled after' :
          ''"
      />
    </div>

    <!-- EMPLOYEE DETAILS -->
    <div class="text-h6 transition-form-section-heading">
      {{ workerLabel() }} Details
    </div>
    <div class="row" v-if="type == 'Name Change'">
      <EmployeeSelect
        name="current_employee"
        label="Employee"
        :employee="currentEmployee"
        :useLegalName="true"
        v-on:input="currentEmployee=$event"
        v-on:clear="currentEmployee=emptyEmployee"
        class="q-mr-md"
        :readOnly="!canEditOtherFields()"
      />
    </div>
    <div class="row">
      <q-input
        stack-label
        v-model="employeeFirstName"
        label="First"
        class="q-mr-md"
        name="first-name"
        :readonly="!canEditOtherFields()"
      />
      <q-input
        stack-label
        v-model="employeeMiddleInitial"
        maxlength=5
        label="Middle Initial"
        class="q-mr-md"
        name="middle-initial"
        style="width: 5em"
        :readonly="!canEditOtherFields()"
      />
      <q-input
        stack-label
        v-model="employeeLastName"
        label="Last"
        class="q-mr-md"
        name="last-name"
        :readonly="!canEditOtherFields()"
      />
      <q-input
        v-model="employeePreferredName"
        label="Preferred Name, if different"
        style="width: 25em"
        name="preferred-name"
        :readonly="!canEditOtherFields()"
      />
    </div>
    <div class="row">
      <q-select
        v-model="employeeID"
        name="employee-id"
        id="employee-id"
        :options="['CLSD', 'CLID', 'None/Non-Employee']"
        label="Employee ID"
        class="q-mr-sm"
        style="width: 130px;"
        :readonly="!canEditEmployeeNumberFields()"
      >
        <template
          v-if="canEditEmployeeNumberFields() && employeeID"
          v-slot:append
        >
          <q-icon
            name="cancel"
            @click.stop="employeeID=''"
            class="cursor-pointer"
          />
        </template>
      </q-select>
      <q-input
        v-model="employeeNumber"
        type="number"
        :label=workerNumberLabel()
        name="employee-number"
        mask="####"
        class="q-mr-md"
        :readonly="!canEditEmployeeNumberFields()"
      />
      <q-input
        v-model="employeeEmail"
        type="email"
        label="Email"
        @focus="suggestEmail()"
        :readonly="!canEditEmployeeNumberFields()"
        name="email"
      />
    </div>

    <!-- POSITION -->
    <div v-if="type != 'Name Change'">
      <div class="text-h6 transition-form-section-heading">Position</div>
      <div class="row">
        <JobTitleSelect
          label="Title"
          :title="title"
          v-on:input="title=$event"
          v-on:clear="title=emptyTitle"
          class="q-mr-md"
          name="title"
          :disable="!canEditOtherFields()"
        />
        <div v-if="type != 'Exit'">
          <q-input
            v-if="workerType == 'Employee'"
            v-model="fte"
            name="fte"
            label="FTE"
            class="q-mr-md"
            :readonly="!canEditOtherFields()"
            :rules="[val => decimalNumberRegex.test(val) || 'Must be a number']"
          />
          <q-input
            v-else-if="workerType !== 'Contractor'"
            v-model="hoursPerWeek"
            name="hoursPerWeek"
            label="Hours per week"
            class="q-mr-md"
            :readonly="!canEditOtherFields()"
            :rules="[val => decimalNumberRegex.test(val) || 'Must be a number']"
          />
        </div>
        <q-checkbox
          v-model="bilingual"
          label="Bilingual"
          class="q-mr-md"
          id="bilingual"
          :disable="!canEditOtherFields()"
        />
        <!-- TODO: For some reason this component won't initialize with secondLanguage -->
        <!-- <LanguageSelect
          v-if="bilingual"
          label="Second Language"
          :language="secondLanguage"
          foo="bar"
          v-on:input="secondLanguage=$event"
          v-on:clear="secondLanguage=''"
        /> -->
        <q-select
          v-if="bilingual"
          label="Second Language"
          v-model="secondLanguage"
          :options="languageOptions"
          class="language-select"
          id="second-language"
          :disable="!canEditOtherFields()"
        >
          <template v-if="secondLanguage" v-slot:append>
            <q-icon
              name="cancel"
              @click.stop="secondLanguage=''"
              class="cursor-pointer" />
          </template>
        </q-select>
      </div>
      <div v-if="parseFloat(fte) < 0.5">
        <span class="text-bold">NOTE:</span> Staff less than .5 FTE are not
        benefits eligible and will not receive LCOG vacation. They will accrue the
        state-mandated sick leave of 1 hour for every 30 hours worked.
      </div>
      <div v-if="workerType == 'Employee'" class="row">
        <q-select
          v-model="unionAffiliation"
          :options="['Non-Represented','EA', 'SEIU', 'Senior Meals', 'Management']"
          label="Salary Schedule/Union Affiliation"
          id="union-affiliation"
          class="q-mr-md"
          :disable="!canEditOtherFields()"
          style="width: 275px;"
        >
          <template v-if="unionAffiliation" v-slot:append>
            <q-icon
              name="cancel"
              @click.stop="unionAffiliation=''"
              class="cursor-pointer"
            />
          </template>
        </q-select>
        <q-input
          v-if="canViewSalaryFields()"
          v-model="salaryRange"
          name="salary-range"
          label="Salary Range"
          class="q-mr-md"
          clearable
          :rules="
            [ val => Number.isInteger(Math.floor(val)) || 'Please enter a number']
          "
        />
        <q-select
          v-if="canViewSalaryFields()"
          v-model="salaryStep"
          id="salary-step"
          name="salary-step"
          :options="Array.from({length:10}, (x, i) => i+1)"
          label="Salary Step"
          style="width: 131px;"
          clearable
        />
      </div>
      <div v-else-if="['Intern', 'Volunteer', 'Contractor'].indexOf(workerType) != -1">
        <q-input
          v-if="canViewSalaryFields()"
          v-model="stipend"
          name="stipend"
          :label="workerType == 'Contractor' ? 'Contractual Maximum Compensation / Not to Exceed Amount' : 'Stipend'"
          class="q-mr-md"
          clearable
        />
      </div>
      <div v-else-if="workerType == 'Temp Non-Agency'">
        <q-input
          v-if="canViewSalaryFields()"
          v-model="hourlyRate"
          name="hourly-rate"
          label="Hourly Rate"
          class="q-mr-md"
          style="width: 150px;"
          :rules="
            [ val => val === null || !isNaN(val) || 'Please enter a number']
          "
        />
      </div>
      <div class="row items-center">
        <EmployeeSelect
          name="manager"
          label="Manager"
          :employee="manager"
          :useLegalName="true"
          v-on:input="manager=$event"
          v-on:clear="manager=emptyEmployee"
          class="q-mr-md"
          :readOnly="!canEditManagerField()"
        />
        <UnitSelect
          label="Unit"
          name="unit"
          :unit="unit"
          v-on:input="unit=$event"
          v-on:clear="unit=emptyUnit"
          :disable="!canEditOtherFields()"
        />
      </div>
    </div>

    <!-- WORK DETAILS -->
    <div v-if="type != 'Name Change'">
      <div class="text-h6 transition-form-section-heading">Work Details</div>
      <div class="row q-mt-md">
        <div v-if="type=='Exit'">End Date/Time</div>
        <div v-else>Start Date/Time</div>
      </div>
      <div v-if="props.print" class="row q-my-sm">{{ transitionDate }}</div>
      <div v-else class="row q-my-sm">
        <q-date
          id="transition-date"
          v-model="transitionDate"
          mask="YYYY-MM-DD HH:mm"
          class="q-mr-md"
          :readonly="!canEditOtherFields()"
        />
        <q-time
          id="transition-time"
          v-model="transitionDate"
          mask="YYYY-MM-DD HH:mm"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div v-if="['Employee', 'Contractor'].indexOf(workerType) == -1" class="row items-center">
        <div class="q-mr-xs text-h6">Schedule</div>
        <q-checkbox
          v-for="(item, index) in scheduleOptions"
          :key="index"
          v-model="schedule"
          :val="item[0]"
          :label="item[1]"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div class="q-my-sm" v-if="['Change/Modify'].indexOf(type) != -1">
        <div class="row items-center">
          <q-checkbox
            id="system-change-date-different"
            v-model="systemChangeDateDifferent"
            label="SDS system changes date different from transition date"
            class="q-mr-xs"
            :disable="!canEditOtherFields()"
          />
          <div
            v-if="systemChangeDateDifferent"
            style="color: red"
          >
            – HR and Payroll systems always change on transition date
          </div>
        </div>
        <q-date
          id="system-change-date"
          v-model="systemChangeDate"
          v-if="systemChangeDateDifferent"
          landscape
          mask="YYYY-MM-DD HH:mm"
          class="q-mr-md"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div class="row q-my-sm" v-if="['New', 'Return'].indexOf(type) != -1">
        <q-checkbox
          id="lwop"
          v-model="lwop"
          label="Pre Approved LWOP at time of hire"
          class="q-mr-md"
          :disable="!canEditOtherFields()"
        />
        <q-input
          name="lwop-details"
          v-model="lwopDetails"
          v-if="lwop"
          label="Dates and hours approved"
          style="width: 350px;"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div class="row q-my-sm">
        <q-checkbox
          id="preliminary-hire"
          v-model="preliminaryHire"
          v-if="employeeID == 'CLSD'"
          label="Preliminary Hire"
          :disable="!canEditOtherFields()"
        />
        <q-checkbox
          name="delete-profile"
          v-if="type=='Exit'"
          v-model="deleteProfile"
          label="Delete Profile"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div class="row" id="office-location">
        <q-btn
          v-if="showMapButton()"
          square
          icon="map"
          color="primary"
          flat
          class="q-mr-sm"
          @click="navigateToMap()"
        >
          <q-tooltip>Map</q-tooltip>
        </q-btn>
        <q-select
          name="office-location"
          v-model="officeLocation"
          :options="[
            'Cottage Grove', 'Florence', 'Junction City', 'Oakridge',
            'PPB - 1st Floor', 'PPB - 4th Floor', 'PPB - 5th Floor',
            'Schaefers - Basement', 'Schaefers - 1st Floor',
            'Schaefers - 2nd Floor', 'Schaefers - 3rd Floor', 'Senior Meals Site',
            'Veneta'
          ]"
          label="Office Location"
          class="q-mr-md"
          style="width: 193px;"
          :disable="!canEditOtherFields()"
        >
          <template v-if="officeLocation" v-slot:append>
            <q-icon
              name="cancel"
              @click.stop="officeLocation=''"
              class="cursor-pointer"
            />
          </template>
        </q-select>
        <q-input
          name="cubicle-number"
          v-model="cubicleNumber"
          maxlength="10"
          label="Cubicle Number"
          class="q-mr-md"
          :readonly="!canEditOtherFields()"
        />
        <q-checkbox
          id="teleworking"
          v-model="teleworking"
          label="Teleworking"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div v-if="['New', 'Return'].indexOf(type) != -1">
        <div class="text-h6 transition-form-section-heading">Computer</div>
        <div class="row items-center" id="computer-type">
          <div class="q-gutter-sm q-mr-md">
            <q-radio
              id="computer-new"
              v-model="computerType"
              val="New"
              label="New"
              :disable="!canEditOtherFields()"
            />
            <q-radio
              id="computer-repurposed"
              v-model="computerType"
              val="Repurposed"
              label="Existing Equipment"
              :disable="!canEditOtherFields()"
            />
          </div>
          <q-input
            v-if="computerType == 'New'"
            name="computer-gl"
            v-model="computerGL"
            label="GL Code"
            style="width: 250px;"
            :readonly="!canEditOtherFields()"
            maxlength="30"
          />
          <q-input
            v-else
            name="computer-description"
            v-model="computerDescription"
            label="Description of existing computer"
            style="width: 350px;"
            :readonly="!canEditOtherFields()"
          />
        </div>
        <div
          v-if="computerType == 'New'"
          class="row q-mt-sm"
          style="color: red"
        >
          Note that new PCs take 2-4 weeks to order.
        </div>
      </div>
    </div>

    <!-- PHONE -->
    <div v-if="type != 'Name Change'">
      <div class="text-h6 transition-form-section-heading">Phone</div>
      <div class="row">
        <q-input
          name="phone-number"
          v-model="phoneNumber"
          type="tel"
          label="Phone Number"
          mask="(###) ###-####"
          fill-mask
          class="q-mr-md"
          :readonly="!canEditOtherFields()"
        />
        <q-select
          name="phone-request"
          v-model="phoneRequest"
          :options="[
            'New number needed', 'Remove phone', 'Delete number', 'Reassign to:',
            'Change name display to:', 'Delete voicemail box', 'No phone needed'
          ]"
          label="Phone Update"
          style="width: 218px;"
          class="q-mr-md"
          :disable="!canEditOtherFields()"
        >
          <template v-if="phoneRequest" v-slot:append>
            <q-icon
              name="cancel"
              @click.stop="phoneRequest=''"
              class="cursor-pointer"
            />
          </template>
        </q-select>
        <q-input
          name="phone-request-data"
          v-model="phoneRequestData"
          v-if="[
            'Reassign to:', 'Change name display to:'
          ].indexOf(phoneRequest) != -1"
          :label="phoneRequest.indexOf('Reassig') != -1 ? 'To whom?' : 'To what?'"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div class="row">
        <q-input
          name="load-code"
          v-model="loadCode"
          v-if="employeeID == 'CLSD'"
          label="Load Code"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div v-if="type !== 'Exit'" class="row">
        <q-checkbox
          id="cell-phone-needed"
          v-model="cellPhone"
          label="Cell Phone Needed"
          class="q-mr-md"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div v-if="['Change/Modify', 'Exit'].indexOf(type) != -1" class="row">
        <q-checkbox
          id="extension-remain-active"
          v-model="extensionRemainActive"
          label="Extension should remain active"
          class="q-mr-md"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div v-if="type=='Exit'" class="row">
        <q-checkbox
          id="delete"
          v-model="shouldDelete"
          label="Delete?"
          :disable="!canEditOtherFields()"
          class="q-mr-md"
        />
        <q-input
          name="reassign-to"
          v-model="reassignTo"
          label="Reassign to"
          :readonly="!canEditOtherFields()"
        />
      </div>
      <div v-if="['New', 'Return', 'Change/Modify'].indexOf(type) != -1">
        <div class="text-h6 transition-form-section-heading">Software/Access</div>
        <div class="row">
          <q-checkbox
            id="gas-pin-needed"
            v-model="gasPINNeeded"
            label="Gas PIN Needed"
            :disable="!canEditOtherFields()"
          />
        </div>
        <div class="row" v-if="employeeID == 'CLSD'">
          <q-select
            name="oregon-access"
            v-model="oregonAccess"
            :options="[
              'Not needed', 'Desktop & Remote', 'Remote'
            ]"
            label="Oregon Access"
            style="width: 218px;"
            :disable="!canEditOtherFields()"
          />
        </div>
      </div>
    </div>

    <!-- ID CARDS -->
    <div v-if="type != 'Name Change'">
      <div class="text-h6 transition-form-section-heading">ID Cards</div>
      <div class="row">
        <q-checkbox
          id="business-cards"
          v-model="businessCards"
          label="Order Business Cards"
          :disable="!canEditOtherFields()"
        />
        <q-checkbox
          v-if="type!='Exit'"
          id="prox-card-needed"
          v-model="proxCardNeeded"
          label="Proxy Card Needed"
          :disable="!canEditOtherFields()"
        />
        <q-checkbox
          v-if="type!='Exit' && employeeID == 'CLSD'"
          id="mailbox-needed"
          v-model="mailboxNeeded"
          label="Physical Mailbox Needed"
          :disable="!canEditOtherFields()"
        />
      </div>
      <div v-if="type=='Exit'">
        <div class="text-h6 transition-form-section-heading">
          Computer Profile
        </div>
        <div class="row">
          <div>
            Email account will be disabled (no incoming or outgoing emails) on End
            Date
            <span class="text-underline">
              unless otherwise specified in special instructions
            </span>.
          </div>
        </div>
        <div class="row">
          <q-checkbox
            id="show-access-emails"
            v-model="showAccessEmails"
            label="Does someone need to access current emails?"
            class="q-mr-md"
            :disable="!canEditOtherFields()"
          />
          <EmployeeSelect
            v-if="showAccessEmails"
            name="access-emails"
            label="Who?"
            :employee="accessEmails"
            :useLegalName="true"
            :readOnly=false
            v-on:input="accessEmails=$event"
            v-on:clear="accessEmails=emptyEmployee"
            class="q-mr-md"
            :disable="!canEditOtherFields()"
          />
        </div>
      </div>
    </div>

    <!-- FISCAL USE ONLY -->
    <div v-if="type != 'Name Change'">
      <div class="text-h6 transition-form-section-heading">
        Fiscal Use Only
      </div>
      <div class="row">
        <div
          v-if="props.print"
          class="print-text-area"
          v-html="fiscalField"
        ></div>
        <q-input
          v-else
          v-model="fiscalField"
          name="fiscal-field"
          autogrow
          style="width:100%"
          hint="_ _ _ - _ _ - _ _ _ _ / Allocation %"
          :readonly="!canEditFiscalField()" />
      </div>
    </div>

    <!-- Dialog of all error items -->
    <q-dialog v-model="showErrorDialog" :position="errorDialogPosition">
      <q-card style="width: 350px">
        <q-list bordered separator>
          <q-item
            v-for="(item, index) in formErrorItems()"
            :key="index"
            clickable
            @click="clickedErrorItem(item)"
          >
            <q-item-label>{{item[1]}}</q-item-label>
          </q-item>
        </q-list>
      </q-card>
    </q-dialog>

    <!-- Dialog of changes -->
    <q-dialog v-model="showChangesDialog">
      <q-card class="q-pa-md">
        <q-list bordered separator>
          <q-item v-for="(changeRecord, index) in changes" :key="index">
            <q-item-section top avatar>
              <Avatar
                :initials="changeRecord.created_by_initials"
                :name="changeRecord.created_by_name"
              />
            </q-item-section>
            <q-item-section>
              <q-item-label
                v-for="(value, key, index) in JSON.parse(changeRecord.changes)"
                :key="index"
              >
                <div v-if="value.original && value.original != 'None'">
                  {{ key }}: {{ value.original }} ->
                  <span class="text-bold">{{ value.new }}</span>
                </div>
                <div v-else>
                  {{ key }}: <span class="text-bold">{{ value.new }}</span>
                </div>
              </q-item-label>
            </q-item-section>
            <q-item-section side top>
              <q-item-label caption>
                {{ readableDateTime(changeRecord.date) }}
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </q-dialog>

    <!-- Send to SDS Hiring Leads Dialog -->
    <q-dialog v-model="showSendToSDSHiringLeadsDialog">
      <q-card class="q-pa-md" style="width: 400px">
        <div class="text-h6">Send transition to S&DS hiring admins?</div>
        <div class="row text-red">
          <q-icon class="col-1 q-mr-xs" name="warning" size="md"/>
          <div class="col text-bold text-center">
            By submitting this information you are providing your electronic
            signature approving this request.
          </div>
        </div>
        <q-chip
          v-if="valuesAreChanged()"
          color="negative"
          text-color="white"
          icon="warning"
          label="Unsaved changes - please save before sending"
        />
        <q-form
          @submit='onSubmitSendDialog("SDS")'
          class="q-gutter-md"
        >
          <q-input
            v-model="sendDialogMessage"
            filled
            type="textarea"
            label="Extra message to include"
          />
          <div class="row justify-between">
            <q-btn
              name="send-sds-dialog-button"
              label="Send"
              icon-right="send"
              type="submit"
              color="primary"
              :disable="formErrors() || valuesAreChanged()"
            />
            <div
              v-if="formErrors()"
              class="text-red text-bold"
              style="width:180px;"
            >
              There are errors in the form. Fix before submitting.
            </div>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Send to Fiscal Dialog -->
    <q-dialog v-model="showSendToFiscalDialog">
      <q-card class="q-pa-md" style="width: 400px">
        <div class="text-h6">Send transition to Fiscal?</div>
        <q-chip
          v-if="valuesAreChanged()"
          color="negative"
          text-color="white"
          icon="warning"
          label="Unsaved changes - please save before sending"
        />
        <q-form
          @submit='onSubmitSendDialog("FI")'
          class="q-gutter-md"
        >
          <q-input
            v-model="sendDialogMessage"
            filled
            type="textarea"
            label="Extra message to include"
          />
          <div class="row justify-between">
            <q-btn
              name="send-fiscal-dialog-button"
              label="Send"
              icon-right="send"
              type="submit"
              color="primary"
              :disable="formErrors() || valuesAreChanged()"
            />
            <div
              v-if="formErrors()"
              class="text-red text-bold"
              style="width:180px;"
            >
              There are errors in the form. Fix before submitting.
            </div>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Send to HR Dialog -->
    <q-dialog v-model="showSendToHRDialog">
      <q-card class="q-pa-md" style="width: 400px">
        <div class="text-h6">Send transition to HR?</div>
        <q-chip
          v-if="valuesAreChanged()"
          color="negative"
          text-color="white"
          icon="warning"
          label="Unsaved changes - please save before sending"
        />
        <q-form
          @submit='onSubmitSendDialog("HR")'
          class="q-gutter-md"
        >
          <q-input
            v-model="sendDialogMessage"
            filled
            type="textarea"
            label="Extra message to include"
          />
          <div class="row justify-between">
            <q-btn
              name="send-hr-dialog-button"
              label="Send"
              icon-right="send"
              type="submit"
              color="primary"
              :disable="formErrors() || valuesAreChanged()"
            />
            <div
              v-if="formErrors()"
              class="text-red text-bold"
              style="width:180px;"
            >
              There are errors in the form. Fix before submitting.
            </div>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Send to staff transition news Dialog -->
    <q-dialog v-model="showSendToSTNDialog">
      <q-card class="q-pa-md">
        <div class="text-h6">Send message to staff transition news?</div>
        <q-chip
          v-if="valuesAreChanged()"
          color="negative"
          text-color="white"
          icon="warning"
          label="Unsaved changes - please save before sending"
        />
        <q-form
          @submit='onSubmitSendDialog("STN")'
          class="q-gutter-md"
        >
          <q-checkbox v-model="sendDialogUpdate" label="Update" />
          <q-input
            v-model="sendDialogMessage"
            filled
            type="textarea"
            label="Extra message to include"
          />
          <div class="row justify-between">
            <q-btn
              name="send-stn-dialog-button"
              label="Send to STN"
              icon-right="send"
              type="submit"
              color="primary"
              :disable="formErrors() || valuesAreChanged()"
            />
            <div
              v-if="formErrors()"
              class="text-red text-bold"
              style="width:180px;"
            >
              There are errors in the form. Fix before submitting.
            </div>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Update assignee Dialog -->
    <q-dialog v-model="showAssigneeDialog">
      <q-card class="q-pa-md">
        <div class="text-h6">Reassign transition form?</div>
        <div>Select a new assignee and include</div> 
        <div>an explaination for this action.</div>
        <div class="text-red text-uppercase text-bold q-mt-sm q-mb-md">This action cannot be undone</div>
        <q-form
          @submit='onSubmitSendDialog("ASSIGN")'
          class="q-gutter-md"
        >
          <q-btn-dropdown
            name="reassign-dialog-assignee-dropdown"
            style="height: 36px;"
            color="primary"
            :label="assigneeLabel('DB')"
          >
            <q-list>
              <q-item
                v-for="option of assigneeOptions()"
                :key="option"
                clickable
                v-close-popup
                @click="setAssignee(option)"
              >
                <q-item-section>
                  <q-item-label>{{ option }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
          <q-input
            name="reassign-extra-message"
            v-model="reassignDialogMessage"
            filled
            type="textarea"
            label="Message - REQUIRED"
          />
          <div>
            <q-btn
              name="reassign-dialog-button"
              label="Reassign"
              icon-right="send"
              type="submit"
              color="primary"
              :disable="reassignDialogMessage.length == 0 ||
                assignee == assigneeCurrentVal"
            />
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Spacing for footer -->
    <div style="height: 80px;"></div>

    <div id="sticky-footer" class="row justify-between" v-if="!props.print">
      <div class="row">
        <q-btn
          v-if="canEditOtherFields()"
          class="q-mr-sm"
          :color="valuesAreChanged() ? 'positive' : 'white'"
          :text-color="valuesAreChanged() ? 'white' : 'black'"
          label="Save"
          name="save-button"
          style="width: 86.33px; height: 36px;"
          :disabled="!valuesAreChanged()"
          @click="updateTransition()"
        />
        <div v-else></div>
        <q-btn
          name="reassign-button"
          style="height: 36px;"
          color="primary"
          :label="assigneeLabel('CURRENT')"
          :disable="!canUpdateAssignee()"
          @click="showAssigneeDialog=true"
        />
      </div>
      <q-chip
        v-if="valuesAreChanged()"
        color="warning"
        text-color="white"
        icon="warning"
        label="Unsaved changes"
      />
      <div>
        <q-btn
          v-if="changes && changes.length"
          color="white"
          text-color="black"
          label="Change Records"
          @click="showChangesDialog = true"
        />
        <q-btn
          v-if="showErrorButton && formErrors()"
          label="Show errors"
          icon="check"
          color="warning"
          class="q-ml-sm"
          @click="openErrorDialog('right')"
        />
        <q-btn
          class="q-ml-sm"
          color="white"
          text-color="black"
          icon="print"
          label="Print"
          @click="router.push({ name: 'workflow-print' })"
        />
        <q-btn
          v-if="canSendToTransitionNews()"
          name="send-stn-button"
          class="q-ml-sm"
          color="white"
          text-color="black"
          icon="send"
          label="Send to STN"
          @click="showSendToSTNDialog = true"
        />
        <q-btn
          v-else-if="canSendToHR()"
          name="send-hr-button"
          class="q-ml-sm"
          color="white"
          text-color="black"
          icon="send"
          label="Send to HR"
          @click="showSendToHRDialog = true"
        />
        <q-btn
          v-else-if="canSendToFiscal()"
          name="send-fiscal-button"
          class="q-ml-sm"
          color="white"
          text-color="black"
          icon="send"
          label="Send to Fiscal"
          @click="showSendToFiscalDialog = true"
        />
        <q-btn
          v-else-if="canSendToHiringLeads()"
          name="send-sds-button"
          class="q-ml-sm"
          color="white"
          text-color="black"
          icon="send"
          label="Send to Hiring Leads"
          @click="showSendToSDSHiringLeadsDialog = true"
        />
      </div>
      <!-- <div class="col-3 self-center status">
        Current Status: {{ status }}
      </div> -->
    </div>
  </div>
</template>

<style scoped lang="scss">
.text-underline {
  text-decoration: underline;
}
.transition-form-section-heading {
  border-bottom: 2px solid black;
  margin: 10px 0;
}
.language-select {
  width: 221px
}
.print-text-area {
  white-space: pre-line;
}
#sticky-footer {
  padding: 10px;
  background-color: rgb(25, 118, 210);
  position: fixed;
  bottom: 0;
  right: 0;
  left: 0;
  z-index: 2;

  .status {
    color: white;
  }
}
@media only screen and (min-width: 1024px) {
  #sticky-footer {
    left: 209px;
  }
}
</style>

<script setup lang="ts">
import { QDialogProps, scroll, useQuasar } from 'quasar'
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref, Ref, watch } from 'vue'
import { useCookies } from 'vue3-cookies'

import useEventBus from 'src/eventBus'
import { readableDateTime } from 'src/filters'
import {
  EmployeeTransition, TransitionChange, WorkflowInstance
} from 'src/types'
import Avatar from 'src/components/Avatar.vue'
import EmployeeSelect from 'src/components/EmployeeSelect.vue'
import InfoTooltip from 'src/components/InfoTooltip.vue'
import JobTitleSelect from 'src/components/JobTitleSelect.vue'
// import LanguageSelect from 'src/components/LanguageSelect.vue'
import UnitSelect from 'src/components/UnitSelect.vue'
import { usePeopleStore } from 'src/stores/people'
import { useUserStore } from 'src/stores/user'
import { useWorkflowsStore } from 'src/stores/workflows'
import { getRoutePk } from 'src/utils'

const quasar = useQuasar()
const { getScrollTarget, setVerticalScrollPosition  } = scroll
const route = useRoute()
const router = useRouter()
const bus = useEventBus()
const { cookies } = useCookies()
const peopleStore = usePeopleStore()
const userStore = useUserStore()
const workflowsStore = useWorkflowsStore()

const emptyEmployee = {name: '', legal_name: '', pk: -1}
const emptyTitle = {name: '', pk: -1}
const emptyUnit = {name: '', pk: -1}

const languageOptions = [
  'American Sign Language', 'Arabic', 'Bengali', 'Chinese', 'Croatian',
  'Czech', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Greek',
  'Gujarati', 'Haitian Creole', 'Hebrew', 'Hindi', 'Hungarian', 'Indonesian',
  'Italian', 'Japanese', 'Korean', 'Latvian', 'Lithuanian', 'Norwegian',
  'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Serbian',
  'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish', 'Tagalog', 'Tamil',
  'Thai', 'Turkish', 'Urdu', 'Vietnamese', 'Welsh', 'Xhosa', 'Zulu',
]

const scheduleOptions = [
  ['M', 'Monday'], ['U', 'Tuesday'], ['W', 'Wednesday'], ['H', 'Thursday'],
  ['F', 'Friday']
]

const decimalNumberRegex = /^[+-]?(([1-9][0-9]*)?[0-9](\.[0-9]*)?|\.[0-9]+)$/

const workerTypeTooltipText = `
  <div>
    <span style="text-decoration: underline;">Employee</span>: This person is being hired as an full- or part-time employee of LCOG. They will provide us a W-4 and LCOG will provide them a W-2.<br />
    <span style="text-decoration: underline;">Intern</span>: This person is coming on as an intern as defined by the Department of Labor. They may or may not receive a stipend (please refer to Department of Labor rules regarding interns and stipends).<br />
    <span style="text-decoration: underline;">Volunteer</span>: This person is volunteering their unpaid time with the agency (please refer to Department of Labor rules regarding volunteers).<br />
    <span style="text-decoration: underline;">Temp Agency</span>: This person is a temporary employee hired through an agency. LCOG pays the agency for their time instead of directly paying the employee.<br />
    <span style="text-decoration: underline;">Temp Non-Agency</span>: This person is a temporary employee hired directly by LCOG. LCOG directly pays the employee for their time.<br />
    <span style="text-decoration: underline;">Contractor</span>: This person is an independent contractor who is providing services to LCOG, but LCOG does not control the means or method by which they perform the work. This person will receive a 1099 and is paid by Accounts Payable upon their submission and the subsequent approval of an invoice.
  </div>
`

const props = defineProps<{
  print?: boolean
}>()

function currentEmployeeTransition(): EmployeeTransition {
  return workflowsStore.currentEmployeeTransition
}

let transitionPk = ref('')

let typeCurrentVal = ref('')
let type = ref('')
let workerTypeCurrentVal = ref('')
let workerType = ref('')
let dateSubmitted = ref(new Date())
let submitterPk = ref(-1)
let submitterName = ref('')
let submitterDivision = ref('')
let currentEmployeeCurrentVal = ref(emptyEmployee)
let currentEmployee = ref(emptyEmployee)
let employeeFirstNameCurrentVal = ref('')
let employeeFirstName = ref('')
let employeeMiddleInitialCurrentVal = ref('')
let employeeMiddleInitial = ref('')
let employeeLastNameCurrentVal = ref('')
let employeeLastName = ref('')
let employeePreferredNameCurrentVal = ref('')
let employeePreferredName = ref('')
let employeeNumberCurrentVal = ref('')
let employeeNumber = ref('')
let employeeIDCurrentVal = ref('') // TODO This should be EmployeeID
let employeeID = ref('') // TODO This should be EmployeeID
let employeeEmailCurrentVal = ref('')
let employeeEmail = ref('')
let titleCurrentVal = ref(emptyTitle)
let title = ref(emptyTitle)
let fteCurrentVal = ref('')
let fte = ref('')
let hoursPerWeekCurrentVal = ref('')
let hoursPerWeek = ref('')
let hourlyRateCurrentVal = ref(null) as Ref<number | null>
let hourlyRate = ref(null) as Ref<number | null>
let salaryRangeCurrentVal = ref(null) as Ref<number | null>
let salaryRange = ref(null) as Ref<number | null>
let salaryStepCurrentVal = ref(null) as Ref<number | null>
let salaryStep = ref(null) as Ref<number | null>
let stipendCurrentVal = ref(null) as Ref<string | null>
let stipend = ref(null) as Ref<string | null>
let bilingualCurrentVal = ref(false)
let bilingual = ref(false)
let secondLanguageCurrentVal = ref('')
let secondLanguage = ref('')
let managerCurrentVal = ref(emptyEmployee)
let manager = ref(emptyEmployee)
let unitCurrentVal = ref(emptyUnit)
let unit = ref(emptyUnit)
let transitionDateCurrentVal = ref(null) as Ref<string | null>
let transitionDate = ref(null) as Ref<string | null>
let systemChangeDateDifferent = ref(false)
let systemChangeDateCurrentVal = ref(null) as Ref<string | null>
let systemChangeDate = ref(null) as Ref<string | null>
let scheduleCurrentVal = ref([]) as Ref<string[]>
let schedule = ref([]) as Ref<string[]>
let lwopCurrentVal = ref(false)
let lwop = ref(false)
let lwopDetailsCurrentVal = ref('')
let lwopDetails = ref('')
let preliminaryHireCurrentVal = ref(false)
let preliminaryHire = ref(false)
let deleteProfileCurrentVal = ref(false)
let deleteProfile = ref(false)
let officeLocationCurrentVal = ref('')
let officeLocation = ref('')
let cubicleNumberCurrentVal = ref(null) as Ref<number | null>
let cubicleNumber = ref(null) as Ref<number | null>
let unionAffiliationCurrentVal = ref('')
let unionAffiliation = ref('')
let teleworkingCurrentVal = ref(false)
let teleworking = ref(false)
let computerTypeCurrentVal = ref('')
let computerType = ref('')
let computerGLCurrentVal = ref('')
let computerGL = ref('')
let computerDescriptionCurrentVal = ref('')
let computerDescription = ref('')
let phoneNumberCurrentVal = ref('')
let phoneNumber = ref('')
let phoneRequestCurrentVal = ref('')
let phoneRequest = ref('')
let phoneRequestDataCurrentVal = ref('')
let phoneRequestData = ref('')
let loadCodeCurrentVal = ref('')
let loadCode = ref('')
let cellPhoneCurrentVal = ref(false)
let cellPhone = ref(false)
let shouldDeleteCurrentVal = ref(false)
let shouldDelete = ref(false)
let extensionRemainActiveCurrentVal = ref(false)
let extensionRemainActive = ref(false)
let reassignToCurrentVal = ref('')
let reassignTo = ref('')
let gasPINNeededCurrentVal = ref(false)
let gasPINNeeded = ref(false)
let oregonAccessCurrentVal = ref('Not needed')
let oregonAccess = ref('Not needed')
let businessCardsCurrentVal = ref(false)
let businessCards = ref(false)
let proxCardNeededCurrentVal = ref(false)
let proxCardNeeded = ref(false)
let mailboxNeededCurrentVal = ref(false)
let mailboxNeeded = ref(false)
let showAccessEmailsCurrentVal = ref(false)
let showAccessEmails = ref(false)
let accessEmailsCurrentVal = ref(emptyEmployee)
let accessEmails = ref(emptyEmployee)
let specialInstructionsCurrentVal = ref('')
let specialInstructions = ref('')
let fiscalFieldCurrentVal = ref('')
let fiscalField = ref('')
let assigneeCurrentVal = ref('')
let assignee = ref('')

function assigneeOptions() {
  if (submitterDivision.value == 'Senior & Disability Services') {
    if (assigneeCurrentVal.value == 'Hiring Lead') {
      return ['Submitter', 'Hiring Lead']
    } else if (assigneeCurrentVal.value == 'Fiscal') {
      return ['Submitter', 'Hiring Lead', 'Fiscal']
    } else if (assigneeCurrentVal.value == 'HR') {
      return ['Submitter', 'Hiring Lead', 'Fiscal', 'HR']
    } else if (assigneeCurrentVal.value == 'Complete') {
      return ['Submitter', 'Hiring Lead', 'Fiscal', 'HR', 'Complete']
    } else {
      return []
    }
  } else {
    if (assigneeCurrentVal.value == 'Hiring Lead') {
      return ['Submitter']
    } else if (assigneeCurrentVal.value == 'Fiscal') {
      return ['Submitter', 'Fiscal']
    } else if (assigneeCurrentVal.value == 'HR') {
      return ['Submitter', 'Fiscal', 'HR']
    } else if (assigneeCurrentVal.value == 'Complete') {
      return ['Submitter', 'Fiscal', 'HR', 'Complete']
    } else {
      return []
    }
  }
}

function assigneeLabel(assigneeType: 'CURRENT' | 'DB') {
  let aVal = assigneeType == 'CURRENT' ? assigneeCurrentVal.value : assignee.value

  if (aVal == 'None') {
    return 'Status: Not submitted'
  } else if (aVal == 'Submitter') {
    return 'Assigned to: ' + submitterName.value
  } else if (aVal == 'Hiring Lead') {
    return 'Assigned to: Hiring Lead'
  } else if (aVal == 'Fiscal') {
    return 'Assigned to: Fiscal'
  } else if (aVal == 'HR') {
    return 'Assigned to: HR'
  } else if (aVal == 'Complete') {
    return 'Status: Complete'
  } else {
    return ''
  }
}

function workerLabel() {
  if (['Temp Agency', 'Temp Non-Agency'].includes(workerType.value)) {
    return 'Temp Worker'
  } else {
    return workerType.value
  }
}

function workerNumberLabel() {
  return workerLabel() + ' Number'
}

let changes = ref(null) as Ref<TransitionChange[] | null>

let showErrorButton = ref(false)
let showErrorDialog = ref(false)
let errorDialogPosition = ref('top') as Ref<QDialogProps['position']>

let showChangesDialog = ref(false)

let showSendToSDSHiringLeadsDialog = ref(false)
let showSendToFiscalDialog = ref(false)
let showSendToHRDialog = ref(false)
let showSendToSTNDialog = ref(false)
let showAssigneeDialog = ref(false)
let sendDialogMessage = ref('')
let sendDialogUpdate = ref(false)
let reassignDialogMessage = ref('')

function formErrors() {
  return formErrorItems().length > 0
}

////////////////////////////
// Retrieve/Modify/Submit //
////////////////////////////

function retrieveEmployeeTransition() {
  return new Promise((resolve, reject) => {
    const t = currentEmployeeTransition()
    if (!t.pk) {
      // TODO: Load a workflow without a transition, and then load a transition
      // and the transition will not have yet loaded. See watch and onMounted
      // retrieveEmployeeTransition(). It should only be called once somehow.
      reject('Transition not yet loaded')
    }
    transitionPk.value = t.pk.toString()

    type.value = t.type
    typeCurrentVal.value = type.value
    workerType.value = t.worker_type
    workerTypeCurrentVal.value = workerType.value

    dateSubmitted.value = t.date_submitted
    submitterPk.value = t.submitter_pk
    submitterName.value = t.submitter_name
    submitterDivision.value = t.submitter_division

    currentEmployee.value = {
      pk: t.current_employee_pk, name: '', legal_name: t.current_employee_name
    }
    currentEmployeeCurrentVal.value = currentEmployee.value
    employeeFirstName.value = t.employee_first_name
    employeeFirstNameCurrentVal.value = employeeFirstName.value
    employeeMiddleInitial.value = t.employee_middle_initial
    employeeMiddleInitialCurrentVal.value = employeeMiddleInitial.value
    employeeLastName.value = t.employee_last_name
    employeeLastNameCurrentVal.value = employeeLastName.value
    employeePreferredName.value = t.employee_preferred_name
    employeePreferredNameCurrentVal.value = employeePreferredName.value
    employeeNumber.value = t.employee_number
    employeeID.value = t.employee_id
    employeeNumberCurrentVal.value = employeeNumber.value
    employeeIDCurrentVal.value = employeeID.value
    employeeEmail.value = t.employee_email
    employeeEmailCurrentVal.value = employeeEmail.value
    title.value = {pk: t.title_pk, name: t.title_name}
    titleCurrentVal.value = title.value
    fte.value = t.fte
    fteCurrentVal.value = fte.value
    hoursPerWeek.value = t.hours_per_week
    hoursPerWeekCurrentVal.value = hoursPerWeek.value
    hourlyRate.value = t.hourly_rate
    hourlyRateCurrentVal.value = hourlyRate.value
    salaryRange.value = t.salary_range
    salaryRangeCurrentVal.value = salaryRange.value
    salaryStep.value = t.salary_step
    salaryStepCurrentVal.value = salaryStep.value
    stipend.value = t.stipend
    stipendCurrentVal.value = stipend.value
    bilingual.value = t.bilingual
    bilingualCurrentVal.value = bilingual.value
    secondLanguage.value = t.second_language
    secondLanguageCurrentVal.value = secondLanguage.value
    manager.value = {pk: t.manager_pk, name: '', legal_name: t.manager_name}
    managerCurrentVal.value = manager.value
    unit.value = {pk: t.unit_pk, name: t.unit_name}
    unitCurrentVal.value = unit.value
    if (t.transition_date === null) {
      transitionDate.value = null
    } else {
      transitionDate.value = t.transition_date.replace('T', ' ')
    }
    transitionDateCurrentVal.value = transitionDate.value
    if (t.system_change_date === null) {
      systemChangeDate.value = null
    } else {
      systemChangeDate.value = t.system_change_date.replace('T', ' ')
      systemChangeDateDifferent.value = true
    }
    systemChangeDateCurrentVal.value = systemChangeDate.value
    schedule.value = t.schedule.split('')
    scheduleCurrentVal.value = schedule.value
    lwop.value = t.lwop
    lwopCurrentVal.value = lwop.value
    lwopDetails.value = t.lwop_details
    lwopDetailsCurrentVal.value = lwopDetails.value
    preliminaryHire.value = t.preliminary_hire
    preliminaryHireCurrentVal.value = preliminaryHire.value
    deleteProfile.value = t.delete_profile
    deleteProfileCurrentVal.value = deleteProfile.value
    officeLocation.value = t.office_location
    officeLocationCurrentVal.value = officeLocation.value
    cubicleNumber.value = t.cubicle_number
    cubicleNumberCurrentVal.value = cubicleNumber.value
    unionAffiliation.value = t.union_affiliation
    unionAffiliationCurrentVal.value = unionAffiliation.value
    teleworking.value = t.teleworking
    teleworkingCurrentVal.value = teleworking.value
    computerType.value = t.computer_type
    computerTypeCurrentVal.value = computerType.value
    computerGL.value = t.computer_gl
    computerGLCurrentVal.value = computerGL.value
    computerDescription.value = t.computer_description
    computerDescriptionCurrentVal.value = computerDescription.value
    phoneNumber.value = t.phone_number
    phoneNumberCurrentVal.value = phoneNumber.value
    phoneRequest.value = t.phone_request
    phoneRequestCurrentVal.value = phoneRequest.value
    phoneRequestData.value = t.phone_request_data
    phoneRequestDataCurrentVal.value = phoneRequestData.value
    loadCode.value = t.load_code
    loadCodeCurrentVal.value = loadCode.value
    cellPhone.value = t.cell_phone
    cellPhoneCurrentVal.value = cellPhone.value
    shouldDelete.value = t.should_delete
    shouldDeleteCurrentVal.value = shouldDelete.value
    extensionRemainActive.value = t.extension_remain_active
    extensionRemainActiveCurrentVal.value = extensionRemainActive.value
    reassignTo.value = t.reassign_to
    reassignToCurrentVal.value = reassignTo.value
    gasPINNeeded.value = t.gas_pin_needed
    gasPINNeededCurrentVal.value = gasPINNeeded.value
    oregonAccess.value = t.oregon_access
    oregonAccessCurrentVal.value = oregonAccess.value
    businessCards.value = t.business_cards
    businessCardsCurrentVal.value = businessCards.value
    proxCardNeeded.value = t.prox_card_needed
    proxCardNeededCurrentVal.value = proxCardNeeded.value
    mailboxNeeded.value = t.mailbox_needed
    mailboxNeededCurrentVal.value = mailboxNeeded.value
    if (t.access_emails_pk != -1) {
      showAccessEmails.value = true
      showAccessEmailsCurrentVal.value = true
    }
    accessEmails.value = {
      pk: t.access_emails_pk, name: '', legal_name: t.access_emails_name
    }
    accessEmailsCurrentVal.value = accessEmails.value
    specialInstructions.value = t.special_instructions
    specialInstructionsCurrentVal.value = specialInstructions.value
    fiscalField.value = t.fiscal_field
    fiscalFieldCurrentVal.value = fiscalField.value
    assignee.value = t.assignee
    assigneeCurrentVal.value = assignee.value

    changes.value = t.changes

    if (formErrors() && dateSubmitted.value) {
      showErrorButton.value = true
    }
    resolve('Retrieved employee transition')
  })
}

function valuesAreChanged(): boolean {
  if (
    type.value == typeCurrentVal.value &&
    workerType.value == workerTypeCurrentVal.value &&
    currentEmployee.value.pk == currentEmployeeCurrentVal.value.pk &&
    employeeFirstName.value == employeeFirstNameCurrentVal.value &&
    employeeMiddleInitial.value == employeeMiddleInitialCurrentVal.value &&
    employeeLastName.value == employeeLastNameCurrentVal.value &&
    employeePreferredName.value == employeePreferredNameCurrentVal.value &&
    employeeID.value == employeeIDCurrentVal.value &&
    employeeNumber.value == employeeNumberCurrentVal.value &&
    employeeEmail.value == employeeEmailCurrentVal.value &&
    title.value.pk == titleCurrentVal.value.pk &&
    fte.value == fteCurrentVal.value &&
    hoursPerWeek.value == hoursPerWeekCurrentVal.value &&
    hourlyRate.value == hourlyRateCurrentVal.value &&
    salaryRange.value == salaryRangeCurrentVal.value &&
    salaryStep.value == salaryStepCurrentVal.value &&
    stipend.value == stipendCurrentVal.value &&
    bilingual.value == bilingualCurrentVal.value &&
    secondLanguage.value == secondLanguageCurrentVal.value &&
    manager.value.pk == managerCurrentVal.value.pk &&
    unit.value.pk == unitCurrentVal.value.pk &&
    (
      // If both dates are null, they are the same
      (
        transitionDate.value == null && transitionDateCurrentVal.value == null
      ) ||
      // If both dates are not null, compare them as dates
      (
        !!transitionDate.value && !!transitionDateCurrentVal.value &&
        Date.parse(transitionDate.value) ==
        Date.parse(transitionDateCurrentVal.value)
      )
    ) &&
    (
      // If both dates are null, they are the same
      (
        systemChangeDate.value == null &&
        systemChangeDateCurrentVal.value == null
      ) ||
      // If both dates are not null, compare them as dates
      (
        !!systemChangeDate.value && !!systemChangeDateCurrentVal.value &&
        Date.parse(systemChangeDate.value) ==
        Date.parse(systemChangeDateCurrentVal.value)
      )
    ) &&
    schedule.value.sort().join('') == 
      scheduleCurrentVal.value.sort().join('') &&
    lwop.value == lwopCurrentVal.value &&
    lwopDetails.value == lwopDetailsCurrentVal.value &&
    preliminaryHire.value == preliminaryHireCurrentVal.value &&
    deleteProfile.value == deleteProfileCurrentVal.value &&
    officeLocation.value == officeLocationCurrentVal.value &&
    cubicleNumber.value == cubicleNumberCurrentVal.value &&
    unionAffiliation.value == unionAffiliationCurrentVal.value &&
    teleworking.value == teleworkingCurrentVal.value &&
    computerType.value == computerTypeCurrentVal.value &&
    computerGL.value == computerGLCurrentVal.value &&
    computerDescription.value == computerDescriptionCurrentVal.value &&
    phoneNumber.value == phoneNumberCurrentVal.value &&
    phoneRequest.value == phoneRequestCurrentVal.value &&
    phoneRequestData.value == phoneRequestDataCurrentVal.value &&
    loadCode.value == loadCodeCurrentVal.value &&
    cellPhone.value == cellPhoneCurrentVal.value &&
    shouldDelete.value == shouldDeleteCurrentVal.value &&
    extensionRemainActive.value == extensionRemainActiveCurrentVal.value &&
    reassignTo.value == reassignToCurrentVal.value &&
    gasPINNeeded.value == gasPINNeededCurrentVal.value &&
    oregonAccess.value == oregonAccessCurrentVal.value &&
    businessCards.value == businessCardsCurrentVal.value &&
    proxCardNeeded.value == proxCardNeededCurrentVal.value &&
    mailboxNeeded.value == mailboxNeededCurrentVal.value &&
    showAccessEmails.value == showAccessEmailsCurrentVal.value &&
    accessEmails.value.pk == accessEmailsCurrentVal.value.pk &&
    specialInstructions.value == specialInstructionsCurrentVal.value &&
    fiscalField.value == fiscalFieldCurrentVal.value
  ) {
    return false
  } else {
    return true
  }
}

function updateTransition() {
  return new Promise((resolve, reject) => {
    // Clean fields
    if (!fte.value) {
      fte.value = '0'
    }
    if (!hoursPerWeek.value) {
      hoursPerWeek.value = '0'
    }
    if (!bilingual.value) {
      secondLanguage.value = ''
    }
    const phoneNumberVal = phoneNumber.value == '(___) ___-____' ? '' :
      phoneNumber.value
    if (
      [
        'Reassign to:', 'Change name display to:'
      ].indexOf(phoneRequest.value) == -1
    ) {
      phoneRequestData.value = ''
    }
    if (!showAccessEmails.value) {
      accessEmails.value = emptyEmployee
    }

    let transitionDateFromForm: Date | undefined = undefined
    if (transitionDate.value) {
      transitionDateFromForm = new Date(transitionDate.value)
    }

    let systemChangeDateFromForm: Date | undefined = undefined
    if (systemChangeDate.value) {
      systemChangeDateFromForm = new Date(systemChangeDate.value)
    }

    // Update the DB
    workflowsStore.updateEmployeeTransition(transitionPk.value, {
      type: type.value,
      worker_type: workerType.value,
      submitter_pk: userStore.getEmployeeProfile.employee_pk,
      current_employee_pk: currentEmployee.value.pk,
      employee_first_name: employeeFirstName.value,
      employee_middle_initial: employeeMiddleInitial.value,
      employee_last_name: employeeLastName.value,
      employee_preferred_name: employeePreferredName.value,
      employee_id: employeeID.value,
      employee_number: employeeNumber.value,
      employee_email: employeeEmail.value,
      title_pk: title.value.pk,
      fte: fte.value,
      hours_per_week: hoursPerWeek.value,
      hourly_rate: hourlyRate.value,
      salary_range: salaryRange.value,
      salary_step: salaryStep.value,
      stipend: stipend.value,
      bilingual: bilingual.value,
      second_language: secondLanguage.value,
      manager_pk: manager.value.pk,
      unit_pk: unit.value.pk,
      transition_date: transitionDateFromForm,
      system_change_date: systemChangeDateFromForm,
      schedule: schedule.value.join(''),
      lwop: lwop.value,
      lwop_details: lwopDetails.value,
      preliminary_hire: preliminaryHire.value,
      delete_profile: deleteProfile.value,
      office_location: officeLocation.value,
      cubicle_number: cubicleNumber.value,
      union_affiliation: unionAffiliation.value,
      teleworking: teleworking.value,
      computer_type: computerType.value,
      computer_gl: computerGL.value,
      computer_description: computerDescription.value,
      phone_number: phoneNumberVal,
      phone_request: phoneRequest.value,
      phone_request_data: phoneRequestData.value,
      load_code: loadCode.value,
      cell_phone: cellPhone.value,
      should_delete: shouldDelete.value,
      extension_remain_active: extensionRemainActive.value,
      reassign_to: reassignTo.value,
      gas_pin_needed: gasPINNeeded.value,
      oregon_access: oregonAccess.value,
      business_cards: businessCards.value,
      prox_card_needed: proxCardNeeded.value,
      mailbox_needed: mailboxNeeded.value,
      access_emails_pk: accessEmails.value.pk,
      special_instructions: specialInstructions.value,
      fiscal_field: fiscalField.value
    })
    .then((t) => {
      typeCurrentVal.value = t.type
      workerTypeCurrentVal.value = t.worker_type

      dateSubmitted.value = t.date_submitted
      submitterPk.value = t.submitter_pk
      submitterName.value = t.submitter_name
      submitterDivision.value = t.submitter_division

      currentEmployeeCurrentVal.value = {
        pk: t.current_employee_pk, name: '', legal_name: t.current_employee_name
      }
      employeeFirstNameCurrentVal.value = t.employee_first_name
      employeeMiddleInitialCurrentVal.value = t.employee_middle_initial
      employeeLastNameCurrentVal.value = t.employee_last_name
      employeePreferredNameCurrentVal.value = t.employee_preferred_name
      employeeIDCurrentVal.value = t.employee_id
      employeeNumberCurrentVal.value = t.employee_number
      employeeEmailCurrentVal.value = t.employee_email
      titleCurrentVal.value = {pk: t.title_pk, name: t.title_name}
      fteCurrentVal.value = t.fte
      hoursPerWeekCurrentVal.value = t.hours_per_week
      hourlyRateCurrentVal.value = t.hourly_rate
      // We need to set salaryRange because integers are set as decimals
      salaryRange.value = t.salary_range
      salaryRangeCurrentVal.value = t.salary_range
      salaryStepCurrentVal.value = t.salary_step
      stipendCurrentVal.value = t.stipend
      bilingualCurrentVal.value = t.bilingual
      secondLanguageCurrentVal.value = t.second_language
      managerCurrentVal.value = {
        pk: t.manager_pk, name: '', legal_name: t.manager_name
      }
      unitCurrentVal.value = {pk: t.unit_pk, name: t.unit_name}
      transitionDateCurrentVal.value = t.transition_date
      systemChangeDateCurrentVal.value = t.system_change_date
      scheduleCurrentVal.value = t.schedule.split('')
      lwopCurrentVal.value = t.lwop
      lwopDetailsCurrentVal.value = t.lwop_details
      preliminaryHireCurrentVal.value = t.preliminary_hire
      deleteProfileCurrentVal.value = t.delete_profile
      officeLocationCurrentVal.value = t.office_location
      cubicleNumberCurrentVal.value = t.cubicle_number
      unionAffiliationCurrentVal.value = t.union_affiliation
      teleworkingCurrentVal.value = t.teleworking
      computerTypeCurrentVal.value = t.computer_type
      computerGLCurrentVal.value = t.computer_gl
      computerDescriptionCurrentVal.value = t.computer_description
      phoneNumberCurrentVal.value = t.phone_number
      phoneRequestCurrentVal.value = t.phone_request
      phoneRequestDataCurrentVal.value = t.phone_request_data
      loadCodeCurrentVal.value = t.load_code
      cellPhoneCurrentVal.value = t.cell_phone
      shouldDeleteCurrentVal.value = t.should_delete
      extensionRemainActiveCurrentVal.value = t.extension_remain_active
      reassignToCurrentVal.value = t.reassign_to
      gasPINNeededCurrentVal.value = t.gas_pin_needed
      oregonAccessCurrentVal.value = t.oregon_access
      businessCardsCurrentVal.value = t.business_cards
      proxCardNeededCurrentVal.value = t.prox_card_needed
      mailboxNeededCurrentVal.value = t.mailbox_needed
      showAccessEmailsCurrentVal.value = showAccessEmails.value
      accessEmailsCurrentVal.value = {
        pk: t.access_emails_pk, name: '', legal_name: t.access_emails_name
      }
      specialInstructionsCurrentVal.value = t.special_instructions
      fiscalFieldCurrentVal.value = t.fiscal_field

      changes.value = t.changes

      const routePk = getRoutePk(route)
      if (routePk) {
        workflowsStore.getCurrentWorkflowInstance(routePk)
          .catch(e => {
            console.error(
              'Error getting getCurrentWorkflowInstance after updating',
              'EmployeeTransition:',
              e
            )
            reject(e)
          })
      }

      if (formErrors()) {
        showErrorButton.value = true
      }

      // TODO: If a new computer is required, send an email to the IT department

      if (!!t.title_name) {
        quasar.notify(
          `Updated Employee Transition for ${t.title_name} Position`
        )
      } else {
        quasar.notify('Updated Employee Transition')
      }

      // Signal to WorkflowInstanceDetail that the transition was assigned.
      bus.emit('transitionReassigned', Math.random())

      resolve('Updated')
    })
    .catch(e => {
      quasar.notify({
        message: e,
        color: 'negative',
        icon: 'report_problem',
        timeout: 5000
      })
      reject(e)
    })
  })
}

function formErrorItems(): Array<[string, string]> {
  let errorItems: Array<[string, string]> = []
  // New, returning, and changing employees must have an office location
  if (
    ['New', 'Return', 'Change/Modify'].indexOf(typeCurrentVal.value) != -1 &&
    !officeLocationCurrentVal.value
  ) {
    errorItems.push(['office-location', 'Provide an office location'])
  }
  // New computers must have a GL code
  if (computerTypeCurrentVal.value == 'New' && !computerGLCurrentVal.value) {
    errorItems.push(
      ['computer-type', 'Provide a valid GL code for computer purchase']
    )
  }
  // Repurposed computers must have a description
  if (
    computerTypeCurrentVal.value == 'Repurposed' &&
    !computerDescriptionCurrentVal.value
  ) {
    errorItems.push(
      ['computer-type', 'Provide a description of existing computer']
    )
  }
  return errorItems
}

function setAssignee(option: string) {
  assignee.value = option
}

/////////////////////////////////
// Field view/edit permissions //
/////////////////////////////////

function formSubmitted() {
  return !!dateSubmitted.value
}

function employeeIsSubmitter() {
  return userStore.getEmployeeProfile.employee_pk == submitterPk.value
}

// Only HR can edit employee number fields. Anyone can view them.
function canEditEmployeeNumberFields() {
  return cookies.get('is_hr_employee') == 'true'
}

// Original submitter can view/edit salary fields.
// If the form is submitted, only the submitter, hiring manager, HR, fiscal, and
// SDS hiring leads can view/edit them.
// All others can neither view nor edit them.
function canViewSalaryFields() {
  return !formSubmitted() ||
    employeeIsSubmitter() ||
    userStore.getEmployeeProfile.employee_pk == manager.value.pk ||
    cookies.get('is_hr_employee') == 'true' ||
    cookies.get('is_fiscal_employee') == 'true' ||
    cookies.get('is_sds_hiring_lead') == 'true'
}

// If the form is submitted, only the original submitter can edit manager field.
// Anyone can view it.
function canEditManagerField() {
  return !formSubmitted() || employeeIsSubmitter() ||
    cookies.get('is_hr_employee') == 'true'
}

// Only fiscal can edit the fiscal field. Anyone can view it.
function canEditFiscalField() {
  return cookies.get('is_fiscal_employee') == 'true'
}

// If the form is submitted, other fields are editable only by submitter, hiring
// manager, HR, fiscal, and SDS hiring leads.
function canEditOtherFields() {
  return !formSubmitted() ||
    employeeIsSubmitter() ||
    userStore.getEmployeeProfile.employee_pk == manager.value.pk ||
    cookies.get('is_hr_employee') == 'true' ||
    cookies.get('is_fiscal_employee') == 'true' ||
    cookies.get('is_sds_hiring_lead') == 'true'
}

// Can only update the assignee if there is an assignee that is not the
// submitter and the current user is in the assignee group.
function canUpdateAssignee() {
  const assignee = assigneeCurrentVal.value
  if (assignee == 'Submitter') {
    return false // No one to assign back to
  } else if (assignee == 'Hiring Lead') {
    return cookies.get('is_sds_hiring_lead') == 'true'
  } else if (assignee == 'Fiscal') {
    return cookies.get('is_fiscal_employee') == 'true'
  } else if (assignee == 'HR') {
    return cookies.get('is_hr_employee') == 'true'
  } else if (assignee == 'Complete') {
    return false
  } else {
    return false
  }
}

function canSendToHiringLeads() {
  return assigneeCurrentVal.value == 'Submitter' && employeeIsSubmitter() &&
    cookies.get('division') == 'Senior & Disability Services'
}

function canSendToFiscal() {
  // GS employees send to fiscal. SDS managers send to SDS hiring leads.
  const division = cookies.get('division')
  // They function the same, so treat AS as GS
  const isGS = [
    'Administrative Services', 'Government Services', 'Test Division'
  ].indexOf(division) != -1
  const isSDS = division == 'Senior & Disability Services'
  if (!(isGS || isSDS)) {
    userStore.logError({
      message: `User does not seem to have a correct division: ${division}`,
      location: 'EmployeeTransitionDetail: canSendToFiscal'
    })
  }
  const isGSSubmitter = employeeIsSubmitter() && isGS
  const isHiringLeadAndAssignee = assigneeCurrentVal.value == 'Hiring Lead' &&
    cookies.get('is_sds_hiring_lead') == 'true'
  const isGSSubmitterAndAssignee = assigneeCurrentVal.value == 'Submitter' &&
    isGSSubmitter
  return isHiringLeadAndAssignee || isGSSubmitterAndAssignee
}

function canSendToHR() {
  return assigneeCurrentVal.value == 'Fiscal' &&
    cookies.get('is_fiscal_employee') == 'true'

}

function canSendToTransitionNews() {
  return ['HR', 'Complete'].indexOf(assigneeCurrentVal.value) != -1 &&
    cookies.get('is_hr_employee') == 'true'

}

////////////////////////
// Interact with form //
////////////////////////

function emailInUse(email: string): boolean {
  const emailList = peopleStore.employeeEmailList
  if (emailList.indexOf(email) > -1) {
    return true
  } else {
    return false
  }
}

function suggestEmail(): void {
  // Create first pass at suggestion
  let suggestedEmail = ''
  let firstChar = ''
  if (employeePreferredName.value) {
    firstChar = employeePreferredName.value.charAt(0).toLowerCase()
  } else if (employeeFirstName.value) {
    firstChar = employeeFirstName.value.charAt(0).toLowerCase()
  } else {
    return
  }
  if (employeeLastName.value) {
    suggestedEmail =
    `${firstChar}${employeeLastName.value.toLowerCase()}@lcog-or.gov`
  } else {
    return
  }

  // Check if email is already in use
  if (emailInUse(suggestedEmail)) {
    // If so, add middle initial and check again
    if (employeeMiddleInitial.value) {
      const mi = employeeMiddleInitial.value.toLowerCase()
      const ln = employeeLastName.value.toLowerCase()
      suggestedEmail = `${firstChar}${mi}${ln}@lcog-or.gov`
    } else {
      return
    }
    if (emailInUse(suggestedEmail)) {
      // If so, add a number to the end and check again
      let i = 1
      while (emailInUse(`${suggestedEmail}${i}`)) {
        i++
      }
      suggestedEmail = `${suggestedEmail}${i}`
    }
  }

  // Set the value
  if (!employeeEmail.value) {
    employeeEmail.value = suggestedEmail
  }
}

function openErrorDialog(position: QDialogProps['position']) {
  errorDialogPosition.value = position
  showErrorDialog.value = true
}

function clickedErrorItem(item: [string, string]) {
  showErrorDialog.value = false
  const element = document.getElementById(item[0])
  if (!!element) {
    const target = getScrollTarget(element)
    const offset = element.offsetTop - 50
    const duration = 500
    setVerticalScrollPosition(target, offset, duration)
  }
}

function handlePrint() {
  const pk = getRoutePk(route)
  if (!pk) {
    router.push('/')
  } else {
    workflowsStore.getCurrentWorkflowInstance(pk)
      .then(() => {
        const wfInstance: WorkflowInstance =
          workflowsStore.currentWorkflowInstance
        if (!wfInstance) {
          console.error(
            'Workflow instance does not seem to exist. Redirecting...'
          )
          router.push({ name: 'workflow-dashboard' })
            .catch(e => {
              console.error(
                'Error navigating to workflow dashboard upon not finding a',
                'matching Workflow Instance:',
                e
              )
            })
          return
        }
        retrieveEmployeeTransition().then(() => {
          // Print the screen
          window.print()
        })
      })
      .catch(e => {
        console.error('Error retrieving workflow instance', e)
        router.push({ name: 'workflow-transition-form', params: { pk: pk } })
          .catch(e => {
            console.error(
              'Error navigating to transition form upon not finding a matching',
              'Workflow Instance:',
              e
            )
          })
      })
  }
}

function showMapButton() {
  return [
    'Schaefers - 1st Floor', 'Schaefers - 2nd Floor', 'Schaefers - 3rd Floor'
  ].indexOf(officeLocation.value) != -1
}

function navigateToMap() {
  let route = ''
  switch(officeLocation.value) {
    case 'Schaefers - 1st Floor':
      route = 'schaefers/1'
      break
    case 'Schaefers - 2nd Floor':
      route = 'schaefers/2'
      break
    case 'Schaefers - 3rd Floor':
      route = 'schaefers/3'
      break
    default:
      return
  }
  const url = `/desk-reservation/${route}`
  window.open(url, '_blank')
}

////////////////////////
// Send notifications //
////////////////////////

function sendMailboxNotificationEmail() {
  workflowsStore.sendMailboxNotificationEmail(transitionPk.value, {
    senderName: userStore.getEmployeeProfile.name,
    senderEmail: userStore.getEmployeeProfile.email,
    transitionUrl: route.fullPath
  })
    .then(() => {
      quasar.notify({
        message: 'Sent Mailbox Notification Email',
        color: 'positive',
        icon: 'send'
      })
    })
    .catch(e => {
      console.error('Error sending Mailbox Notification Email', e)
      quasar.notify({
        message: 'Error sending Mailbox Notification Email',
        color: 'negative',
        icon: 'report_problem'
      })
    })
}

function onSubmitSendDialog(t: 'SDS'|'FI'|'HR'|'STN'|'ASSIGN') {
  // Send mailbox notification email if needed
  if (
    t == 'STN' &&
    employeeID.value == 'CLSD' &&
    mailboxNeeded.value == true &&
    ['New', 'Return', 'Change/Modify'].indexOf(type.value) != -1
  ) {
    sendMailboxNotificationEmail()
  }
  
  const extraMessage = t == 'ASSIGN' ? reassignDialogMessage.value : sendDialogMessage.value
  workflowsStore.sendTransitionToEmailList(transitionPk.value, {
    type: t,
    reassignTo: assignee.value,
    update: sendDialogUpdate.value,
    extraMessage,
    senderName: userStore.getEmployeeProfile.name,
    senderEmail: userStore.getEmployeeProfile.email,
    transitionUrl: route.fullPath
  })
    .then(() => {
      quasar.notify({
        message: 'Sent',
        color: 'positive',
        icon: 'send'
      })
      showSendToSDSHiringLeadsDialog.value = false
      showSendToFiscalDialog.value = false
      showSendToHRDialog.value = false
      showSendToSTNDialog.value = false
      showAssigneeDialog.value = false
      sendDialogUpdate.value = false
      sendDialogMessage.value = ''
      reassignDialogMessage.value = ''
      // Signal to WorkflowInstanceDetail that the transition was assigned or
      // completed, in which case we need to get the newly created process
      // instances.
      bus.emit('transitionReassigned', Math.random())
    })
    .catch(e => {
      console.error('Error sending email', e)
      quasar.notify({
        message: 'Error sending email',
        color: 'negative',
        icon: 'report_problem'
      })
    })
}

/////////////////////////
// Vue Lifecycle Hooks //
/////////////////////////

watch(() => bus.bus.value.get('workflowInstanceRetrieved'), () => {
  // TODO: We should only set state once, but when you load /transition
  // this runs twice
  retrieveEmployeeTransition()
})

onMounted(() => {
  if (props.print) {
    handlePrint()
  } else {
    retrieveEmployeeTransition()
  }

  if (!peopleStore.employeeEmailList.length) {
    peopleStore.getEmployeeEmailList()
      .catch(e => {
        console.error('Error retrieving simple employee list', e)
      })
  }
})
</script>

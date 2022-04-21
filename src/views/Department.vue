<template>
  <div>
    <div v-if="department.deptName" class="d-flex flex-row flex-wrap justify-space-between">
      <h1 id="page-title" class="mr-5">
        {{ department.deptName }}
        <span v-if="department.catalogListings">
          ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})
        </span>
        <span v-if="selectedTerm">
          - {{ $_.get(selectedTerm, 'name') }}
        </span>
      </h1>
      <div
        v-if="$currentUser.isAdmin"
        class="d-flex align-baseline flex-grow-1 justify-end"
      >
        <label
          id="select-term-label"
          for="select-term"
          class="align-self-baseline text-nowrap pr-3"
        >
          Previous terms:
        </label>
        <select
          id="select-term"
          v-model="selectedTermId"
          class="native-select-override select-term my-2 px-3"
          :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
          :disabled="disableControls || loading"
          @change="onChangeTerm"
        >
          <option
            v-for="term in availableTerms"
            :id="`term-option-${term.id}`"
            :key="term.id"
            :value="term.id"
          >
            {{ term.name }}
          </option>
        </select>
      </div>
    </div>
    <v-container v-if="!loading" class="mx-0 px-0 pb-6" fluid>
      <v-row justify="start">
        <v-col cols="12" md="5">
          <h2 class="pb-1 px-2">Department Contacts</h2>
          <v-btn
            v-if="$currentUser.isAdmin && !isCreatingNotification"
            id="open-notification-form-btn"
            class="ma-2 secondary text-capitalize"
            :disabled="disableControls || $_.isEmpty(contacts)"
            @click="() => isCreatingNotification = true"
          >
            Send notification
          </v-btn>
          <NotificationForm
            v-if="$currentUser.isAdmin && isCreatingNotification"
            :after-send="afterSendNotification"
            :on-cancel="cancelSendNotification"
            :recipients="[notificationRecipients]"
          />
          <v-btn
            class="float-right text-capitalize mt-2 mr-4"
            color="primary--text"
            text
            @click="() => contactsPanel = []"
          >
            Collapse All
            <v-icon class="flip-horizontally ml-1">mdi-collapse-all-outline</v-icon>
          </v-btn>
          <v-expansion-panels
            v-model="contactsPanel"
            flat
            focusable
            hover
            multiple
          >
            <DepartmentContact
              v-for="(contact, index) in contacts"
              :key="contact.id"
              :contact="contact"
              :index="index"
            />
          </v-expansion-panels>
          <v-btn
            v-if="$currentUser.isAdmin && !isAddingContact"
            id="add-dept-contact-btn"
            class="text-capitalize pl-2 my-1 mx-2"
            color="tertiary"
            text
            @click="() => isAddingContact = true"
          >
            <v-icon>mdi-plus-thick</v-icon>
            Add Contact
          </v-btn>
          <EditDepartmentContact
            v-if="$currentUser.isAdmin && isAddingContact"
            :id="`add-department-contact`"
            :after-save="afterSaveContact"
            :on-cancel="onCancelAddContact"
          />
        </v-col>
        <v-col cols="12" md="7">
          <DepartmentNote v-if="$currentUser.isAdmin" />
        </v-col>
      </v-row>
    </v-container>
    <v-container v-if="!loading" class="mx-0 px-0 pb-6" fluid>
      <v-row>
        <v-col cols="12" sm="6">
          <div class="d-flex flex-row flex-grow-1 align-baseline mb-4">
            <select
              id="select-course-actions"
              v-model="selectedCourseAction"
              aria-labelledby="action-option-label"
              class="native-select-override"
              :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
              :disabled="disableControls"
            >
              <option
                id="action-option-label"
                :key="0"
                disabled
                :value="undefined"
              >
                Course Actions
              </option>
              <option
                v-for="(action, index) in courseActions"
                :id="`action-option-${action.value}`"
                :key="index + 1"
                :value="action.value"
              >
                {{ action.text }}
              </option>
            </select>
            <v-btn
              id="apply-course-action-btn"
              class="mx-2"
              color="secondary"
              :disabled="!selectedCourseAction || !selectedEvaluationIds.length || (bulkUpdateOptions.evalDatesEnabled && !bulkUpdateOptions.startDate)"
              @click="applyCourseAction"
            >
              Apply
            </v-btn>
          </div>
          <div v-if="selectedCourseAction === 'duplicate'" class="mb-4">
            <v-checkbox
              v-model="bulkUpdateOptions.midtermFormEnabled"
              class="text-nowrap"
              color="tertiary"
              hide-details="auto"
              label="Use midterm department forms"
            />
            <div class="d-flex align-center mt-2">
              <v-checkbox
                v-model="bulkUpdateOptions.evalDatesEnabled"
                class="text-nowrap mt-0 pt-0"
                color="tertiary"
                label="Set evaluation start date:"
                hide-details="auto"
              />
              <c-date-picker
                v-model="bulkUpdateOptions.startDate"
                class="mx-3"
                :min-date="$moment($config.currentTermDates.begin).toDate()"
                :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
                title-position="left"
              >
                <template v-slot="{ inputValue, inputEvents }">
                  <input
                    class="input-override my-0"
                    :class="$vuetify.theme.dark ? 'dark' : 'light'"
                    :value="inputValue"
                    v-on="inputEvents"
                  />
                </template>
              </c-date-picker>
            </div>
          </div>
          <v-dialog
            id="error-dialog"
            v-model="errorDialog"
            width="400"
            role="alertdialog"
            aria-labelledby="error-dialog-title"
            aria-describedby="error-dialog-text"
          >
            <v-card>
              <v-card-title id="error-dialog-title" tabindex="-1">Error</v-card-title>
              <v-card-text id="error-dialog-text" class="pt-3">{{ errorDialogText }}</v-card-text>
              <div class="d-flex pa-2">
                <div class="mr-2">
                  <v-btn
                    id="error-dialog-ok-btn"
                    color="primary"
                    @click="dismissErrorDialog"
                    @keypress.enter.prevent="dismissErrorDialog"
                  >
                    OK
                  </v-btn>
                </div>
              </div>
            </v-card>
          </v-dialog>
        </v-col>
        <v-col cols="12" sm="6">
          <div class="d-flex flex-grow-1 align-baseline justify-end mb-4">
            <v-btn
              v-if="!isAddingSection"
              id="add-course-section-btn"
              class="text-capitalize pl-2 mt-1"
              color="tertiary"
              text
              @click="() => isAddingSection = true"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add Course Section
            </v-btn>
            <AddCourseSection
              v-if="isAddingSection"
              id="add-course-section"
              :evaluations="evaluations"
              :on-submit="addCourseSection"
              :on-cancel="cancelAddSection"
            />
          </div>
        </v-col>
      </v-row>
      <v-card outlined class="elevation-1">
        <EvaluationTable :evaluations="evaluations" :update-evaluation="updateEvaluation" />
      </v-card>
    </v-container>
  </div>
</template>

<script>
import {addSection, getSectionEvaluations, updateEvaluations} from '@/api/departments'
import AddCourseSection from '@/components/evaluation/AddCourseSection.vue'
import Context from '@/mixins/Context.vue'
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import NotificationForm from '@/components/admin/NotificationForm'

export default {
  name: 'Department',
  components: {
    AddCourseSection,
    DepartmentContact,
    DepartmentNote,
    EditDepartmentContact,
    EvaluationTable,
    NotificationForm
  },
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    availableTerms: undefined,
    bulkUpdateOptions: {
      evalDatesEnabled: false,
      midtermFormEnabled: false,
      startDate: null,
    },
    contactsPanel: [],
    courseActions: [
      {'text': 'Mark for review', 'value': 'mark'},
      {'text': 'Mark as confirmed', 'value': 'confirm'},
      {'text': 'Unmark', 'value': 'unmark'},
      {'text': 'Duplicate', 'value': 'duplicate'},
      {'text': 'Ignore', 'value': 'ignore'}
    ],
    department: {},
    errorDialog: false,
    errorDialogText: null,
    evaluations: [],
    isAddingContact: false,
    isAddingSection: false,
    isCreatingNotification: false,
    selectedCourseAction: undefined,
    selectedEvaluationIds: [],
    selectedTermId: undefined
  }),
  computed: {
    notificationRecipients() {
      return {
        'deptName': this.department.deptName,
        'deptId': this.department.id,
        'recipients': this.$_.filter(this.contacts, 'canReceiveCommunications')
      }
    }
  },
  created() {
    this.availableTerms = this.$config.availableTerms
    this.selectedTermId = this.$config.currentTermId
    this.$root.$on('update-evaluations-selected', this.updateEvaluationsSelected)
    this.refresh()
  },
  methods: {
    addCourseSection(courseNumber) {
      this.isAddingSection = false
      addSection(this.department.id, courseNumber).then(this.refresh(`Section ${courseNumber} added.`))
    },
    afterSaveContact() {
      this.isAddingContact = false
      this.alertScreenReader('Contact saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    afterSendNotification() {
      this.isCreatingNotification = false
      this.snackbarOpen('Notification sent.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    applyCourseAction() {
      let fields = null
      if (this.selectedCourseAction === 'duplicate') {
        fields = {}
        if (this.bulkUpdateOptions.midtermFormEnabled) {
          fields.midterm = 'true'
        }
        if (this.bulkUpdateOptions.evalDatesEnabled) {
          const duration = (this.$config.currentTermDates.begin + 77) > this.bulkUpdateOptions.startDate ? 13 : 20
          fields.endDate = this.$moment(this.bulkUpdateOptions.startDate).add(duration, 'days').format('YYYY-MM-DD')
        }
      }
      if (this.selectedCourseAction !== 'confirm' || this.validateConfirmable(this.selectedEvaluationIds, fields.departmentFormId, fields.evaluationTypeId)) {
        updateEvaluations(
          this.department.id,
          this.selectedCourseAction,
          this.selectedEvaluationIds,
          fields
        ).then(() => this.refresh(), error => this.showErrorDialog(error.response.data.message))
      }
    },
    cancelAddSection() {
      this.isAddingSection = false
      this.alertScreenReader('Section lookup canceled.')
      this.$putFocusNextTick('add-course-section-btn')
    },
    cancelSendNotification() {
      this.isCreatingNotification = false
      this.alertScreenReader('Notification canceled.')
    },
    dismissErrorDialog() {
      this.errorDialog = false
      this.errorDialogText = null
    },
    onCancelAddContact() {
      this.isAddingContact = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    onChangeTerm(event) {
      const term = this.$_.find(this.availableTerms, ['id', event.target.value])
      this.alertScreenReader(`Loading ${this.$_.get(term, 'name', 'term')}`)
      this.refresh()
      this.$putFocusNextTick('select-term')
    },
    refresh(screenreaderAlert) {
      this.$loading()
      const departmentId = this.$_.get(this.$route, 'params.departmentId')
      const termId = this.selectedTermId
      this.init({departmentId, termId}).then(department => {
        this.department = department
        this.$_.each(department.evaluations, e => {
          e.isSelected = false
          // When sorting by course number, keep cross-listings with home sections.
          if (e.crossListedWith && e.foreignDepartmentCourse) {
            e.sortableCourseNumber = `${e.crossListedWith}-${e.courseNumber}`
          } else if (e.roomSharedWith && e.foreignDepartmentCourse) {
            e.sortableCourseNumber = `${e.roomSharedWith}-${e.courseNumber}`
          } else {
            e.sortableCourseNumber = e.courseNumber
          }
        })
        this.evaluations = this.$_.sortBy(department.evaluations, 'sortableCourseNumber')
        this.$ready(`${this.department.deptName} ${this.$_.get(this.selectedTerm, 'name')}`, screenreaderAlert)
      })
    },
    showErrorDialog(text) {
      this.errorDialog = true
      this.errorDialogText = text
    },
    updateEvaluation(evaluationId, sectionId, fields) {
      this.alertScreenReader('Saving evaluation row.')
      return new Promise(resolve => {
        if (fields.status === 'confirmed' && !this.validateConfirmable([evaluationId], fields.departmentFormId, fields.evaluationTypeId)) {
          resolve()
        } else {
          updateEvaluations(this.department.id, 'edit', [evaluationId], fields).then(() => {
            getSectionEvaluations(this.department.id, sectionId).then(data => {
              let sectionIndex = this.$_.findIndex(this.evaluations, ['courseNumber', sectionId])
              if (sectionIndex === -1) {
                sectionIndex = this.evaluations.length
              }
              const sectionCount = this.$_.filter(this.evaluations, ['courseNumber', sectionId]).length
              this.evaluations.splice(sectionIndex, sectionCount, ...data)
              this.alertScreenReader('Changes saved.')
              resolve()
            })
          }, error => {
            this.showErrorDialog(error.response.data.message)
            resolve()
          })
        }
      })
    },
    updateEvaluationsSelected() {
      this.selectedEvaluationIds = this.$_.reduce(this.evaluations, (ids, e) => {
        if (e.isSelected) {
          ids.push(e.id)
        }
        return ids
      }, [])
    },
    validateConfirmable(evaluationIds, departmentFormId, evaluationTypeId) {
      if (this.$_.some(this.evaluations, e => this.$_.includes(evaluationIds, e.id) && (!(departmentFormId && e.departmentForm) || !(evaluationTypeId && e.evaluationType)))) {
        this.showErrorDialog('Cannot confirm evaluations with missing fields.')
        return false
      }
      return true
    }
  }
}
</script>

<style scoped>
.select-term {
  max-width: 200px;
}
</style>
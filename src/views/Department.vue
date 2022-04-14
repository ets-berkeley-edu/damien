<template>
  <div v-if="!loading">
    <v-row>
      <v-col cols="12" md="7" class="d-flex justify-start">
        <h1 id="page-title">
          {{ department.deptName }}
          ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})
          - {{ $_.get(selectedTerm, 'name') }}
        </h1>
      </v-col>
      <v-col
        v-if="$currentUser.isAdmin"
        cols="12"
        md="5"
        class="d-flex justify-end"
      >
        <label id="select-term-label" for="select-term" class="pa-3">
          Previous terms:
        </label>
        <v-select
          id="select-term"
          v-model="selectedTermId"
          :disabled="disableControls"
          item-text="name"
          item-value="id"
          :items="availableTerms"
          label="Select..."
          solo
          @change="refresh"
        >
          <span :id="`term-option-${data.item.id}`" slot="item" slot-scope="data">{{ data.item.name }}</span>
        </v-select>
      </v-col>
    </v-row>
    <v-container class="mx-0 px-0 pb-6">
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
        <v-col cols="12" md="7"><DepartmentNote /></v-col>
      </v-row>
    </v-container>
    <v-row>
      <v-col cols="12" md="4" class="mb-4">
        <v-select
          id="select-course-actions"
          v-model="selectedCourseAction"
          item-text="text"
          item-value="value"
          :items="courseActions"
          label="Course Actions"
          hide-details="auto"
          solo
        >
        </v-select>
        <div v-if="selectedCourseAction === 'duplicate'" class="my-4">
          <v-checkbox
            v-model="bulkUpdateOptions.midtermFormEnabled"
            hide-details="auto"
            label="Use midterm department forms"
          />
          <div class="d-flex">
            <v-checkbox
              v-model="bulkUpdateOptions.evalDatesEnabled"
              label="Set evaluation start date:"
              hide-details="auto"
            />
            <c-date-picker
              v-model="bulkUpdateOptions.startDate"
              :min-date="$moment($config.currentTermDates.begin).toDate()"
              :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
              title-position="left"
            >
              <template v-slot="{ inputValue, inputEvents }">
                <input
                  class="input-override"
                  :value="inputValue"
                  v-on="inputEvents"
                /> 
              </template>
            </c-date-picker>
          </div>
        </div>
      </v-col>
      <v-col cols="12" md="4">
        <v-btn
          :disabled="!selectedCourseAction || !selectedEvaluationIds.length || (bulkUpdateOptions.evalDatesEnabled && !bulkUpdateOptions.startDate)"
          @click="applyCourseAction"
        >
          Apply
        </v-btn>
      </v-col>
      <v-col cols="12" md="4">
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
      </v-col>
    </v-row>
    <v-card outlined class="elevation-1">
      <EvaluationTable :evaluations="evaluations" :update-evaluation="updateEvaluation" />
    </v-card>
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
      this.alertScreenReader('Notification sent.')
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
      updateEvaluations(
        this.department.id,
        this.selectedCourseAction,
        this.selectedEvaluationIds,
        fields
      ).then(this.refresh)
    },
    cancelAddSection() {
      this.isAddingSection = false
      this.alertScreenReader('Section lookup canceled.')
    },
    cancelSendNotification() {
      this.isCreatingNotification = false
      this.alertScreenReader('Notification canceled.')
    },
    onCancelAddContact() {
      this.isAddingContact = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
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
    updateEvaluation(evaluationId, sectionId, fields) {
      this.alertScreenReader('Saving evaluation row.')
      return new Promise(resolve => {
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
        })
      })
    },
    updateEvaluationsSelected() {
      this.selectedEvaluationIds = this.$_.reduce(this.evaluations, (ids, e) => {
        if (e.isSelected) {
          ids.push(e.id)
        }
        return ids
      }, [])
    }
  }
}
</script>

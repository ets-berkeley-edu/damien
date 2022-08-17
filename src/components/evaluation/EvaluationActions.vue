<template>
  <div class="d-flex align-center">
    <div class="d-flex">
      <template v-for="(action, key) in courseActions">
        <v-btn
          :id="`apply-course-action-btn-${key}`"
          :key="key"
          class="position-relative text-capitalize text-nowrap px-2"
          :color="$vuetify.theme.dark ? 'tertiary' : 'secondary'"
          :disabled="disableControls || !allowEdits || !selectedEvaluationIds.length || isLoading || isInvalidAction(action)"
          text
          @click.stop="action.apply(key)"
          @keypress.enter.prevent="action.apply(key)"
        >
          <span v-if="!isLoading">{{ action.text }}</span>
        </v-btn>
        <v-divider
          v-if="key === 'ignore' && !isLoading"
          :key="`${key}-divider`"
          class="align-self-stretch primary--text separator ma-2"
          inset
          role="presentation"
          vertical
        ></v-divider>
      </template>
      <v-progress-circular
        v-if="isLoading"
        :indeterminate="true"
        rotate="5"
        size="20"
        width="3"
        color="tertiary"
        class="ma-2 pl-5"
      ></v-progress-circular>
    </div>
    <v-dialog
      id="duplicate-row-dialog"
      v-model="isDuplicating"
      aria-labelledby="duplicate-row-dialog-title"
      class="overflow-y-visible"
      width="500"
    >
      <v-card>
        <v-card-title id="duplicate-row-dialog-title" tabindex="-1">Duplicate</v-card-title>
        <v-card-text>
          <div class="d-flex align-center mt-2">
            <PersonLookup
              v-if="isDuplicating"
              id="bulk-duplicate-instructor-lookup-autocomplete"
              :disabled="disableControls"
              :instructor-lookup="true"
              placeholder="Instructor name or UID"
              :on-select-result="selectInstructor"
              :required="isInstructorRequired"
              solo
            />
          </div>
          <v-checkbox
            v-if="midtermFormAvailable"
            v-model="bulkUpdateOptions.midtermFormEnabled"
            class="text-nowrap"
            color="tertiary"
            :disabled="disableControls"
            hide-details
            label="Use midterm department forms"
            :ripple="false"
          />
          <div class="my-4">
            <label
              id="bulk-duplicate-select-type-label"
              for="bulk-duplicate-select-type"
              class="v-label d-block py-1"
            >
              Evaluation Type:
            </label>
            <select
              id="bulk-duplicate-select-type"
              v-model="bulkUpdateOptions.evaluationType"
              class="native-select-override light d-block mx-auto"
              :disabled="disableControls"
            >
              <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
            </select>
          </div>
          <div class="d-flex align-center mt-2">
            <label
              for="bulk-duplicate-start-date"
              class="v-label"
              :class="$vuetify.theme.dark ? 'theme--dark' : 'theme--light'"
            >
              Evaluation start date:
            </label>
            <c-date-picker
              v-model="bulkUpdateOptions.startDate"
              class="mx-3"
              :min-date="$moment(selectedTermValidDates.begin).toDate()"
              :max-date="$moment(selectedTermValidDates.end).subtract(13, 'days').toDate()"
              :popover="{positionFixed: true}"
              title-position="left"
            >
              <template #default="{ inputValue, inputEvents }">
                <input
                  id="bulk-duplicate-start-date"
                  class="datepicker-input input-override my-0"
                  :class="$vuetify.theme.dark ? 'dark' : 'light'"
                  :disabled="disableControls"
                  maxlength="10"
                  minlength="10"
                  :value="inputValue"
                  v-on="inputEvents"
                />
              </template>
            </c-date-picker>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <div class="d-flex pa-2">
            <v-btn
              id="apply-course-action-btn"
              class="mt-2 mr-2"
              color="secondary"
              :disabled="disableApplyDuplicate"
              @click="applyAction('duplicate')"
              @keypress.enter.prevent="applyAction('duplicate')"
            >
              <span v-if="!isLoading">Apply</span>
            </v-btn>
            <v-btn
              id="cancel-duplicate-btn"
              class="mt-2 mr-2"
              :disabled="disableControls"
              @click="cancelDuplicate"
              @keypress.enter.prevent="cancelDuplicate"
            >
              Cancel
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {updateEvaluations} from '@/api/departments'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationActions',
  components: {
    PersonLookup
  },
  mixins: [Context, DepartmentEditSession, Util],
  data: () => ({
    applyingAction: null,
    bulkUpdateOptions: {
      instructor: {},
      midtermFormEnabled: false,
      startDate: undefined,
      evaluationType: undefined,
    },
    courseActions: {},
    evaluationTypes: [],
    isDuplicating: false,
    isInstructorRequired: false,
    isLoading: false,
    midtermFormAvailable: false,
  }),
  created() {
    this.courseActions = {
      // TO DO: Clean up dictionary keys and and statuses
      review: {
        apply: this.applyAction,
        completedText: 'Marked as to-do',
        inProgressText: 'Marking as to-do',
        key: 'review',
        status: 'review',
        text: 'Mark as to-do'
      },
      confirm: {
        apply: this.applyAction,
        completedText: 'Marked as done',
        inProgressText: 'Marking as done',
        key: 'confirm',
        status: 'confirmed',
        text: 'Mark as done'
      },
      unmark: {
        apply: this.applyAction,
        completedText: 'Unmarked',
        inProgressText: 'Unmarking',
        key: 'unmark',
        status: null,
        text: 'Unmark'
      },
      ignore: {
        apply: this.applyAction,
        completedText: 'Ignored',
        inProgressText: 'Ignoring',
        key: 'ignore',
        status: 'ignore',
        text: 'Ignore'
      },
      duplicate: {
        apply: this.showDuplicateOptions,
        completedText: 'Duplicated',
        inProgressText: 'Duplicating',
        key: 'duplicate',
        text: 'Duplicate'
      }
    }
    this.evaluationTypes = [{id: null, name: 'Default'}].concat(this.$config.evaluationTypes)
  },
  watch: {
    bulkUpdateOptions: {
      handler(options) {
        if (this.midtermFormAvailable) {
          this.isInstructorRequired = !options.midtermFormEnabled
        }
      },
      deep: true
    }
  },
  computed: {
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
    disableApplyDuplicate() {
      return this.disableControls
          || !this.allowEdits
          || this.$_.isEmpty(this.selectedEvaluationIds)
          || (this.isInstructorRequired && !this.$_.get(this.bulkUpdateOptions.instructor, 'uid'))
    },
    selectedTermValidDates() {
      const selectedTerm = this.$_.find(this.$config.availableTerms, {'id': this.selectedTermId})
      return selectedTerm.validDates
    }
  },
  methods: {
    afterApply(response) {
      this.refreshAll().then(() => {
        const selectedRowCount = this.applyingAction.key === 'duplicate' ? ((response.length || 0) / 2) : (response.length || 0)
        const target = `${selectedRowCount} ${selectedRowCount === 1 ? 'row' : 'rows'}`
        this.alertScreenReader(`${this.applyingAction.completedText} ${target}`)
        this.$putFocusNextTick(`apply-course-action-btn-${this.applyingAction.key}`)
        this.reset()
      }).finally(() => this.setDisableControls(false))
    },
    applyAction(key) {
      let fields = null
      let valid = true
      const target = `${this.selectedEvaluationIds.length || 0} ${this.selectedEvaluationIds.length === 1 ? 'row' : 'rows'}`
      this.applyingAction = this.courseActions[key]
      this.alertScreenReader(`${this.applyingAction.inProgressText} ${target}`)
      if (key === 'duplicate') {
        fields = {
          instructorUid: this.$_.get(this.bulkUpdateOptions.instructor, 'uid')
        }
        if (this.bulkUpdateOptions.midtermFormEnabled) {
          fields.midterm = 'true'
        }
        if (this.bulkUpdateOptions.startDate) {
          fields.startDate = this.$moment(this.bulkUpdateOptions.startDate).format('YYYY-MM-DD')
        }
        if (this.bulkUpdateOptions.evaluationType) {
          fields.evaluationTypeId = this.bulkUpdateOptions.evaluationType
        }
        valid = this.validateDuplicable(this.selectedEvaluationIds, fields)
      } else if (key === 'confirm') {
        valid = this.validateConfirmable(this.selectedEvaluationIds)
      }
      if (valid) {
        this.setDisableControls(true)
        this.isLoading = true
        updateEvaluations(
          this.department.id,
          key,
          this.selectedEvaluationIds,
          this.selectedTermId,
          fields
        ).then(response => this.afterApply(response), error => this.handleError(error))
      }
    },
    cancelDuplicate() {
      this.reset()
      this.alertScreenReader('Canceled duplication.')
      this.$putFocusNextTick('apply-course-action-btn-duplicate')
    },
    handleError(error) {
      this.showErrorDialog(this.$_.get(error, 'response.data.message', 'An unknown error occurred.'))
      this.refreshEvaluations().then(() => {
        this.setDisableControls(false)
        this.applyingAction = null
        this.isLoading = false
      })

    },
    isInvalidAction(action) {
      const uniqueStatuses = this.$_.uniq(this.evaluations
                  .filter(e => this.selectedEvaluationIds.includes(e.id))
                  .map(e => e.status))

      return (uniqueStatuses.length === 1 && uniqueStatuses[0] === action.status)
    },
    refreshEvaluations() {
      const selectedCourseNumbers = this.$_.uniq(this.evaluations
                  .filter(e => this.selectedEvaluationIds.includes(e.id))
                  .map(e => e.courseNumber))
      if (selectedCourseNumbers.length === 1) {
        return this.refreshSection({sectionId: selectedCourseNumbers[0], termId: this.selectedTermId})
      }
      return this.refreshAll()
    },
    reset() {
      this.bulkUpdateOptions = {
        instructor: {},
        midtermFormEnabled: false,
        startDate: null,
        evaluationType: null,
      }
      this.isDuplicating = false
      this.applyingAction = null
      this.isLoading = false
      this.midtermFormAvailable = false
    },
    selectInstructor(suggestion) {
      this.bulkUpdateOptions.instructor = suggestion
      this.$putFocusNextTick('bulk-duplicate-instructor-lookup-autocomplete')
    },
    showDuplicateOptions() {
      const selectedEvals = this.$_.filter(this.evaluations, e => this.selectedEvaluationIds.includes(e.id))

      // Pre-populate start date if shared by all selected evals.
      const uniqueStartDates = this.$_.chain(selectedEvals).map(e => new Date(e.startDate).toDateString()).uniq().value()
      if (uniqueStartDates.length === 1) {
        this.bulkUpdateOptions.startDate = new Date(uniqueStartDates[0])
      }

      // Pre-populate type if shared by all selected evals
      const uniqueTypes = this.$_.chain(selectedEvals).map(e => this.$_.get(e, 'evaluationType.id')).uniq().value()
      if (uniqueTypes.length === 1) {
        this.bulkUpdateOptions.evaluationType = this.$_.get(selectedEvals, '0.evaluationType.id')
      }

      // Show midterm form option only if a midterm form exists for all selected evals.
      this.midtermFormAvailable = true
      const availableFormNames = this.$_.map(this.$config.departmentForms, 'name')
      this.$_.each(selectedEvals, e => {
        const formName = this.$_.get(e, 'departmentForm.name')
        if (!formName || !(formName.endsWith('_MID') || availableFormNames.includes(formName + '_MID'))) {
          this.midtermFormAvailable = false
          return false
        }
      })
      if (!this.midtermFormAvailable) {
        this.isInstructorRequired = true
      }
      this.isDuplicating = true
      this.$putFocusNextTick('bulk-duplicate-instructor-lookup-autocomplete')
    }
  }
}
</script>

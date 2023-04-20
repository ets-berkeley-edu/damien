<template>
  <div class="align-center d-flex">
    <div class="align-center d-flex flex-wrap pl-2">
      <div v-for="(action, key) in courseActions" :key="key" class="align-center d-flex">
        <div :class="`evaluation-${key}-btn`">
          <v-btn
            :id="`apply-course-action-btn-${key}`"
            :key="key"
            class="text-capitalize text-nowrap mx-0 px-2"
            :color="$vuetify.theme.dark ? 'tertiary' : 'secondary'"
            :disabled="disableControls || !allowEdits || !selectedEvaluationIds.length || isLoading || isInvalidAction(action)"
            text
            @click.stop="action.apply(key)"
          >
            <span v-if="!(isLoading && key !== 'duplicate' && applyingAction.key === key)">{{ action.text }}</span>
            <v-progress-circular
              v-if="isLoading && key !== 'duplicate' && applyingAction.key === key"
              :indeterminate="true"
              color="tertiary"
              rotate="5"
              size="20"
              width="3"
            />
          </v-btn>
        </div>
        <div v-if="key === 'ignore'" class="align-self-center pt-1 px-1">
          <span class="font-size-18 text--secondary">|</span>
        </div>
      </div>
    </div>
    <UpdateEvaluations
      action="Duplicate"
      :apply-action="onConfirmDuplicate"
      :cancel-action="onCancelDuplicate"
      :is-applying="isApplying"
      :is-updating="isDuplicating"
      :midterm-form-available="midtermFormAvailable"
      v-bind="bulkUpdateOptions"
    />
    <UpdateEvaluations
      action="Edit"
      :apply-action="onConfirmEdit"
      :cancel-action="onCancelEdit"
      :is-applying="isApplying"
      :is-updating="isEditing"
      v-bind="bulkUpdateOptions"
    >
      <template #status="{status, on}">
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label
              id="update-evaluations-select-status-label"
              for="update-evaluations-select-status"
              class="v-label"
            >
              Status:
            </label>
          </v-col>
          <v-col cols="8">
            <select
              id="update-evaluations-select-status"
              class="native-select-override bulk-action-form-input light"
              :disabled="disableControls"
              :status="status"
              :value="status"
              v-on="on"
            >
              <option v-for="s in evaluationStatuses" :key="s.text" :value="s.value">{{ s.text }}</option>
            </select>
          </v-col>
        </v-row>
      </template>
      <template #form="{form, on}">
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label
              id="update-evaluations-select-form-label"
              for="update-evaluations-select-form"
              class="v-label"
            >
              Department Form:
            </label>
          </v-col>
          <v-col>
            <select
              id="update-evaluations-select-form"
              class="native-select-override bulk-action-form-input light"
              :disabled="disableControls"
              :form="form"
              :value="form"
              v-on="on"
            >
              <option v-for="df in activeDepartmentForms" :key="df.id" :value="df.id">{{ df.name }}</option>
            </select>
          </v-col>
        </v-row>
      </template>
    </UpdateEvaluations>
    <ConfirmDialog
      v-if="markAsDoneWarning"
      confirm-button-label="Proceed"
      :disabled="disableControls"
      :on-click-cancel="() => markAsDoneWarning = undefined"
      :on-click-confirm="onProceedMarkAsDone"
      :text="markAsDoneWarning"
      icon="mdi-alert-circle"
      title="Warning"
    />
  </div>
</template>

<script>
import {updateEvaluations} from '@/api/departments'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import UpdateEvaluations from '@/components/evaluation/UpdateEvaluations'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationActions',
  components: {
    ConfirmDialog,
    UpdateEvaluations
  },
  mixins: [Context, DepartmentEditSession, Util],
  data: () => ({
    applyingAction: null,
    bulkUpdateOptions: {
      departmentForm: undefined,
      evaluationStatus: undefined,
      evaluationType: undefined,
      instructor: undefined,
      midtermFormEnabled: false,
      startDate: undefined,
    },
    courseActions: {},
    isApplying: false,
    isDuplicating: false,
    isEditing: false,
    isLoading: false,
    markAsDoneWarning: undefined,
    midtermFormAvailable: false
  }),
  created() {
    this.courseActions = {
      // TO DO: Clean up dictionary keys and statuses
      review: {
        apply: this.onClickReview,
        completedText: 'Marked as to-do',
        inProgressText: 'Marking as to-do',
        key: 'review',
        status: 'review',
        text: 'Mark as to-do'
      },
      confirm: {
        apply: this.onClickMarkDone,
        completedText: 'Marked as done',
        inProgressText: 'Marking as done',
        key: 'confirm',
        status: 'confirmed',
        text: 'Mark as done'
      },
      unmark: {
        apply: this.onClickUnmark,
        completedText: 'Unmarked',
        inProgressText: 'Unmarking',
        key: 'unmark',
        status: null,
        text: 'Unmark'
      },
      ignore: {
        apply: this.onClickIgnore,
        completedText: 'Ignored',
        inProgressText: 'Ignoring',
        key: 'ignore',
        status: 'ignore',
        text: 'Ignore'
      },
      duplicate: {
        apply: this.onClickDuplicate,
        completedText: 'Duplicated',
        inProgressText: 'Duplicating',
        key: 'duplicate',
        text: 'Duplicate'
      },
      edit: {
        apply: this.onClickEdit,
        completedText: 'Edited',
        inProgressText: 'Editing',
        key: 'edit',
        text: 'Edit'
      }
    }
  },
  computed: {
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
    selectedEvaluations() {
      return this.$_.filter(this.evaluations, e => this.selectedEvaluationIds.includes(e.id))
    }
  },
  methods: {
    onCancelDuplicate() {
      this.reset()
      this.alertScreenReader('Canceled duplication.')
      this.$putFocusNextTick('apply-course-action-btn-duplicate')
    },
    onCancelEdit() {
      this.reset()
      this.alertScreenReader('Canceled edit.')
      this.$putFocusNextTick('apply-course-action-btn-edit')
    },
    onClickDuplicate() {
      this.showUpdateOptions()
      this.bulkUpdateOptions.instructor = {}
      this.midtermFormAvailable = this.department.usesMidtermForms
      if (this.midtermFormAvailable) {
        // Show midterm form option only if a midterm form exists for all selected evals.
        const availableFormNames = this.$_.map(this.activeDepartmentForms, 'name')
        this.$_.each(this.selectedEvaluations, e => {
          const formName = this.$_.get(e, 'departmentForm.name')
          if (!formName || !(formName.endsWith('_MID') || availableFormNames.includes(formName + '_MID'))) {
            this.midtermFormAvailable = false
            return false
          }
        })
      }
      this.isDuplicating = true
      this.$putFocusNextTick('update-evaluations-instructor-lookup-autocomplete')
    },
    onClickEdit() {
      this.showUpdateOptions()
      // Pre-populate form if shared by all selected evals
      const uniqueForms = this.$_.chain(this.selectedEvaluations).map(e => this.$_.get(e, 'departmentForm.id')).uniq().value()
      if (uniqueForms.length === 1) {
        this.bulkUpdateOptions.departmentForm = this.$_.get(this.selectedEvaluations, '0.departmentForm.id')
      }
      // Show instructor lookup if instructor is missing from all selected evals
      if (this.$_.every(this.selectedEvaluations, {'instructor': null})) {
        this.bulkUpdateOptions.instructor = {}
      }
      // Pre-populate status if shared by all selected evals
      const uniqueStatuses = this.$_.chain(this.selectedEvaluations).map(e => this.$_.get(e, 'status')).uniq().value()
      if (uniqueStatuses.length === 1) {
        this.bulkUpdateOptions.evaluationStatus = this.$_.get(this.selectedEvaluations, '0.status', 'none')
      }
      this.isEditing = true
      this.$putFocusNextTick('update-evaluations-select-status')
    },
    onClickIgnore(key) {
      this.validateAndUpdate(key)
    },
    onClickMarkDone(key) {
      const selected = this.$_.filter(this.evaluations, e => this.$_.includes(this.selectedEvaluationIds, e.id))
      this.markAsDoneWarning = this.validateMarkAsDone(selected)
      if (!this.markAsDoneWarning) {
        this.validateAndUpdate(key)
      }
    },
    onClickReview(key) {
      this.validateAndUpdate(key)
    },
    onClickUnmark(key) {
      this.validateAndUpdate(key)
    },
    onConfirmDuplicate(options) {
      this.bulkUpdateOptions = options
      this.validateAndUpdate('duplicate')
    },
    onConfirmEdit(options) {
      const selected = this.$_.filter(this.evaluations, e => this.$_.includes(this.selectedEvaluationIds, e.id))
      this.bulkUpdateOptions = options
      if ('confirmed' === this.bulkUpdateOptions.evaluationStatus) {
        this.markAsDoneWarning = this.validateMarkAsDone(selected)
      }
      if (!this.markAsDoneWarning) {
        this.validateAndUpdate('edit')
      }
    },
    onProceedMarkAsDone() {
      this.markAsDoneWarning = null
      this.validateAndUpdate(this.isEditing ? 'edit' : 'confirm')
    },
    getEvaluationFieldsForUpdate(key) {
      let fields = null
      if (['duplicate', 'edit'].includes(key)) {
        fields = {}
        if (this.bulkUpdateOptions.departmentForm) {
          fields.departmentFormId = this.bulkUpdateOptions.departmentForm
        }
        if (this.$_.has(this.bulkUpdateOptions, 'evaluationStatus')) {
          fields.status = this.bulkUpdateOptions.evaluationStatus
        }
        if (this.bulkUpdateOptions.evaluationType) {
          fields.evaluationTypeId = this.bulkUpdateOptions.evaluationType
        }
        if (this.bulkUpdateOptions.instructor) {
          fields.instructorUid = this.$_.get(this.bulkUpdateOptions.instructor, 'uid')
        }
        if (this.bulkUpdateOptions.startDate) {
          fields.startDate = this.$moment(this.bulkUpdateOptions.startDate).format('YYYY-MM-DD')
        }
        if (key === 'duplicate') {
          if (this.bulkUpdateOptions.midtermFormEnabled) {
            fields.midterm = 'true'
          }
        }
      }
      return fields
    },
    isInvalidAction(action) {
      const uniqueStatuses = this.$_.uniq(this.evaluations
                  .filter(e => this.selectedEvaluationIds.includes(e.id))
                  .map(e => e.status))
      return (uniqueStatuses.length === 1 && uniqueStatuses[0] === action.status)
    },
    reset() {
      this.bulkUpdateOptions = {
        departmentForm: null,
        evaluationStatus: null,
        evaluationType: null,
        instructor: null,
        midtermFormEnabled: false,
        startDate: null,
      }
      this.isDuplicating = false
      this.isEditing = false
      this.applyingAction = null
      this.isApplying = false
      this.isLoading = false
      this.markAsDoneWarning = null
      this.midtermFormAvailable = false
    },
    selectInstructor(suggestion) {
      this.bulkUpdateOptions.instructor = suggestion
      this.$putFocusNextTick('update-evaluations-instructor-lookup-autocomplete')
    },
    showUpdateOptions() {
      // Pre-populate start date if shared by all selected evals.
      const uniqueStartDates = this.$_.chain(this.selectedEvaluations).map(e => new Date(e.startDate).toDateString()).uniq().value()
      if (uniqueStartDates.length === 1) {
        this.bulkUpdateOptions.startDate = new Date(uniqueStartDates[0])
      }
      // Pre-populate type if shared by all selected evals
      const uniqueTypes = this.$_.chain(this.selectedEvaluations).map(e => this.$_.get(e, 'evaluationType.id')).uniq().value()
      if (uniqueTypes.length === 1) {
        this.bulkUpdateOptions.evaluationType = this.$_.get(this.selectedEvaluations, '0.evaluationType.id')
      }
    },
    update(fields, key) {
      this.setDisableControls(true)
      this.isLoading = true
      const selectedCourseNumbers = this.$_.uniq(this.evaluations
        .filter(e => this.selectedEvaluationIds.includes(e.id))
        .map(e => e.courseNumber))
      const refresh = () => {
        return selectedCourseNumbers.length === 1
          ? this.refreshSection({sectionId: selectedCourseNumbers[0], termId: this.selectedTermId})
          : this.refreshAll()
      }
      updateEvaluations(
        this.department.id,
        key,
        this.selectedEvaluationIds,
        this.selectedTermId,
        fields
      ).then(
        response => {
          refresh().then(() => {
            const selectedRowCount = this.applyingAction.key === 'duplicate' ? ((response.length || 0) / 2) : (response.length || 0)
            const target = `${selectedRowCount} ${selectedRowCount === 1 ? 'row' : 'rows'}`
            this.alertScreenReader(`${this.applyingAction.completedText} ${target}`)
            this.$putFocusNextTick('select-all-evals-checkbox')
            this.reset()
          }).finally(() => {
            this.isApplying = false
            this.setDisableControls(false)
          })
        },
        error => {
          this.showErrorDialog(this.$_.get(error, 'response.data.message', 'An unknown error occurred.'))
          this.setDisableControls(false)
          this.isApplying = false
          this.isLoading = false
        }
      )
    },
    validateAndUpdate(key) {
      let valid = true
      const target = `${this.selectedEvaluationIds.length || 0} ${this.selectedEvaluationIds.length === 1 ? 'row' : 'rows'}`
      this.applyingAction = this.courseActions[key]
      this.isApplying = true
      this.alertScreenReader(`${this.applyingAction.inProgressText} ${target}`)

      const fields = this.getEvaluationFieldsForUpdate(key)
      if (key === 'duplicate') {
        valid = this.validateDuplicable(this.selectedEvaluationIds, fields)
      } else if (key === 'confirm' || (key === 'edit' && this.bulkUpdateOptions.evaluationStatus === 'confirmed')) {
        valid = this.validateConfirmable(this.selectedEvaluationIds, fields)
      }
      if (valid) {
        this.update(fields, key)
      } else {
        this.isApplying = false
      }
    }
  }
}
</script>

<style scoped>
.evaluation-confirm-btn {
  min-width: 7.6em
}
.evaluation-duplicate-btn {
  min-width: 5.45em
}
.evaluation-edit-btn {
  min-width: 4.02em
}
.evaluation-ignore-btn {
  min-width: 4.05em
}
.evaluation-review-btn {
  min-width: 7.84em
}
.evaluation-unmark-btn {
  min-width: 4.65em
}
</style>

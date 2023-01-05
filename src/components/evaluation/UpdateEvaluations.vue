<template>
  <v-dialog
    id="update-evaluations-dialog"
    v-model="model"
    aria-labelledby="update-evaluations-dialog-title"
    class="overflow-y-visible"
    width="500"
    v-bind="$attrs"
    v-on="$listeners"
    @click:outside="onClickCancel"
    @keydown.esc="onClickCancel"
  >
    <v-card>
      <v-card-title id="update-evaluations-dialog-title" tabindex="-1">{{ title }}</v-card-title>
      <v-card-text>
        <slot name="status" :status="selectedEvaluationStatus" :on="{change: e => selectedEvaluationStatus = e.target.value}"></slot>
        <div class="d-flex align-center mt-2">
          <PersonLookup
            v-if="instructor !== null"
            id="update-evaluations-instructor-lookup-autocomplete"
            :disabled="disableControls"
            :instructor-lookup="true"
            :on-select-result="selectInstructor"
            placeholder="Instructor name or UID"
            :required="isInstructorRequired"
            solo
            :value="selectedInstructor"
          />
        </div>
        <v-checkbox
          v-if="midtermFormAvailable"
          v-model="midtermFormEnabled"
          class="text-nowrap"
          color="tertiary"
          :disabled="disableControls"
          hide-details
          label="Use midterm department forms"
          :ripple="false"
        />
        <slot name="form" :form="selectedDepartmentForm" :on="{change: e => selectedDepartmentForm = e.target.value}"></slot>
        <div class="my-4">
          <label
            id="update-evaluations-select-type-label"
            for="update-evaluations-select-type"
            class="v-label d-block py-1"
          >
            Evaluation Type:
          </label>
          <select
            id="update-evaluations-select-type"
            v-model="selectedEvaluationType"
            class="native-select-override light d-block mx-auto"
            :disabled="disableControls"
          >
            <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
          </select>
        </div>
        <div class="d-flex align-center mt-2">
          <label
            for="update-evaluations-start-date"
            class="v-label"
            :class="$vuetify.theme.dark ? 'theme--dark' : 'theme--light'"
          >
            Evaluation start date:
          </label>
          <c-date-picker
            v-model="selectedStartDate"
            class="mx-3"
            :min-date="$moment(validDates.begin).toDate()"
            :max-date="$moment(validDates.end).subtract(13, 'days').toDate()"
            :popover="{positionFixed: true}"
            title-position="left"
          >
            <template #default="{ inputValue, inputEvents }">
              <input
                id="update-evaluations-start-date"
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
            :disabled="disableApply"
            min-width="85"
            @click="onClickApply"
          >
            <span v-if="!isApplying">Apply</span>
            <v-progress-circular
              v-if="isApplying"
              :indeterminate="true"
              color="white"
              rotate="5"
              size="20"
              width="3"
            ></v-progress-circular>
          </v-btn>
          <v-btn
            id="cancel-duplicate-btn"
            class="mt-2 mr-2"
            :disabled="disableControls"
            @click="onClickCancel"
          >
            Cancel
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'
import Util from '@/mixins/Util'

export default {
  name: 'UpdateEvaluations',
  components: {
    PersonLookup
  },
  mixins: [Context, DepartmentEditSession, Util],
  props: {
    applyAction: {
      required: true,
      type: Function
    },
    cancelAction: {
      required: true,
      type: Function
    },
    departmentForm: {
      default: undefined,
      required: false,
      type: Number
    },
    evaluationStatus: {
      default: undefined,
      required: false,
      type: String
    },
    evaluationType: {
      default: undefined,
      required: false,
      type: Number
    },
    instructor: {
      default: undefined,
      required: false,
      type: Object
    },
    isApplying: {
      required: true,
      type: Boolean
    },
    isUpdating: {
      required: true,
      type: Boolean
    },
    midtermFormAvailable: {
      required: false,
      type: Boolean
    },
    startDate: {
      default: undefined,
      required: false,
      type: Date
    },
    title: {
      required: true,
      type: String
    }
  },
  data: () => ({
    evaluationTypes: [],
    isInstructorRequired: false,
    midtermFormEnabled: false,
    model: false,
    selectedDepartmentForm: undefined,
    selectedEvaluationStatus: undefined,
    selectedEvaluationType: undefined,
    selectedInstructor: undefined,
    selectedStartDate: undefined
  }),
  watch: {
    midtermFormEnabled(midtermFormEnabled) {
      if (this.midtermFormAvailable) {
        this.isInstructorRequired = !midtermFormEnabled
      }
    },
    isUpdating(isUpdating) {
      this.model = isUpdating
      if (isUpdating) {
        this.midtermFormEnabled = false
        this.selectedDepartmentForm = this.departmentForm
        this.selectedEvaluationStatus = this.evaluationStatus
        this.selectedEvaluationType = this.evaluationType
        this.selectedInstructor = this.instructor
        this.selectedStartDate = this.startDate
        this.isInstructorRequired = this.midtermFormAvailable
      }
    }
  },
  created() {
    this.evaluationTypes = [{id: null, name: 'Default'}].concat(this.$config.evaluationTypes)
  },
  computed: {
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
    disableApply() {
      return this.disableControls
          || !this.allowEdits
          || (this.isInstructorRequired && !this.$_.get(this.selectedInstructor, 'uid'))
    },
    validDates() {
      const selectedTerm = this.$_.find(this.$config.availableTerms, {'id': this.selectedTermId})
      return selectedTerm.validDates
    }
  },
  methods: {
    onClickApply() {
      this.applyAction({
        departmentForm: this.selectedDepartmentForm,
        evaluationStatus: this.selectedEvaluationStatus === 'none' ? null : this.selectedEvaluationStatus,
        evaluationType: this.selectedEvaluationType,
        instructor: this.selectedInstructor,
        midtermFormEnabled: this.midtermFormEnabled,
        startDate: this.selectedStartDate
      })
    },
    onClickCancel() {
      this.isInstructorRequired = false
      this.midtermFormEnabled = false
      this.selectedDepartmentForm = null
      this.selectedEvaluationStatus = null
      this.selectedEvaluationType = null
      this.selectedInstructor = null
      this.selectedStartDate = null
      this.cancelAction()
    },
    selectInstructor(suggestion) {
      this.selectedInstructor = suggestion
    }
  }
}
</script>
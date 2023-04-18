<template>
  <v-dialog
    v-model="model"
    aria-labelledby="update-evaluations-dialog-title"
    class="overflow-y-visible"
    width="600"
    v-bind="$attrs"
    v-on="$listeners"
    @click:outside="onClickCancel"
    @keydown.esc="onClickCancel"
  >
    <v-card>
      <v-card-title id="update-evaluations-dialog-title" tabindex="-1">{{ title }}</v-card-title>
      <v-card-text class="px-0 pb-0">
        <v-container class="px-8 pb-4">
          <slot name="status" :status="selectedEvaluationStatus" :on="{change: e => selectedEvaluationStatus = e.target.value}"></slot>
          <PersonLookup
            v-if="$_.isObject(instructor)"
            id="update-evaluations-instructor-lookup-autocomplete"
            container-class="flex-row py-1"
            :disabled="disableControls"
            :inline="true"
            input-class="bulk-action-form-input"
            :instructor-lookup="true"
            label="Instructor: "
            label-class="v-label d-flex text-nowrap align-center"
            :on-select-result="selectInstructor"
            placeholder="Name or UID"
            :required="isInstructorRequired"
            solo
            :value="selectedInstructor"
          />
          <v-row v-if="midtermFormAvailable" class="d-flex align-center" dense>
            <v-col cols="4"></v-col>
            <v-col cols="8">
              <v-checkbox
                v-model="midtermFormEnabled"
                class="bulk-action-form-input text-nowrap my-1"
                color="tertiary"
                :disabled="disableControls"
                hide-details
                label="Use midterm department forms"
                :ripple="false"
              />
            </v-col>
          </v-row>
          <slot name="form" :form="selectedDepartmentForm" :on="{change: e => selectedDepartmentForm = $_.toInteger(e.target.value)}"></slot>
          <v-row class="d-flex align-center" dense>
            <v-col cols="4">
              <label
                id="update-evaluations-select-type-label"
                for="update-evaluations-select-type"
                class="v-label d-block text-nowrap py-1"
              >
                Evaluation Type:
              </label>
            </v-col>
            <v-col cols="8">
              <select
                id="update-evaluations-select-type"
                v-model="selectedEvaluationType"
                class="native-select-override bulk-action-form-input light"
                :disabled="disableControls"
              >
                <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
              </select>
            </v-col>
          </v-row>
          <v-row class="d-flex align-center" dense>
            <v-col cols="4">
              <label
                for="update-evaluations-start-date"
                class="v-label text-nowrap"
                :class="$vuetify.theme.dark ? 'theme--dark' : 'theme--light'"
              >
                Evaluation Start Date:
              </label>
            </v-col>
            <v-col cols="8">
              <c-date-picker
                v-model="selectedStartDate"
                class="bulk-action-form-input"
                :min-date="$_.get(validStartDates, 'min')"
                :max-date="$_.get(validStartDates, 'max')"
                :popover="{positionFixed: true}"
                title-position="left"
              >
                <template #default="{ inputValue, inputEvents }">
                  <input
                    id="update-evaluations-start-date"
                    class="datepicker-input input-override light my-0"
                    :disabled="disableControls"
                    maxlength="10"
                    minlength="10"
                    :value="inputValue"
                    v-on="inputEvents"
                  />
                </template>
              </c-date-picker>
            </v-col>
          </v-row>
        </v-container>
        <div v-if="$_.size(selectedEvaluations)" class="bulk-action-preview pt-2">
          <v-simple-table dense class="bulk-action-preview-table">
            <caption class="bulk-action-preview-caption text-left"><div class="px-6 pb-3">Preview Your Changes</div></caption>
            <thead>
              <tr>
                <th
                  v-for="(colName, index) in previewHeaders"
                  :key="index"
                  class="pl-1"
                  :class="{'pl-3': index === 0}"
                >
                  {{ colName }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(evaluation, index) in selectedEvaluations" :key="index">
                <td class="bulk-action-status-col pl-3">
                  <div v-if="evaluation.status" :class="{'text-decoration-line-through accent--text': selectedEvaluationStatus && selectedEvaluationStatus !== evaluation.status}">
                    {{ getStatusText(evaluation.status) }}
                  </div>
                  <div v-if="selectedEvaluationStatus && selectedEvaluationStatus !== evaluation.status">
                    {{ getStatusText(selectedEvaluationStatus) }}
                  </div>
                </td>
                <td class="bulk-action-number-col pl-1">{{ evaluation.courseNumber }}</td>
                <td class="bulk-action-name-col pl-1">
                  <div>{{ evaluation.subjectArea }} {{ evaluation.catalogId }}</div>
                  <div>{{ evaluation.instructionFormat }} {{ evaluation.sectionNumber }}</div>
                </td>
                <td class="bulk-action-instructor-col pl-1">
                  <div v-if="$_.get(evaluation, 'instructor.uid')" :class="{'text-decoration-line-through accent--text': $_.get(selectedInstructor, 'uid') && selectedInstructor.uid !== evaluation.instructor.uid}">
                    <div>{{ evaluation.instructor.firstName }} {{ evaluation.instructor.lastName }}</div>
                    <div>({{ evaluation.instructor.uid }})</div>
                  </div>
                  <div v-if="$_.get(selectedInstructor, 'uid') && selectedInstructor.uid !== $_.get(evaluation, 'instructor.uid')">
                    <div>{{ selectedInstructor.firstName }} {{ selectedInstructor.lastName }}</div>
                    <div>({{ selectedInstructor.uid }})</div>
                  </div>
                </td>
                <td class="bulk-action-form-col pl-1">
                  <div v-if="evaluation.departmentForm" :class="{'text-decoration-line-through accent--text': selectedDepartmentForm && selectedDepartmentForm !== evaluation.departmentForm.id}">
                    {{ evaluation.departmentForm.name }}
                  </div>
                  <div v-if="selectedDepartmentForm && selectedDepartmentForm !== $_.get(evaluation, 'departmentForm.id')">
                    {{ selectedDepartmentFormName }}
                  </div>
                </td>
                <td class="bulk-action-type-col pl-1">
                  <div v-if="evaluation.evaluationType" :class="{'text-decoration-line-through accent--text accent--text': selectedEvaluationType && selectedEvaluationType !== evaluation.evaluationType.id}">
                    {{ evaluation.evaluationType.name }}
                  </div>
                  <div v-if="selectedEvaluationType && selectedEvaluationType !== $_.get(evaluation, 'evaluationType.id')">
                    {{ selectedEvaluationTypeName }}
                  </div>
                </td>
                <td class="bulk-action-date-col pl-1">
                  <div v-if="evaluation.startDate" :class="{'text-decoration-line-through accent--text': selectedStartDate && selectedStartDay !== $moment.utc(evaluation.startDate).dayOfYear()}">
                    {{ evaluation.startDate | moment('MM/DD/YY') }}
                  </div>
                  <div v-if="selectedStartDate && selectedStartDay !== $moment.utc(evaluation.startDate).dayOfYear()">
                    {{ selectedStartDate | moment('MM/DD/YY') }}
                  </div>
                </td>
              </tr>
            </tbody>
          </v-simple-table>
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
    model: undefined,
    previewHeaders: ['Status', 'Course Number', 'Course Name', 'Instructor', 'Department Form', 'Evaluation Type', 'Start Date'],
    selectedDepartmentForm: undefined,
    selectedEvaluations: [],
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
    },
    model() {
      this.reset()
    }
  },
  created() {
    this.evaluationTypes = [{id: null, name: 'Default'}].concat(this.$config.evaluationTypes)
    this.model = this.isUpdating
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
    selectedDepartmentFormName() {
      return this.$_.get(this.$_.find(this.$config.departmentForms, df => df.id === this.selectedDepartmentForm), 'name')
    },
    selectedEvaluationTypeName() {
      return this.$_.get(this.$_.find(this.$config.evaluationTypes, et => et.id === this.selectedEvaluationType), 'name')
    },
    selectedStartDay() {
      return this.$moment.utc(this.selectedStartDate).dayOfYear()
    },
    validStartDates() {
      // The intersection of the selected rows' allowed evaluation start dates
      return {
        'max': this.$moment.min(this.$_.map(this.selectedEvaluations, e => this.$moment(e.maxStartDate))).toDate(),
        'min': this.$moment.max(this.$_.map(this.selectedEvaluations, e => this.$moment(e.meetingDates.start))).toDate()
      }
    }
  },
  methods: {
    getStatusText(status) {
      return status === 'none' ? null : this.$_.get(this.$_.find(this.evaluationStatuses, es => es.value === status), 'text')
    },
    onClickApply() {
      this.applyAction({
        departmentForm: this.selectedDepartmentForm,
        evaluationStatus: this.selectedEvaluationStatus === 'none' ? null : this.selectedEvaluationStatus,
        evaluationType: this.selectedEvaluationType,
        instructor: this.selectedInstructor || this.instructor,
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
    reset() {
      this.selectedEvaluations = this.$_.reduce(this.evaluations, (evaluations, e) => {
        if (e.isSelected) {
          evaluations.push(e)
        }
        return evaluations
      }, [])
      this.midtermFormEnabled = false
      this.selectedDepartmentForm = this.departmentForm
      this.selectedEvaluationStatus = this.evaluationStatus
      this.selectedEvaluationType = this.evaluationType
      this.selectedInstructor = this.instructor
      this.selectedStartDate = this.startDate
      this.isInstructorRequired = this.midtermFormAvailable
    },
    selectInstructor(suggestion) {
      this.selectedInstructor = suggestion
    }
  }
}
</script>

<style>
.bulk-action-form-input {
  width: 250px
}
</style>

<style scoped>
.bulk-action-date-col {
    margin-right: 15px;
    width: 65px;
  }
.bulk-action-form-col {
  width: 80px;
}
.bulk-action-instructor-col {
  width: 100px;
}
.bulk-action-name-col {
  width: 80px;
}
.bulk-action-number-col {
  width: 60px;
}
.bulk-action-preview {
  overflow-x: hidden;
  overflow-y: auto;
  scrollbar-gutter: stable;
}
.bulk-action-preview-caption {
  font-size: 16px;
  font-weight: 500;
}
.bulk-action-preview-table {
  max-height: 200px;
}
.bulk-action-preview-table > div {
  margin-right: -15px !important;
}
.bulk-action-status-col {
  width: 70px;
}
.bulk-action-type-col {
  width: 80px;
}
</style>

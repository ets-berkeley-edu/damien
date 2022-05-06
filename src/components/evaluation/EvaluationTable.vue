<template>
  <div>
    <v-row>
      <v-col>
        <v-text-field
          v-model="searchFilter"
          class="ml-4"
          append-icon="mdi-magnify"
          color="tertiary"
          label="Find"
          single-line
          hide-details
        ></v-text-field>
      </v-col>
      <v-col v-if="!readonly" class="ma-4 text-right">
        Show statuses:
        <v-btn
          v-for="type in $_.keys(filterTypes)"
          :id="`evaluations-filter-${type}`"
          :key="type"
          role="tablist"
          class="filter ma-1 px-2 text-center"
          :class="{
            'secondary': filterTypes[type].enabled,
            'filter-inactive': !filterTypes[type].enabled
          }"
          aria-controls="timeline-messages"
          :aria-selected="filterTypes[type].enabled"
          @click="toggleFilter(type)"
          @keypress.enter.prevent="toggleFilter(type)"
        >
          {{ filterTypes[type].label }}
        </v-btn>
      </v-col>
    </v-row>
    <v-data-table
      id="evaluation-table"
      class="scrollable-table"
      disable-pagination
      :headers="headers"
      :search="searchFilter"
      hide-default-footer
      :items="evaluations"
    >
      <template #body="{items}">
        <tbody>
          <template v-for="(evaluation, rowIndex) in items">
            <v-hover v-if="filterEnabled(evaluation)" v-slot="{ hover }" :key="evaluation.id">
              <tr
                class="evaluation-row"
                :class="evaluationClass(evaluation, hover)"
              >
                <td v-if="readonly" :id="`evaluation-${rowIndex}-department`">
                  <router-link :to="`/department/${evaluation.department.id}`">
                    {{ evaluation.department.name }}
                  </router-link>
                </td>
                <td v-if="!readonly">
                  <v-checkbox
                    v-if="!isEditing(evaluation)"
                    :id="`evaluation-${rowIndex}-checkbox`"
                    :value="evaluation.isSelected"
                    :color="`${hover ? 'primary' : 'tertiary'}`"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
                    @change="updateEvaluationsSelected(rowIndex)"
                  ></v-checkbox>
                </td>
                <td :id="`evaluation-${rowIndex}-status`" class="position-relative">
                  <div
                    v-if="!isEditing(evaluation) && (!hover || readonly) && evaluation.status"
                    class="pill"
                    :class="evaluationPillClass(evaluation)"
                  >
                    {{ evaluation.status }}
                  </div>
                  <div
                    v-if="!isEditing(evaluation) && ((hover && !readonly) || !evaluation.status)"
                    class="pill pill-invisible"
                  >
                    <v-btn
                      class="primary--text"
                      :class="{'hidden': isEditing(evaluation) || !hover}"
                      block
                      text
                      @click="onEditEvaluation(evaluation)"
                      @keypress.enter.prevent="onEditEvaluation(evaluation)"
                    >
                      Edit
                    </v-btn>
                  </div>
                  <select
                    v-if="isEditing(evaluation)"
                    id="select-evaluation-status"
                    v-model="selectedEvaluationStatus"
                    class="native-select-override light status-select"
                  >
                    <option v-for="s in evaluationStatuses" :key="s.text" :value="s.value">{{ s.text }}</option>
                  </select>
                </td>
                <td :id="`evaluation-${rowIndex}-lastUpdated`">
                  {{ $moment(evaluation.lastUpdated) | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${rowIndex}-courseNumber`">
                  {{ evaluation.courseNumber }}
                  <div v-if="evaluation.crossListedWith" class="xlisting-note">
                    (Cross-listed with {{ evaluation.crossListedWith.length > 1 ? 'sections' : 'section' }}
                    {{ evaluation.crossListedWith.join(', ') }})
                  </div>
                  <div v-if="evaluation.roomSharedWith" class="xlisting-note">
                    (Room shared with {{ evaluation.roomSharedWith.length > 1 ? 'sections' : 'section' }}
                    {{ evaluation.roomSharedWith.join(', ') }})
                  </div>
                </td>
                <td>
                  <div :id="`evaluation-${rowIndex}-courseName`">
                    {{ evaluation.subjectArea }}
                    {{ evaluation.catalogId }}
                    {{ evaluation.instructionFormat }}
                    {{ evaluation.sectionNumber }}
                  </div>
                  <div :id="`evaluation-${rowIndex}-courseTitle`">
                    {{ evaluation.courseTitle }}
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-instructor`">
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.firstName }}
                    {{ evaluation.instructor.lastName }}
                    ({{ evaluation.instructor.uid }})
                  </div>
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.emailAddress }}
                  </div>
                  <div v-if="!evaluation.instructor && isEditing(evaluation)">
                    <div v-if="pendingInstructor" class="py-2">
                      {{ pendingInstructor.firstName }}
                      {{ pendingInstructor.lastName }}
                      ({{ pendingInstructor.uid }})
                    </div>
                    <div v-if="pendingInstructor">
                      {{ pendingInstructor.emailAddress }}
                    </div>
                    <div class="pb-2">
                      <div>
                        <div class="d-flex align-center mt-2">
                          <PersonLookup
                            id="input-instructor-lookup-autocomplete"
                            :instructor-lookup="true"
                            placeholder="Choose instructor name or UID"
                            :on-select-result="selectInstructor"
                            solo
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-departmentForm`">
                  <div v-if="evaluation.departmentForm && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.departmentForm}">
                    {{ evaluation.departmentForm.name }}
                    <div v-for="(conflict, index) in evaluation.conflicts.departmentForm" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value }} from {{ conflict.department }} department
                    </div>
                  </div>
                  <div
                    v-if="!evaluation.departmentForm && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    class="evaluation-error error--text"
                  >
                    <v-icon small color="error">mdi-alert-circle</v-icon> Department form required
                  </div>
                  <vue-select
                    v-if="isEditing(evaluation)"
                    id="select-department-form"
                    v-model="selectedDepartmentForm"
                    class="vue-select-override light py-2"
                    :clearable="false"
                    label="name"
                    :options="departmentForms"
                    @option:selected="afterSelectDepartmentForm"
                  >
                    <template #search="{attributes, events}">
                      <input
                        id="input-department-form"
                        class="vs__search input-department-form"
                        v-bind="attributes"
                        v-on="events"
                      />
                    </template>
                    <template #selected-option-container="{option}">
                      <div>{{ option.name }}</div>
                    </template>
                  </vue-select>
                </td>
                <td :id="`evaluation-${rowIndex}-evaluationType`">
                  <div v-if="evaluation.evaluationType && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.evaluationType}">
                    {{ evaluation.evaluationType.name }}
                    <div v-for="(conflict, index) in evaluation.conflicts.evaluationType" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value }} from {{ conflict.department }} department
                    </div>
                  </div>
                  <div
                    v-if="!evaluation.evaluationType && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    class="evaluation-error error--text"
                  >
                    <v-icon small color="error">mdi-alert-circle</v-icon> Evaluation type required
                  </div>
                  <select
                    v-if="isEditing(evaluation)"
                    id="select-evaluation-type"
                    v-model="selectedEvaluationType"
                    class="native-select-override light"
                  >
                    <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
                  </select>
                </td>
                <td :id="`evaluation-${rowIndex}-period`">
                  <span v-if="evaluation.startDate && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.evaluationPeriod}">
                    <div>{{ evaluation.startDate | moment('MM/DD/YY') }} - {{ evaluation.endDate | moment('MM/DD/YY') }}</div>
                    <div>{{ evaluation.modular ? 2 : 3 }} weeks</div>
                    <div v-for="(conflict, index) in evaluation.conflicts.evaluationPeriod" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon>
                      Conflicts with period starting
                      {{ $moment(conflict.value).format('MM/DD/YY') }}
                      from {{ conflict.department }} department
                    </div>
                  </span>
                  <div v-if="isEditing(evaluation)">
                    <div v-if="selectedStartDate">
                      Start date:
                    </div>
                    <div v-if="!selectedStartDate" class="evaluation-error">
                      <v-icon small color="white">mdi-alert-circle</v-icon> Start date required
                    </div>
                    <c-date-picker
                      v-model="selectedStartDate"
                      :min-date="new Date(evaluation.meetingDates.start)"
                      :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
                      title-position="left"
                    >
                      <template v-slot="{ inputValue, inputEvents }">
                        <input
                          class="datepicker-input input-override light"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    </c-date-picker>
                  </div>
                </td>
              </tr>
            </v-hover>
            <tr v-if="isEditing(evaluation)" :key="`${evaluation.id}-edit`" class="secondary white--text border-top-none">
              <td></td>
              <td colspan="8">
                <div class="d-flex justify-end">
                  <v-btn
                    id="save-evaluation-edit-btn"
                    class="ma-2 evaluation-edit-btn"
                    color="primary"
                    width="150px"
                    :disabled="disableControls || !rowValid || saving"
                    @click.prevent="saveEvaluation(evaluation)"
                    @keypress.enter.prevent="saveEvaluation(evaluation)"
                  >
                    <span v-if="!saving">Save</span>
                    <v-progress-circular
                      v-if="saving"
                      :indeterminate="true"
                      color="white"
                      rotate="5"
                      size="20"
                      width="3"
                    ></v-progress-circular>
                  </v-btn>
                  <v-btn
                    id="cancel-evaluation-edit-btn"
                    class="ma-2 evaluation-edit-btn"
                    :disabled="saving"
                    width="150px"
                    @click="clearEdit"
                    @keypress.enter.prevent="clearEdit"
                  >
                    Cancel
                  </v-btn>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import {getDepartmentForms} from '@/api/departmentForms'
import {getEvaluationTypes} from '@/api/evaluationTypes'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'

export default {
  name: 'EvaluationTable',
  mixins: [Context, DepartmentEditSession],
  components: { PersonLookup },
  data: () => ({
    departmentForms: [],
    editRowId: null,
    evaluationStatuses: [
      {text: 'Unmarked', value: null},
      {text: 'Review', value: 'review'},
      {text: 'Confirmed', value: 'confirmed'},
      {text: 'Ignore', value: 'ignore'}
    ],
    evaluationTypes: [],
    filterTypes: {
      'unmarked': {label: 'Unmarked', enabled: true},
      'review': {label: 'Review', enabled: true},
      'confirmed': {label: 'Confirmed', enabled: true},
      'ignore': {label: 'Ignore', enabled: false}
    },
    headers: [
      {class: 'text-nowrap', text: 'Status', value: 'status'},
      {class: 'text-nowrap', text: 'Last Updated', value: 'lastUpdated'},
      {class: 'text-nowrap', text: 'Course Number', value: 'sortableCourseNumber', width: '90px'},
      {class: 'text-nowrap', text: 'Course Name', value: 'sortableCourseName', width: '200px'},
      {class: 'text-nowrap', text: 'Instructor', value: 'sortableInstructor'},
      {class: 'text-nowrap', text: 'Department Form', value: 'departmentForm.name', width: '180px'},
      {class: 'text-nowrap', text: 'Evaluation Type', value: 'evaluationType.name', width: '90px'},
      {class: 'text-nowrap', text: 'Evaluation Period', value: 'startDate', width: '200px'}
    ],
    pendingInstructor: null,
    readonly: false,
    rules: {
      currentTermDate: null,
      instructorUid: null
    },
    saving: false,
    searchFilter: '',
    selectedDepartmentForm: null,
    selectedEvaluationStatus: null,
    selectedEvaluationType: null,
    selectedStartDate: null
  }),
  computed: {
    rowValid() {
      return this.rules.currentTermDate(this.selectedStartDate) === true
    }
  },
  methods: {
    afterSelectDepartmentForm(selected) {
      this.alertScreenReader(`${selected.name} department form selected.`)
      this.$putFocusNextTick('input-department-form')
    },
    clearEdit() {
      this.editRowId = null
      this.pendingInstructor = null
      this.saving = false
      this.selectedDepartmentForm = null
      this.selectedEvaluationStatus = null
      this.selectedEvaluationType = null
      this.selectedStartDate = null
    },
    clearPendingInstructor() {
      this.pendingInstructor = null
    },
    onEditEvaluation(evaluation) {
      this.editRowId = evaluation.id
      this.pendingInstructor = evaluation.instructor
      this.selectedDepartmentForm = this.$_.get(evaluation, 'departmentForm')
      this.selectedEvaluationStatus = this.$_.get(evaluation, 'status')
      this.selectedEvaluationType = this.$_.get(evaluation, 'evaluationType.id')
      this.selectedStartDate = evaluation.startDate
    },
    evaluationClass(evaluation, hover) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore muted--text': evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'secondary white--text border-bottom-none': evaluation.id === this.editRowId,
        'evaluation-row-review': evaluation.id !== this.editRowId && evaluation.status === 'review',
        'evaluation-row-xlisting': evaluation.id !== this.editRowId && !evaluation.status && (evaluation.crossListedWith || evaluation.roomSharedWith),
        'primary-contrast primary--text': hover && !this.readonly && !this.isEditing(evaluation)
      }
    },
    evaluationPillClass(evaluation) {
      return {
        'pill-confirmed': evaluation.status === 'confirmed',
        'pill-ignore': evaluation.status === 'ignore',
        'pill-review': evaluation.status === 'review'
      }
    },
    isEditing(evaluation) {
      return this.editRowId === evaluation.id
    },
    filterEnabled(evaluation) {
      const status = evaluation.status || 'unmarked'
      return this.filterTypes[status].enabled
    },
    setPendingInstructor(instructor) {
      this.pendingInstructor = instructor
    },
    saveEvaluation(evaluation) {
      this.saving = true
      const fields = {
        'departmentFormId': this.$_.get(this.selectedDepartmentForm, 'id'),
        'evaluationTypeId': this.selectedEvaluationType,
        'instructorUid': this.$_.get(this.pendingInstructor, 'uid'),
        'status': this.selectedEvaluationStatus
      }
      if (this.selectedStartDate) {
        fields.startDate = this.$moment(this.selectedStartDate).format('YYYY-MM-DD')
      }
      this.updateEvaluation(evaluation.id, evaluation.courseNumber, fields).then(this.clearEdit)
    },
    toggleFilter(type) {
      const filter = this.filterTypes[type]
      filter.enabled = !filter.enabled
      this.alertScreenReader(`Filter ${filter.label} ${filter.enabled ? 'enabled' : 'disabled'}.`)
    },
    updateEvaluation(evaluationId, sectionId, fields) {
      this.alertScreenReader('Saving evaluation row.')
      return new Promise(resolve => {
        if (fields.status === 'confirmed' && !this.validateConfirmable([evaluationId], fields.departmentFormId, fields.evaluationTypeId)) {
          resolve()
        } else {
          this.editEvaluation({evaluationId, sectionId, fields}).then(() => {
            this.alertScreenReader('Changes saved.')
            this.updateSelectedEvaluationIds()
            resolve()
          }, error => {
            this.showErrorDialog(error)
            resolve()
          })
        }
      })
    },
    updateEvaluationsSelected(rowIndex) {
      this.toggleSelectEvaluation(rowIndex)
      this.$root.$emit('update-evaluations-selected')
    },
    selectInstructor(instructor) {
      instructor.emailAddress = instructor.email
      this.setPendingInstructor(instructor)
    }
  },
  created() {
    this.readonly = !this.updateEvaluation
    if (this.readonly) {
      this.headers = [{class: 'text-nowrap', text: 'Department', value: 'department.id'}].concat(this.headers)
    } else {
      this.headers = [{class: 'text-nowrap', text: 'Select'}].concat(this.headers)
    }
    getDepartmentForms().then(data => {
        this.departmentForms = [{id: null, name: 'None'}].concat(data)
    })
    getEvaluationTypes().then(data => {
      this.evaluationTypes = [{id: null, name: 'None'}].concat(data)
    })
    this.rules.currentTermDate = v => {
      const formatted = this.$moment(v).format('YYYY-MM-DD')
      if (formatted > this.$config.currentTermDates.begin && formatted < this.$config.currentTermDates.end) {
        return true
      }
      return 'Date must be within current term.'
    }
    this.rules.instructorUid = () => {
      return this.$_.get(this.pendingInstructor, 'uid') ? true : 'Instructor is required.'}
  },
}
</script>

<style>
tr.border-bottom-none td {
  border-bottom: none !important;
}

tr.border-top-none td {
  border-top: none !important;
}

.evaluation-input .v-messages__message {
  color: #fff !important;
}
</style>

<style scoped>
.evaluation-edit-btn {
  width: 150px;
}
.evaluation-error {
  font-size: 0.8em;
  font-style: italic;
}
.filter {
  color: #fff;
}
.filter-active {
  background-color: #0074aa !important;
}
.filter-inactive {
  background-color: #999 !important;
}
.hidden {
  visibility: hidden;
}
.input-department-form {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.pill {
  border: 1px solid #999;
  border-radius: 5px;
  color: #fff;
  font-size: 0.8em;
  font-weight: bold;
  margin: 0;
  padding: 3px 10px;
  text-align: center;
  text-transform: uppercase;
}
.pill-confirmed {
  background-color: #666;
}
.pill-ignore {
  background-color: #777;
}
.pill-invisible {
  border: none;
}
.pill-review {
  background-color: #595;
}
.position-relative {
  position: relative;
}
.scrollable-table {
  max-height: 500px;
  overflow-y: scroll;
}
.status-select {
  left: 0;
  max-width: fit-content;
  position: absolute;
  top: 14px;
}
.xlisting-note {
  font-size: 0.8em;
}
</style>

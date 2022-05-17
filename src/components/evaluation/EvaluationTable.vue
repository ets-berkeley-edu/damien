<template>
  <div v-if="evaluations">
    <div class="sticky" :class="$vuetify.theme.dark ? 'sticky-dark' : 'sticky-light'">
      <EvaluationActions v-if="!readonly" />
      <v-row class="mt-0">
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
        <v-col v-if="!readonly" class="ma-3 text-right">
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
    </div>
    <v-data-table
      id="evaluation-table"
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
                <td v-if="readonly" :id="`evaluation-${rowIndex}-department`" class="py-1">
                  <router-link :to="`/department/${$_.get(evaluation.department, 'id')}`">
                    {{ $_.get(evaluation.department, 'name') }}
                  </router-link>
                </td>
                <td v-if="!readonly && allowEdits" class="text-center">
                  <v-checkbox
                    v-if="!isEditing(evaluation)"
                    :id="`evaluation-${rowIndex}-checkbox`"
                    :value="evaluation.isSelected"
                    :color="`${hover ? 'primary' : 'tertiary'}`"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
                    @change="updateEvaluationsSelected(evaluation.id)"
                  ></v-checkbox>
                </td>
                <td :id="`evaluation-${rowIndex}-status`" class="align-middle position-relative">
                  <div
                    v-if="!isEditing(evaluation) && (!hover || !allowEdits || readonly) && evaluation.status"
                    class="pill mx-auto"
                    :class="evaluationPillClass(evaluation)"
                  >
                    {{ evaluation.status }}
                  </div>
                  <div
                    v-if="allowEdits && !isEditing(evaluation) && ((hover && !readonly) || !evaluation.status)"
                    class="pill pill-invisible mx-auto pl-0"
                  >
                    <v-btn
                      class="primary--text"
                      :class="{'hidden': isEditing(evaluation) || !hover}"
                      block
                      :disabled="!allowEdits"
                      text
                      @click="onEditEvaluation(evaluation)"
                      @keypress.enter.prevent="onEditEvaluation(evaluation)"
                    >
                      Edit
                    </v-btn>
                  </div>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <label id="select-evaluation-status-label" for="select-evaluation-status">
                      Status:
                    </label>
                    <select
                      id="select-evaluation-status"
                      v-model="selectedEvaluationStatus"
                      class="native-select-override light d-block mx-auto"
                    >
                      <option v-for="s in evaluationStatuses" :key="s.text" :value="s.value">{{ s.text }}</option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-lastUpdated`" class="align-middle">
                  {{ $moment(evaluation.lastUpdated) | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${rowIndex}-courseNumber`" class="align-middle">
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
                <td class="align-middle">
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
                <td :id="`evaluation-${rowIndex}-instructor`" class="align-middle">
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.firstName }}
                    {{ evaluation.instructor.lastName }}
                    ({{ evaluation.instructor.uid }})
                  </div>
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.emailAddress }}
                  </div>
                  <div v-if="!evaluation.instructor && isEditing(evaluation) && allowEdits">
                    <div class="mt-1 pb-2">
                      <label id="input-instructor-lookup-autocomplete-label" for="input-instructor-lookup-autocomplete">
                        Instructor<span class="sr-only"> search by name or UID</span>:
                      </label>
                      <PersonLookup
                        id="input-instructor-lookup-autocomplete"
                        :instructor-lookup="true"
                        :on-select-result="selectInstructor"
                        solo
                      />
                    </div>
                    <div v-if="pendingInstructor">
                      {{ pendingInstructor.firstName }}
                      {{ pendingInstructor.lastName }}
                      ({{ pendingInstructor.uid }})
                    </div>
                    <div v-if="pendingInstructor">
                      {{ pendingInstructor.emailAddress }}
                    </div>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-departmentForm`" class="align-middle">
                  <div
                    v-if="evaluation.departmentForm && !isEditing(evaluation)"
                    :class="{'error--text': evaluation.conflicts.departmentForm}"
                  >
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
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <label id="select-department-form-label" for="select-department-form">
                      Department Form:
                    </label>
                    <vue-select
                      id="select-department-form"
                      v-model="selectedDepartmentForm"
                      class="vue-select-override light"
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
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-evaluationType`" class="align-middle">
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
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <label id="select-evaluation-type-label" for="select-evaluation-type">
                      Evaluation Type:
                    </label>
                    <select
                      id="select-evaluation-type"
                      v-model="selectedEvaluationType"
                      class="native-select-override light"
                    >
                      <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-period`" class="align-middle">
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
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <div class="d-flex align-center">
                      <label id="input-evaluation-start-date-label" for="input-evaluation-start-date">
                        Start date:
                      </label>
                      <div v-if="!selectedStartDate" class="evaluation-error">
                        <v-icon class="pl-2 pr-1" small color="white">mdi-alert-circle</v-icon>Required
                      </div>
                    </div>
                    <c-date-picker
                      v-model="selectedStartDate"
                      :min-date="new Date(evaluation.meetingDates.start)"
                      :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
                      title-position="left"
                    >
                      <template v-slot="{ inputValue, inputEvents }">
                        <input
                          id="input-evaluation-start-date"
                          class="datepicker-input input-override light mt-0"
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
  <div v-else class="no-eligible-sections">
    <span>No eligible sections to load. You may still add a section manually.</span>
  </div>
</template>

<script>
import {getDepartmentForms} from '@/api/departmentForms'
import {getEvaluationTypes} from '@/api/evaluationTypes'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationActions from '@/components/evaluation/EvaluationActions'
import PersonLookup from '@/components/admin/PersonLookup'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationTable',
  mixins: [Context, DepartmentEditSession, Util],
  components: { EvaluationActions, PersonLookup },
  props: {
    readonly: {
      type: Boolean,
      required: false
    }
  },
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
      {align: 'center', class: 'text-nowrap', text: 'Status', value: 'status', width: '130px'},
      {class: 'text-nowrap', text: 'Last Updated', value: 'lastUpdated', width: '75px'},
      {class: 'text-nowrap', text: 'Course Number', value: 'sortableCourseNumber', width: '80px'},
      {class: 'text-nowrap course-name', text: 'Course Name', value: 'sortableCourseName'},
      {class: 'text-nowrap', text: 'Instructor', value: 'sortableInstructor', width: '200px'},
      {class: 'text-nowrap', text: 'Department Form', value: 'departmentForm.name', width: '180px'},
      {class: 'text-nowrap', text: 'Evaluation Type', value: 'evaluationType.name', width: '175px'},
      {class: 'text-nowrap', text: 'Evaluation Period', value: 'startDate', width: '180px'}
    ],
    pendingInstructor: null,
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
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
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
      this.$putFocusNextTick(`${this.readonly ? '' : 'select-evaluation-status'}`)
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
    updateEvaluationsSelected(evaluationId) {
      this.toggleSelectEvaluation(evaluationId)
      this.$root.$emit('update-evaluations-selected')
    },
    selectInstructor(instructor) {
      instructor.emailAddress = instructor.email
      this.setPendingInstructor(instructor)
    }
  },
  created() {
    if (this.readonly) {
      this.headers = [{class: 'text-nowrap', text: 'Department', value: 'department.id'}].concat(this.headers)
    } else if (this.allowEdits) {
      this.headers = [{class: 'text-nowrap', text: 'Select', width: '40px'}].concat(this.headers)
    }
    getDepartmentForms().then(data => {
        this.departmentForms = [{id: null, name: 'Revert'}].concat(data)
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
.course-name {
  min-width: 250px;
}
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
.align-middle {
  vertical-align: middle;
}
.evaluation-edit-btn {
  width: 150px;
}
.evaluation-error {
  font-size: 0.8em;
  font-style: italic;
}
.evaluation-row {
  vertical-align: top;
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
.no-eligible-sections {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 40px;
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
  width: 90px;
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
.sticky {
  position: sticky;
  margin: 1px !important;
  top: 60px;
  z-index: 1;
}
.sticky-dark {
  background-color: #222;
}
.sticky-light {
  background-color: #fff;
}
.xlisting-note {
  font-size: 0.8em;
}
</style>

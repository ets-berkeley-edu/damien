<template>
  <div>
    <div class="ma-4 text-right">
      Show statuses:
      <v-btn
        v-for="type in $_.keys(filterTypes)"
        :id="`evaluations-filter-${type}`"
        :key="type"
        role="tablist"
        class="filter ml-2 pl-2 pr-2 text-center"
        :class="{
          'secondary': filterTypes[type].enabled,
          'filter-inactive': !filterTypes[type].enabled
        }"
        aria-controls="timeline-messages"
        :aria-selected="filterTypes[type].enabled"
        @click="toggleFilter(type)"
      >
        {{ filterTypes[type].label }}
      </v-btn>
    </div>
    <v-data-table
      id="evaluation-table"
      disable-pagination
      :headers="headers"
      hide-default-footer
      :items="evaluations"
    >
      <template #body="{items}">
        <tbody>
          <template v-for="(evaluation, evaluationId) in items">
            <v-hover v-if="filterEnabled(evaluation)" v-slot="{ hover }" :key="evaluation.id">
              <tr 
                class="evaluation-row"
                :class="evaluationClass(evaluation, hover)"
              >
                <td>
                  <v-checkbox
                    :id="`evaluation-${evaluationId}-checkbox`"
                    v-model="evaluation.isSelected"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
                    @change="updateEvaluationsSelected"
                  ></v-checkbox>
                </td>
                <td :id="`evaluation-${evaluationId}-status`">
                  <div
                    v-if="(!hover || isEditing(evaluation)) && evaluation.status"
                    class="pill"
                    :class="evaluationPillClass(evaluation)"
                  >
                    {{ evaluation.status }}
                  </div>
                  <div
                    v-if="(hover && !isEditing(evaluation)) || !evaluation.status"
                    class="pill pill-invisible"
                  >
                    <v-btn
                      class="primary--text"
                      :class="{'hidden': isEditing(evaluation) || !hover}"
                      block
                      text
                      @click="editEvaluation(evaluation)"
                    >
                      Edit
                    </v-btn>
                  </div>
                </td>
                <td :id="`evaluation-${evaluationId}-lastUpdated`">
                  {{ evaluation.lastUpdated | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${evaluationId}-courseNumber`">
                  {{ evaluation.courseNumber }}
                  <div v-if="evaluation.crossListedWith" class="xlisting-note">
                    (Cross-listed with section {{ evaluation.crossListedWith }})
                  </div>
                  <div v-if="evaluation.roomSharedWith" class="xlisting-note">
                    (Room shared with section {{ evaluation.roomSharedWith }})
                  </div>
                </td>
                <td>
                  <div :id="`evaluation-${evaluationId}-courseName`">
                    {{ evaluation.subjectArea }} 
                    {{ evaluation.catalogId }}
                    {{ evaluation.instructionFormat }}
                    {{ evaluation.sectionNumber }}
                  </div>
                  <div :id="`evaluation-${evaluationId}-courseTitle`">
                    {{ evaluation.courseTitle }}
                  </div>
                </td>
                <td :id="`evaluation-${evaluationId}-instructor`">
                  <div v-if="!isEditing(evaluation) && evaluation.instructor">
                    {{ evaluation.instructor.firstName }}
                    {{ evaluation.instructor.lastName }}
                    ({{ evaluation.instructor.uid }})
                  </div>
                  <div v-if="!isEditing(evaluation) && evaluation.instructor">
                    {{ evaluation.instructor.emailAddress }}
                  </div>
                  <div v-if="isEditing(evaluation) && pendingInstructor">
                    <div class="py-2">
                      {{ pendingInstructor.firstName }}
                      {{ pendingInstructor.lastName }}
                      ({{ pendingInstructor.uid }})
                    </div>
                    <div class="pb-2">
                      <v-btn
                        :id="`evaluation-${evaluationId}-change-instructor`"
                        @click="clearPendingInstructor"
                        @keydown.enter="clearPendingInstructor"
                      >
                        Change
                      </v-btn>
                    </div>
                  </div>
                  <div v-if="isEditing(evaluation) && !pendingInstructor">
                    <PersonLookup
                      v-if="isEditing(evaluation)"
                      :instructor-lookup="true"
                      :on-select-result="setPendingInstructor"
                      solo
                    />
                  </div>
                </td>
                <td :id="`evaluation-${evaluationId}-departmentForm`">
                  <div v-if="evaluation.departmentForm && !isEditing(evaluation)" :class="{'error': evaluation.conflicts.departmentForm}">
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
                  <v-select
                    v-if="isEditing(evaluation)"
                    id="select-department-form"
                    v-model="selectedDepartmentForm"
                    item-text="name"
                    item-value="id"
                    :items="departmentForms"
                    hide-details="auto"
                    label="Select..."
                    solo
                  />
                </td>
                <td :id="`evaluation-${evaluationId}-evaluationType`">
                  <div v-if="evaluation.evaluationType && !isEditing(evaluation)" :class="{'error': evaluation.conflicts.evaluationType}">
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
                  <v-select
                    v-if="isEditing(evaluation)"
                    id="select-evaluation-type"
                    v-model="selectedEvaluationType"
                    item-text="name"
                    item-value="id"
                    :items="evaluationTypes"
                    hide-details="auto"
                    label="Select..."
                    solo
                  />
                </td>
                <td :id="`evaluation-${evaluationId}-startDate`">
                  <span v-if="!isEditing(evaluation)" :class="{'error': evaluation.conflicts.startDate}">
                    {{ evaluation.startDate | moment('MM/DD/YYYY') }}
                    <div v-for="(conflict, index) in evaluation.conflicts.startDate" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value | moment('MM/DD/YYYY') }} from {{ conflict.department }} department
                    </div>
                  </span>
                  <v-text-field
                    v-if="isEditing(evaluation)"
                    v-model="selectedStartDate"
                    type="date"
                    hide-details="auto"
                    class="evaluation-input"
                    :rules="[rules.currentTermDate, rules.beforeEndDate]"
                    solo
                  />
                </td>
                <td :id="`evaluation-${evaluationId}-endDate`">
                  <span v-if="!isEditing(evaluation)" :class="{'error': evaluation.conflicts.endDate}">
                    {{ evaluation.endDate | moment('MM/DD/YYYY') }}
                    <div v-for="(conflict, index) in evaluation.conflicts.endDate" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value | moment('MM/DD/YYYY') }} from {{ conflict.department }} department
                    </div>
                  </span>
                  <v-text-field
                    v-if="isEditing(evaluation)"
                    v-model="selectedEndDate"
                    type="date"
                    hide-details="auto"
                    class="evaluation-input"
                    :rules="[rules.currentTermDate, rules.afterStartDate]"
                    solo
                  />
                </td>
                <td>
                  <div class="d-flex align-center" :class="{'hidden': !isEditing(evaluation)}">
                    <v-btn
                      class="ma-1"
                      color="primary"
                      :disabled="!rowValid"
                      @click="saveEvaluation(evaluation)"
                    >
                      Save
                    </v-btn>
                    <v-btn class="ma-1" @click="cancelEdit">Cancel</v-btn>
                  </div>
                </td>
              </tr>
            </v-hover>
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
import PersonLookup from '@/components/admin/PersonLookup'

export default {
  name: 'EvaluationTable',
  components: {PersonLookup},
  mixins: [Context],
  props: {
    evaluations: {
      required: true,
      type: Array
    },
    updateEvaluation: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    departmentForms: [],
    editRowId: null,
    evaluationTypes: [],
    filterTypes: {
      'unmarked': {label: 'Unmarked', enabled: true},
      'review': {label: 'Review', enabled: true},
      'confirmed': {label: 'Confirmed', enabled: true},
      'ignore': {label: 'Ignore', enabled: false}
    },
    headers: [
      {text: 'Select'},
      {text: 'Status', value: 'status'},
      {text: 'Last Updated', value: 'lastUpdated'},
      {text: 'Course Number', value: 'sortableCourseNumber'},
      {text: 'Course Name', value: 'courseName'},
      {text: 'Instructor', value: 'instructorUid'},
      {text: 'Department Form', value: 'departmentForm'},
      {text: 'Evaluation Type', value: 'evaluationType'},
      {text: 'Course Start Date', value: 'startDate'},
      {text: 'Course End Date', value: 'endDate'}
    ],
    pendingInstructor: null,
    rules: {
      afterStartDate: null,
      currentTermDate: null,
    },
    selectedDepartmentForm: null,
    selectedEndDate: null,
    selectedEvaluationType: null,
    selectedStartDate: null
  }),
  computed: {
    rowValid() {
      return (
        this.rules.currentTermDate(this.selectedStartDate) === true &&
        this.rules.currentTermDate(this.selectedEndDate) === true &&
        this.rules.afterStartDate(this.selectedEndDate) === true &&
        this.rules.beforeEndDate(this.selectedStartDate) === true
      )
    }
  },
  methods: {
    cancelEdit() {
      this.editRowId = null
      this.pendingInstructor = null
      this.selectedDepartmentForm = null
      this.selectedEndDate = null
      this.selectedEvaluationType = null
      this.selectedStartDate = null
    },
    clearPendingInstructor() {
      this.pendingInstructor = null
    },
    editEvaluation(evaluation) {
      this.editRowId = evaluation.id
      this.pendingInstructor = evaluation.instructor
      this.selectedDepartmentForm = this.$_.get(evaluation, 'departmentForm.id')
      this.selectedEndDate = evaluation.endDate
      this.selectedEvaluationType = this.$_.get(evaluation, 'evaluationType.id')
      this.selectedStartDate = evaluation.startDate
    },
    evaluationClass(evaluation, hover) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore muted--text': evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'evaluation-row-editing': evaluation.id === this.editRowId,
        'evaluation-row-review': evaluation.id !== this.editRowId && evaluation.status === 'review',
        'evaluation-row-xlisting': evaluation.id !== this.editRowId && !evaluation.status && (evaluation.crossListedWith || evaluation.roomSharedWith),
        'primary-contrast primary--text': hover
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
      const fields = {
        'departmentFormId': this.selectedDepartmentForm,
        'endDate': this.selectedEndDate,
        'evaluationTypeId': this.selectedEvaluationType,
        'instructorUid': this.pendingInstructor.uid,
        'startDate': this.selectedStartDate,
      }
      this.updateEvaluation(evaluation.id, fields)
    },
    toggleFilter(type) {
      const filter = this.filterTypes[type]
      filter.enabled = !filter.enabled
      this.alertScreenReader(`Filter ${filter.label} ${filter.enabled ? 'enabled' : 'disabled'}.`)
    },
    updateEvaluationsSelected() {
      this.$root.$emit('update-evaluations-selected')
    }
  },
  created() {
    getDepartmentForms().then(data => this.departmentForms = data)
    getEvaluationTypes().then(data => this.evaluationTypes = data)
    this.rules.afterStartDate = v => (v > this.selectedStartDate) || 'End date must be after start date.'
    this.rules.beforeEndDate = v => (v < this.selectedEndDate) || 'End date must be after start date.'
    this.rules.currentTermDate = v => {
      if (v > this.$config.currentTermDates.begin && v < this.$config.currentTermDates.end) {
        return true
      }
      return 'Date must be within current term.'
    }
  },
}
</script>

<style>
.evaluation-input .v-messages__message {
  color: #fff !important;
}
</style>

<style scoped>
.evaluation-error {
  font-size: 0.8em;
  font-style: italic;
}
.evaluation-row-editing, .evaluation-row-editing:hover {
  background-color: #369 !important;
  color: #fff !important;
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
.xlisting-note {
  font-size: 0.8em;
}
</style>

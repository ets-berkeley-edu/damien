<template>
  <div>
    <v-row>
      <v-col>
        <v-text-field
          v-model="searchFilter"
          class="ml-4"
          append-icon="mdi-magnify"
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
      </v-col>
    </v-row>
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
          <template v-for="(evaluation, evaluationId) in items">
            <v-hover v-if="filterEnabled(evaluation)" v-slot="{ hover }" :key="evaluation.id">
              <tr
                class="evaluation-row"
                :class="evaluationClass(evaluation, hover)"
              >
                <td v-if="readonly" :id="`evaluation-${evaluationId}-department`">
                  <router-link :to="`/department/${evaluation.department.id}`">
                    {{ evaluation.department.name }}
                  </router-link>
                </td>
                <td v-if="!readonly">
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
                    v-if="(!hover || readonly || isEditing(evaluation)) && evaluation.status"
                    class="pill"
                    :class="evaluationPillClass(evaluation)"
                  >
                    {{ evaluation.status }}
                  </div>
                  <div
                    v-if="(hover && !readonly && !isEditing(evaluation)) || !evaluation.status"
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
                    :options="departmentForms"
                    label="name"
                    :clearable="false"
                    class="vue-select-override"
                  >
                  </vue-select>
                </td>
                <td :id="`evaluation-${evaluationId}-evaluationType`">
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
                    class="native-select-override"
                  >
                    <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
                  </select>
                </td>
                <td :id="`evaluation-${evaluationId}-period`">
                  <span v-if="$_.get(evaluation, 'evaluationPeriod.start') && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.evaluationPeriod}">
                    <div>{{ evaluation.evaluationPeriod.start | moment('MM/DD/YY') }} - {{ evaluation.evaluationPeriod.end | moment('MM/DD/YY') }}</div>
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
                      {{ evaluation.evaluationPeriod.modularCutoff > selectedStartDate ? 2 : 3 }} weeks starting:
                    </div>
                    <div v-if="!selectedStartDate" class="evaluation-error">
                      <v-icon small color="white">mdi-alert-circle</v-icon> Start date required
                    </div>
                    <c-date-picker
                      v-model="selectedStartDate"
                      :min-date="new Date(evaluation.startDate)"
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
                </td>
                <td v-if="!readonly">
                  <div class="d-flex align-center" :class="{'hidden': !isEditing(evaluation)}">
                    <v-btn
                      class="ma-1"
                      color="primary"
                      :disabled="!rowValid || saving"
                      @click.prevent="saveEvaluation(evaluation)"
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
                    <v-btn class="ma-1" :disabled="saving" @click="clearEdit">Cancel</v-btn>
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
      required: false,
      default: null,
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
      {text: 'Status', value: 'status'},
      {text: 'Last Updated', value: 'lastUpdated'},
      {text: 'Course Number', value: 'sortableCourseNumber', width: '100px'},
      {text: 'Course Name', value: 'sortableCourseName', width: '200px'},
      {text: 'Instructor', value: 'sortableInstructor'},
      {text: 'Department Form', value: 'departmentForm.name', width: '180px'},
      {text: 'Evaluation Type', value: 'evaluationType.name'},
      {text: 'Evaluation Period', value: 'evaluationPeriod.start', width: '200px'},
      {text: ''}
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
    selectedEvaluationType: null,
    selectedStartDate: null
  }),
  computed: {
    rowValid() {
      return this.rules.currentTermDate(this.selectedStartDate) === true
          && this.rules.instructorUid(this.pendingInstructor) === true
    }
  },
  methods: {
    clearEdit() {
      this.editRowId = null
      this.pendingInstructor = null
      this.saving = false
      this.selectedDepartmentForm = null
      this.selectedEvaluationType = null
      this.selectedStartDate = null
    },
    clearPendingInstructor() {
      this.pendingInstructor = null
    },
    editEvaluation(evaluation) {
      this.editRowId = evaluation.id
      this.pendingInstructor = evaluation.instructor
      this.selectedDepartmentForm = this.$_.get(evaluation, 'departmentForm')
      this.selectedEvaluationType = this.$_.get(evaluation, 'evaluationType.id')
      this.selectedStartDate = evaluation.evaluationPeriod.start
    },
    evaluationClass(evaluation, hover) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore muted--text': evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'secondary white--text': evaluation.id === this.editRowId,
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
        'instructorUid': this.$_.get(this.pendingInstructor, 'uid')
      }
      if (this.selectedStartDate) {
        const duration = evaluation.evaluationPeriod.modularCutoff > this.selectedStartDate ? 13 : 20
        fields.endDate = this.$moment(this.selectedStartDate).add(duration, 'days').format('YYYY-MM-DD')
      }
      this.updateEvaluation(evaluation.id, evaluation.courseNumber, fields).then(this.clearEdit)
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
    this.readonly = !this.updateEvaluation
    if (this.readonly) {
      this.headers = [{text: 'Department', value: 'department.id'}].concat(this.headers)
    } else {
      this.headers = [{text: 'Select'}].concat(this.headers)
    }
    this.$_.each(this.evaluations, e => {
      e.sortableCourseName = `${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber} ${e.courseTitle}`
      e.sortableCourseNumber = e.sortableCourseNumber || e.courseNumber
      if (e.instructor) {
        e.sortableInstructor = `${e.instructor.lastName} ${e.instructor.firstName} ${e.instructor.uid} ${e.instructor.emailAddress}`
      } else {
        e.sortableInstructor = ''
      }
      e.evaluationPeriod.start = this.$moment(e.evaluationPeriod.start).toDate()
      e.evaluationPeriod.end = this.$moment(e.endDate).toDate()
      e.evaluationPeriod.modularCutoff = this.$moment(e.startDate).add(76, 'days').toDate()
    })
    getDepartmentForms().then(data => this.departmentForms = data)
    getEvaluationTypes().then(data => this.evaluationTypes = data)
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
.evaluation-input .v-messages__message {
  color: #fff !important;
}

.input-override {
  background-color: #fff !important;
  border-radius: 5px;
  border: 1px solid #333333;
  margin: 5px 0;
  padding: 5px;
}

.native-select-override {
  border-radius: 5px;
  border: 1px solid #333333;
  padding: 10px;
  -webkit-appearance: menulist !important; /* override vuetify style */
  -moze-appearance: menulist !important; /* override vuetify style */
  appearance: menulist !important; /* override vuetify style */
  background-color: #fff !important;
  margin-bottom: 0;
}

.vue-select-override {
  color: #000 !important;
  background-color: #fff !important;
  border-radius: 5px;
  border: 1px solid #333333;
  padding: 0;
}

.vs__dropdown-toggle {
  padding: 5px !important;
}
</style>

<style scoped>
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

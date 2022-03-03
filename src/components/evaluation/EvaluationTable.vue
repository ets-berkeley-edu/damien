<template>
  <div>
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
            <v-hover v-slot="{ hover }" :key="evaluation.id">
              <tr 
                class="evaluation-row"
                :class="evaluationClass(evaluation)"
              >
                <td>
                  <v-checkbox
                    :id="`evaluation-${evaluationId}-checkbox`"
                    v-model="evaluation.isSelected"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
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
                  <v-btn
                    v-if="hover && !isEditing(evaluation)"
                    block
                    text
                    @click="editEvaluation(evaluation)"
                  >
                    Edit
                  </v-btn>
                </td>
                <td :id="`evaluation-${evaluationId}-lastUpdated`">
                  {{ evaluation.lastUpdated | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${evaluationId}-courseNumber`">
                  {{ evaluation.courseNumber }}
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
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.firstName }}
                    {{ evaluation.instructor.lastName }}
                    ({{ evaluation.instructor.uid }})
                  </div>
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.emailAddress }}
                  </div>
                </td>
                <td :id="`evaluation-${evaluationId}-departmentForm`">
                  <span v-if="evaluation.departmentForm && !isEditing(evaluation)">
                    {{ evaluation.departmentForm.name }}
                  </span>
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
                  <span v-if="evaluation.evaluationType && !isEditing(evaluation)">
                    {{ evaluation.evaluationType.name }}
                  </span>
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
                  <span v-if="!isEditing(evaluation)">
                    {{ evaluation.startDate | moment('MM/DD/YYYY') }}
                  </span>
                  <v-text-field
                    v-if="isEditing(evaluation)"
                    v-model="selectedStartDate"
                    type="date"
                    hide-details="auto"
                    solo
                  />
                </td>
                <td :id="`evaluation-${evaluationId}-endDate`">
                  <span v-if="!isEditing(evaluation)">
                    {{ evaluation.endDate | moment('MM/DD/YYYY') }}
                  </span>
                  <v-text-field
                    v-if="isEditing(evaluation)"
                    v-model="selectedEndDate"
                    type="date"
                    hide-details="auto"
                    solo
                  />
                </td>
                <td>
                  <div v-if="isEditing(evaluation)" class="d-flex align-center">
                    <v-btn class="ma-1" color="primary" @click="saveEvaluation(evaluation)">Save</v-btn>
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

export default {
  name: 'EvaluationTable',
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
    headers: [
      {text: 'Select'},
      {text: 'Status', value: 'status'},
      {text: 'Last Updated', value: 'lastUpdated'},
      {text: 'Course Number', value: 'courseNumber'},
      {text: 'Course Name', value: 'courseName'},
      {text: 'Instructor', value: 'instructorUid'},
      {text: 'Department Form', value: 'departmentForm'},
      {text: 'Evaluation Type', value: 'evaluationType'},
      {text: 'Course Start Date', value: 'startDate'},
      {text: 'Course End Date', value: 'endDate'}
    ],
    selectedDepartmentForm: null,
    selectedEndDate: null,
    selectedEvaluationType: null,
    selectedStartDate: null
  }),
  methods: {
    cancelEdit() {
      this.editRowId = null
      this.selectedDepartmentForm = null
      this.selectedEndDate = null
      this.selectedEvaluationType = null
      this.selectedStartDate = null
    },
    editEvaluation(evaluation) {
      this.editRowId = evaluation.id
      this.selectedDepartmentForm = this.$_.get(evaluation, 'departmentForm.id')
      this.selectedEndDate = evaluation.endDate
      this.selectedEvaluationType = this.$_.get(evaluation, 'evaluationType.id')
      this.selectedStartDate = evaluation.startDate
    },
    evaluationClass(evaluation) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore': evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'evaluation-row-editing': evaluation.id === this.editRowId,
        'evaluation-row-review': evaluation.id !== this.editRowId && evaluation.status === 'review'
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
    saveEvaluation(evaluation) {
      const fields = {
        'departmentFormId': this.selectedDepartmentForm,
        'endDate': this.selectedEndDate,
        'evaluationTypeId': this.selectedEvaluationType,
        'startDate': this.selectedStartDate,
      }
      this.updateEvaluation(evaluation.id, fields)
    }
  },
  created() {
    getDepartmentForms().then(data => this.departmentForms = data)
    getEvaluationTypes().then(data => this.evaluationTypes = data)
  },
}
</script>

<style scoped>
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
.pill-review {
  background-color: #595;
}
.evaluation-row:hover {
  background-color: #def !important;
  color: #069 !important;
}
.evaluation-row-confirmed {
  background-color: #eee;
  color: #666;
}
.evaluation-row-editing, .evaluation-row-editing:hover {
  background-color: #369 !important;
  color: #fff !important;
}
.evaluation-row-ignore {
  background-color: #ddd;
  color: #777;
}
.evaluation-row-review {
  background-color: #efe;  
}
</style>

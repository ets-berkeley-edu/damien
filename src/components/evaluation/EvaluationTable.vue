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
            <tr :key="evaluation.id">
              <td>
                <v-simple-checkbox
                  :id="`evaluation-${evaluationId}-checkbox`"
                  :ripple="false"
                ></v-simple-checkbox>
              </td>
              <td :id="`evaluation-${evaluationId}-status`">
                {{ evaluation.status }}
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
                <span v-if="evaluation.departmentForm">
                  {{ evaluation.departmentForm.name }}
                </span>
              </td>
              <td :id="`evaluation-${evaluationId}-evaluationType`">
                <span v-if="evaluation.evaluationType">
                  {{ evaluation.evaluationType.name }}
                </span>
              </td>
              <td :id="`evaluation-${evaluationId}-startDate`">
                {{ evaluation.startDate | moment('MM/DD/YYYY') }}
              </td>
              <td :id="`evaluation-${evaluationId}-endDate`">
                {{ evaluation.endDate | moment('MM/DD/YYYY') }}
              </td>
            </tr>
          </template>
        </tbody>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  name: 'EvaluationTable',
  props: {
    evaluations: {
      required: true,
      type: Array
    }
  },
  data: () => ({
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
    ]
  })
}
</script>

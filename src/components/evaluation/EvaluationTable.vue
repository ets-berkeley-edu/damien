<template>
  <div>
    <v-data-table
      id="evaluation-table"
      disable-pagination
      :headers="headers"
      hide-default-footer
      :items="sections"
    >
      <template #body="{items}">
        <tbody>
          <template v-for="(section, sectionIndex) in items">
            <tr :key="section.courseNumber">
              <td :id="`section-status-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-status-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.status }}
                </div>
              </td>
              <td :id="`section-lastUpdated-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-lastUpdated-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.lastUpdated }}
                </div>
              </td>
              <td :id="`section-courseNumber-${sectionIndex}`">
                {{ section.courseNumber }}
              </td>
              <td :id="`section-courseName-${sectionIndex}`">
                {{ section.subjectArea }} {{ section.catalogId }} {{ section.instructionFormat }} {{ section.sectionNumber }} {{ section.courseTitle }}
              </td>
              <td :id="`section-instructors-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-instructor-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.instructor.firstName }} {{ evaluation.instructor.lastName }} ({{ evaluation.instructor.uid }}) {{ evaluation.instructor.emailAddress }}
                </div>
              </td>
              <td :id="`section-departmentForm-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-departmentForm-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.departmentForm }}
                </div>
              </td>
              <td :id="`section-evaluationType-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-evaluationType-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.evaluationType }}
                </div>
              </td>
              <td :id="`section-startDate-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-startDate-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.startDate }}
                </div>
              </td>
              <td :id="`section-endDate-${sectionIndex}`">
                <div v-for="(evaluation, evaluationIndex) in section.evaluations" :id="`section-endDate-${sectionIndex}-${evaluationIndex}`" :key="evaluationIndex">
                  {{ evaluation.endDate }}
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
export default {
  name: 'EvaluationTable',
  props: {
    sections: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    headers: [
      {text: 'Status', value: 'status'},
      {text: 'Last Updated', value: 'lastUpdated'},
      {text: 'Course Number', value: 'courseNumber'},
      {text: 'Course Name', value: 'courseName'},
      {text: 'Instructor(s)', value: 'instructorUid'},
      {text: 'Department Form', value: 'departmentForm'},
      {text: 'Evaluation Type', value: 'evaluationType'},
      {text: 'Course Start Date', value: 'startDate'},
      {text: 'Course End Date', value: 'endDate'}
    ]
  })
}
</script>

<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

const $_isInvalid = (e, evaluationIds, fields) => {
  return _.includes(evaluationIds, e.id) && !(
    (e.departmentForm || _.get(fields, 'departmentFormId')) &&
    (e.evaluationType || _.get(fields, 'evaluationTypeId')) &&
    (e.instructor || _.get(fields, 'instructorUid'))
  )
}

export default {
  name: 'DepartmentEditSession',
  data: () => ({
    NUMBER_OF_THE_BEAST: '666'
  }),
  computed: {
    ...mapGetters('departmentEditSession', [
      'activeDepartmentForms',
      'allDepartmentForms',
      'contacts',
      'department',
      'disableControls',
      'errorDialog',
      'errorDialogText',
      'evaluations',
      'note',
      'selectedEvaluationIds',
      'showTheOmenPoster'
    ]),
    evaluationStatuses() {
      return [
        {text: 'None', value: 'none'},
        {text: 'To-do', value: 'review'},
        {text: 'Done', value: 'confirmed'},
        {text: 'Ignore', value: 'ignore'}
      ]
    }
  },
  methods: {
    validateConfirmable(evaluationIds, fields) {
      if (this.$_.some(this.evaluations, e => $_isInvalid(e, evaluationIds, fields))) {
        this.showErrorDialog('Cannot confirm evaluations with missing fields.')
        return false
      }
      return true
    },
    validateDuplicable(evaluationIds, fields) {
      if (fields.midterm === 'true') {
        return true
      }
      const duplicatingEvaluations = this.$_.filter(this.evaluations, e => this.$_.includes(evaluationIds, e.id))
      const conflicts = this.$_.intersectionWith(duplicatingEvaluations, this.evaluations, (dupe, e) => {
        return e.courseNumber === dupe.courseNumber
            && this.$_.get(e.instructor, 'uid', NaN) === (fields.instructorUid || this.$_.get(dupe.instructor, 'uid', NaN))
      })
      if (conflicts.length) {
        this.showErrorDialog('Cannot create identical duplicate evaluations.')
        return false
      }
      return true
    },
    validateMarkAsDone(selectedEvaluations) {
      let warningMessage
      const now = this.$moment()
      const evaluationsInProgress = this.$_.filter(selectedEvaluations, e => now.isAfter(e.startDate))
      if (evaluationsInProgress.length) {
        // Grab the first in-progress evaluation, to give the user an example of the problem.
        const e = evaluationsInProgress[0]
        const course = `${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber}`
        let startDate = this.$moment(e.startDate)
        startDate = startDate.format(startDate.year() === now.year() ? 'MMMM Do' : 'MMMM Do, YYYY')

        if (evaluationsInProgress.length === 1) {
          warningMessage = `The ${course} evaluation period started on ${startDate}.
            Are you sure you want to mark it as done?`
        } else {
          warningMessage = `Some of the selected evaluation periods have already started.
            For example, ${course} evaluation period started on ${startDate}.
            Are you sure you want to mark those as done?`
        }
      }
      return warningMessage
    },
    ...mapActions('departmentEditSession', [
      'addSection',
      'deleteContact',
      'deselectAllEvaluations',
      'dismissErrorDialog',
      'editEvaluation',
      'filterSelectedEvaluations',
      'init',
      'refreshAll',
      'refreshSection',
      'selectAllEvaluations',
      'setDisableControls',
      'setEvaluations',
      'setSelectedEvaluations',
      'setShowTheOmenPoster',
      'showErrorDialog',
      'toggleSelectEvaluation',
      'updateContact',
      'updateNote',
      'updateSelectedEvaluationIds'
    ])
  }
}
</script>

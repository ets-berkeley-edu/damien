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
      const evaluationsEnded = []
      this.$_.each(selectedEvaluations, e => {
        const startDate = this.$moment(e.startDate)
        const evalStateOffset = startDate.diff(e.meetingDates.start, 'days')
        const endDate = (evalStateOffset < 70) ? startDate.add(13, 'day') : startDate.add(20, 'day')
        if (now.isAfter(endDate)) {
          evaluationsEnded.push(e)
        }
      })
      if (evaluationsEnded.length) {
        warningMessage = `You're requesting evaluations with an evaluation period that has already ended, which will result in
          those evaluations <strong>NOT being sent to students</strong>. Please set a new start date for the evaluations listed below:<br>`
        this.$_.each(evaluationsEnded, e => {
          warningMessage += `<br>${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber}`
        })
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

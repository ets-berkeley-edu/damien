<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

const $_isInvalid = (e, evaluationIds) => {
  return _.includes(evaluationIds, e.id) && !(e.departmentForm && e.evaluationType && e.instructor)
}

export default {
  name: 'DepartmentEditSession',
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
      'selectedEvaluationIds'
    ])
  },
  methods: {
    validateConfirmable(evaluationIds) {
      if (this.$_.some(this.evaluations, e => $_isInvalid(e, evaluationIds))) {
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
      'showErrorDialog',
      'toggleSelectEvaluation',
      'updateContact',
      'updateNote',
      'updateSelectedEvaluationIds'
    ])
  }
}
</script>

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
    ...mapActions('departmentEditSession', [
      'addSection',
      'deleteContact',
      'deselectAllEvaluations',
      'dismissErrorDialog',
      'editEvaluation',
      'filterSelectedEvaluations',
      'init',
      'refreshAll',
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

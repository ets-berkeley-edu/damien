<script>
import {mapActions, mapGetters} from 'vuex'

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
      'isSelectedTermLocked',
      'note',
      'selectedEvaluationIds',
      'selectedTerm'
    ])
  },
  methods: {
    validateConfirmable(evaluationIds) {
      if (this.$_.some(this.evaluations, e => this.$_.includes(evaluationIds, e.id) && (!e.departmentForm || !e.evaluationType))) {
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

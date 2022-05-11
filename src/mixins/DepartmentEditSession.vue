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
    validateConfirmable(evaluationIds, departmentFormId, evaluationTypeId) {
      if (this.$_.some(this.evaluations, e => this.$_.includes(evaluationIds, e.id) && (!(departmentFormId && e.departmentForm) || !(evaluationTypeId && e.evaluationType)))) {
        this.showErrorDialog('Cannot confirm evaluations with missing fields.')
        return false
      }
      return true
    },
    ...mapActions('departmentEditSession', [
      'addSection',
      'deleteContact',
      'dismissErrorDialog',
      'editEvaluation',
      'init',
      'refreshAll',
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

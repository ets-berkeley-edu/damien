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
      'note',
      'selectedEvaluationIds',
      'selectedTerm'
    ])
  },
  methods: {
    ...mapActions('departmentEditSession', [
      'addSection',
      'deleteContact',
      'dismissErrorDialog',
      'editEvaluation',
      'init',
      'setDisableControls',
      'showErrorDialog',
      'toggleSelectEvaluation',
      'updateContact',
      'updateNote',
      'updateSelectedEvaluationIds'
    ])
  }
}
</script>

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
      'selectedTerm'
    ])
  },
  methods: {
    ...mapActions('departmentEditSession', [
      'deleteContact',
      'dismissErrorDialog',
      'editEvaluation',
      'init',
      'setDisableControls',
      'showErrorDialog',
      'toggleSelectEvaluation',
      'updateContact',
      'updateNote'
    ])
  }
}
</script>

<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'ListManagementSession',
  computed: {
    ...mapGetters('listManagementSession', [
      'departmentForms',
      'disableControls',
      'evaluationTypes',
      'instructors',
      'isAddingDepartmentForm',
      'isAddingEvaluationType',
      'isAddingInstructor',
      'isConfirming',
      'isSaving',
      'itemToDelete',
      'onDelete'
    ])
  },
  methods: {
    ...mapActions('listManagementSession', [
      'addDepartmentForm',
      'addEvaluationType',
      'addInstructor',
      'confirmDeleteDepartmentForm',
      'confirmDeleteEvaluationType',
      'confirmDeleteInstructor',
      'deleteDepartmentForm',
      'deleteEvaluationType',
      'deleteInstructor',
      'init',
      'reset',
      'setAddingDepartmentForm',
      'setAddingEvaluationType',
      'setAddingInstructor',
      'setDisableControls'
    ])
  }
}
</script>

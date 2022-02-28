<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'ListManagementSession',
  computed: {
    ...mapGetters('listManagementSession', [
      'departmentForms',
      'disableControls',
      'evaluationTypes',
      'isAddingDepartmentForm',
      'isAddingEvaluationType',
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
      'confirmDeleteDepartmentForm',
      'confirmDeleteEvaluationType',
      'deleteDepartmentForm',
      'deleteEvaluationType',
      'init',
      'reset',
      'setAddingDepartmentForm',
      'setAddingEvaluationType'
    ])
  }
}
</script>

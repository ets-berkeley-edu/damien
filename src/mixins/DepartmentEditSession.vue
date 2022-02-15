<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DepartmentEditSession',
  computed: {
    ...mapGetters('departmentEditSession', [
      'contacts',
      'departmentId',
      'disableControls',
      'note',
      'termId'
    ])
  },
  methods: {
    ...mapActions('departmentEditSession', [
      'init',
      'update',
      'updateContact'
    ])
  }
}
</script>

<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DepartmentEditSession',
  computed: {
    ...mapGetters('departmentEditSession', [
      'contacts',
      'departmentId',
      'note'
    ])
  },
  methods: {
    ...mapActions('departmentEditSession', [
      'init'
    ])
  }
}
</script>

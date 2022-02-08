<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DepartmentEditSession',
  computed: {
    ...mapGetters('departmentEditSession', [
      'contacts',
      'departmentId'
    ])
  },
  methods: {
    ...mapActions('departmentEditSession', [
      'init'
    ])
  }
}
</script>

<script>
  import _ from 'lodash'

  export default {
    name: 'Utils',
    methods: {
      stripAnchorRef: path => _.split(path, '#', 1)[0]
    }
  }
</script>

<script>
  import _ from 'lodash'
  import VueScrollTo from 'vue-scrollto'

  export default {
    name: 'Utils',
    computed: {
      primaryHexColor() {
        const theme = this.$vuetify.theme
        return theme.dark ? theme.themes.dark.primary : theme.themes.light.primary
      }
    },
    methods: {
      oxfordJoin: arr => {
        switch(arr.length) {
        case 1: return _.head(arr)
        case 2: return `${_.head(arr)} and ${_.last(arr)}`
        default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
        }
      },
      scrollTo: anchor => VueScrollTo.scrollTo(anchor, 400),
      scrollToTop: delay => VueScrollTo.scrollTo('#app', (delay || 400)),
      stripAnchorRef: path => _.split(path, '#', 1)[0]
    }
  }
</script>

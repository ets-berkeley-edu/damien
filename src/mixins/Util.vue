<script>
  import _ from 'lodash'
  import VueScrollTo from 'vue-scrollto'

  export default {
    name: 'Utils',
    computed: {
      titleHexColor() {
        const theme = this.$vuetify.theme
        return theme.dark ? theme.themes.dark.title : theme.themes.light.title
      }
    },
    methods: {
      getCatalogListings(department) {
        return _.filter(this.$_.keys(department.catalogListings), _.trim)
      },
      oxfordJoin: arr => {
        switch(arr.length) {
        case 1: return _.head(arr)
        case 2: return `${_.head(arr)} and ${_.last(arr)}`
        default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
        }
      },
      pluralize: (noun, count, substitutions = {}, pluralSuffix = 's') => {
        return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
      },
      scrollTo: anchor => VueScrollTo.scrollTo(anchor, 400),
      scrollToTop: delay => VueScrollTo.scrollTo('#app', (delay || 400)),
      stripAnchorRef: path => _.split(path, '#', 1)[0]
    }
  }
</script>

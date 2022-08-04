<script>
import store from '@/store'
import Vue from 'vue'
import {mapActions, mapGetters} from 'vuex'
export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', ['isSelectedTermLocked', 'loading', 'screenReaderAlert', 'selectedTermName', 'serviceAnnouncement', 'snackbar']),
    snackbarShow: {
      get: () => store.getters['context/snackbarShow'],
      set: show => store.dispatch(show ? 'context/snackbarOpen' : 'context/snackbarClose')
    },
    selectedTermId: {
      get: () => store.getters['context/selectedTermId'],
      set: termId => store.dispatch('context/selectTerm', {termId: termId})
    }
  },
  methods: {
    ...mapActions('context', ['setIsSelectedTermLocked', 'snackbarClose', 'selectTerm']),
    alertScreenReader(message) {
      store.dispatch('context/alertScreenReader', '')
      Vue.nextTick(() => store.dispatch('context/alertScreenReader', message))
    },
    reportError: message => store.dispatch('context/snackbarReportError', message),
    snackbarOpen: (text, color) => store.dispatch('context/snackbarOpen', {text, color})
  }
}
</script>
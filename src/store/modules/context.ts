import { getServiceAnnouncement } from '@/api/config'
import Vue from 'vue'

const state = {
  loading: undefined,
  screenReaderAlert: undefined,
  serviceAnnouncement: undefined,
  snackbar: {
    color: 'primary',
    text: undefined,
    timeout: 8000
  },
  snackbarShow: false
}

const getters = {
  loading: (state: any): boolean => state.loading,
  screenReaderAlert: (state: any): string => state.screenReaderAlert,
  serviceAnnouncement: (state: any): string => state.serviceAnnouncement,
  snackbar: (state: any): any => state.snackbar,
  snackbarShow: (state: any): boolean => state.snackbarShow,
}

const mutations = {
  loadingComplete: (state: any, {pageTitle, alert}) => {
    document.title = `${pageTitle || 'UC Berkeley'} | Course Evaluations`
    state.loading = false
    if (alert) {
      state.screenReaderAlert = alert
    } else if (pageTitle) {
      state.screenReaderAlert = `${pageTitle} page is ready`
    }
    Vue.prototype.$putFocusNextTick('page-title')
  },
  loadingStart: (state: any) => (state.loading = true),
  setScreenReaderAlert: (state: any, alert: string) => (state.screenReaderAlert = alert),
  setServiceAnnouncement: (state: any, data: any) => (state.serviceAnnouncement = data),
  snackbarClose: (state: any) => {
    state.snackbarShow = false
    state.snackbar.text = undefined
    state.screenReaderAlert = 'Message closed'
  },
  snackbarOpen: (state: any, text) => {
    state.snackbar.text = text
    state.snackbar.color = 'secondary'
    state.snackbarShow = true
  },
  snackbarReportError: (state: any, text) => {
    state.snackbar.text = text
    state.snackbar.color = 'error'
    state.snackbarShow = true
  }
}

const actions = {
  alertScreenReader: ({ commit }, alert) => commit('setScreenReaderAlert', alert),
  loadingComplete: ({ commit }, {pageTitle, alert}) => commit('loadingComplete', {pageTitle, alert}),
  loadingStart: ({ commit }) => {
    commit('loadingStart')
    getServiceAnnouncement().then(data => {
      commit('setServiceAnnouncement', data)
    })
  },
  snackbarClose: ({ commit }) => commit('snackbarClose'),
  snackbarOpen: ({ commit }, text) => commit('snackbarOpen', text),
  snackbarReportError: ({ commit }, text) => commit('snackbarReportError', text)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
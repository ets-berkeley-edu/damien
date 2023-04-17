import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import linkify from 'vue-linkify'
import moment from 'moment-timezone'
import router from './router'
import store from './store'
import utils from './utils'
import Vue from 'vue'
import vuetify from './plugins/vuetify'

import VCalendar from 'v-calendar'
Vue.use(VCalendar, {componentPrefix: 'c'})

import VueMoment from 'vue-moment'
Vue.use(VueMoment, {moment})

Vue.directive('linkified', linkify)

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL
const isDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'

Vue.prototype.$_ = _
Vue.prototype.$loading = () => store.dispatch('context/loadingStart')
Vue.prototype.$putFocusNextTick = utils.putFocusNextTick
Vue.prototype.$ready = (pageTitle, alert) => store.dispatch('context/loadingComplete', {pageTitle, alert})

// Axios
axios.defaults.withCredentials = true
axios.interceptors.response.use(
  response => response.headers['content-type'] === 'application/json' ? response.data : response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      // Refresh user in case his/her session expired.
      return axios.get(`${apiBaseUrl}/api/user/my_profile`).then(data => {
        Vue.prototype.$currentUser = data
        utils.axiosErrorHandler(error)
        return Promise.reject(error)
      })
    } else {
      const errorUrl = _.get(error, 'response.config.url')
      // 400 and 404 from the section or department evaluations API should be handled by the individual component.
      if (!(errorUrl && (errorUrl.includes('/api/section') || (errorUrl.includes('/api/department') && errorUrl.includes('/evaluations'))))) {
        utils.axiosErrorHandler(error)
      }
      return Promise.reject(error)
    }
  }
)

// Vue config
Vue.config.productionTip = false
Vue.config.errorHandler = function(error, vm, info) {
  console.error(error || info)
  router.push({
    path: '/error',
    query: {
      m: _.get(error, 'message') || info
    }
  })
}

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(data => {
  Vue.prototype.$currentUser = data

  axios.get(`${apiBaseUrl}/api/config`).then(data => {
    Vue.prototype.$config = data
    Vue.prototype.$config.apiBaseUrl = apiBaseUrl
    Vue.prototype.$config.isVueAppDebugMode = isDebugMode

    new Vue({
      router,
      store,
      vuetify,
      render: h => h(App),
    }).$mount('#app')
  })
})

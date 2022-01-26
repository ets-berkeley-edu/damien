import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import router from './router'
import store from './store'
import utils from './utils'
import Vue from 'vue'
import vuetify from './plugins/vuetify'

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL

Vue.prototype.$_ = _
Vue.prototype.$putFocusNextTick = utils.putFocusNextTick

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
      utils.axiosErrorHandler(error)
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

    new Vue({
      router,
      store,
      vuetify,
      render: h => h(App),
    }).$mount('#app')
  })
})
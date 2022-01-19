import axios from 'axios'
import {createApp, nextTick} from 'vue'
import Damien from './Damien.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import _ from 'lodash'

const app = createApp(Damien)
app.use(store)
app.use(router)
app.use(vuetify)

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL

app.config.globalProperties.$_ = _
app.config.globalProperties.$putFocusNextTick = (id: string, cssSelector?: string) => {
  nextTick(() => {
    let counter = 0
    const putFocus = setInterval(() => {
      let el = document.getElementById(id)
      el = el && cssSelector ? el.querySelector(cssSelector) : el
      el && el.focus()
      if (el || ++counter > 5) {
        // Abort after success or three attempts
        clearInterval(putFocus)
      }
    }, 500)
  })
}

// Axios
axios.defaults.withCredentials = true
const axiosErrorHandler = (error: any) => {
  const errorStatus = _.get(error, 'response.status')
  if (_.get(app.config.globalProperties.$currentUser, 'isAuthenticated')) {
    if (errorStatus === 404) {
      router.push({path: '/404'})
    } else if (errorStatus >= 400) {
      const message = _.get(error, 'response.data.message') || error.message
      // eslint-disable-next-line
      console.error(message)
      router.push({
        path: '/error',
        query: {
          m: message
        }
      })
    }
  } else {
    router.push({
      path: '/login',
      query: {
        m: 'Your session has expired'
      }
    })
  }
}
axios.interceptors.response.use(
  response => response.headers['content-type'] === 'application/json' ? response.data : response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      axiosErrorHandler(error)
      return Promise.resolve(error)
    }
  }
)

app.config.errorHandler = function(error, vm, info) {
  // eslint-disable-next-line
  console.error(error || info)
  router.push({
    path: '/error',
    query: {
      m: _.get(error, 'message') || info
    }
  })
}

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(data => {
  app.config.globalProperties.$currentUser = data

  axios.get(`${apiBaseUrl}/api/config`).then(data => {
    app.config.globalProperties.$config = data
    app.config.globalProperties.$config.apiBaseUrl = apiBaseUrl

    app.mount('#app')
  })
})

export default app
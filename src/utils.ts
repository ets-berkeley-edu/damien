import _ from 'lodash'
import router from './router'
import Vue from 'vue'

export default {
  axiosErrorHandler: error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.get(Vue.prototype, '$currentUser.isAuthenticated')) {
      if (errorStatus === 404) {
        router.push({path: '/404'})
      } else if (errorStatus >= 400) {
        const message = _.get(error, 'response.data.message') || error.message
        console.error(message)
        router.push({
          path: '/error',
          query: {
            m: message
          }
        })
      } else if (errorStatus === 400) {
        console.error(error)
      }
    } else {
      router.push({
        path: '/login',
        query: {
          m: 'Your session has expired'
        }
      })
    }
  },
  putFocusNextTick: (id, cssSelector) => {
    const callable = () => {
        let el = document.getElementById(id)
        el = el && cssSelector ? el.querySelector(cssSelector) : el
        el && el.focus()
        return !!el
    }
    Vue.prototype.$nextTick(() => {
      let counter = 0
      const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
    })
  }
}

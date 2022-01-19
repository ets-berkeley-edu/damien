import _ from 'lodash'
import Vue from 'vue'

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'home' ? undefined : to.fullPath
    }
  })
}

export default {
  requiresAuthenticated: (to: any, from: any, next: any) => {
    if (_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
      next()
    } else {
      $_goToLogin(to, next)
    }
  }
}
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
  requiresAdmin: (to: any, from: any, next: any) => {
    if (_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
      if (_.get(Vue.prototype.$currentUser, 'isAdmin')) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresAuthenticated: (to: any, from: any, next: any) => {
    if (_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
      next()
    } else {
      $_goToLogin(to, next)
    }
  }
}

import _ from 'lodash'
import auth from './auth'
import Error from '@/views/Error.vue'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Router from 'vue-router'
import Vue from 'vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        if (_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
          next('/home')
        } else {
          next()
        }
      },
      meta: {
        title: 'Welcome'
      }
    },
    {
      path: '/home',
      component: Home,
      beforeEnter: auth.requiresAuthenticated,
      name: 'home'
    },
    {
      path: '/error',
      component: Error
    }
  ]
})

router.beforeEach((to: any, from: any, next: any) => {
  const redirect = _.trim(to.query.redirect)
  if (Vue.prototype.$currentUser.isAuthenticated && redirect) {
    next(redirect)
  } else {
    next()
  }
})

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | Course Evaluations`
})

export default router
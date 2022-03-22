import _ from 'lodash'
import auth from './auth'
import BaseView from '@/views/BaseView.vue'
import CourseErrors from '@/views/CourseErrors.vue'
import Department from '@/views/Department.vue'
import Error from '@/views/Error.vue'
import Login from '@/views/Login.vue'
import NannysRoom from '@/views/NannysRoom.vue'
import NotFound from '@/views/NotFound.vue'
import StatusBoard from '@/views/StatusBoard.vue'
import TheMonastery from '@/views/TheMonastery.vue'
import Router from 'vue-router'
import Vue from 'vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      beforeEnter: (to: any, from: any, next: any) => {
        if (!_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
          next('/login')
        } if (_.get(Vue.prototype.$currentUser, 'isAdmin')) {
          next('/status')
        } else if (_.get(Vue.prototype.$currentUser, 'departments[0]')) {
          next(`/department/${Vue.prototype.$currentUser.departments[0]}`)
        } else {
          //TODO: where to send a non-admin user who doesn't belong to a department?
          next()
        }
      }
    },
    {
      path: '/login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        if (_.get(Vue.prototype.$currentUser, 'isAuthenticated')) {
          next('/')
        } else {
          next()
        }
      },
      meta: {
        title: 'Welcome'
      }
    },
    {
      path: '/',
      component: BaseView,
      beforeEnter: auth.requiresAuthenticated,
      children: [
        {
          path: '/department/:departmentId',
          component: Department,
          meta: {
            title: 'Department'
          }
        },
        {
          path: '/departments',
          component: TheMonastery,
          meta: {
            title: 'Group Management'
          }
        },
        {
          path: '/errors',
          component: CourseErrors,
          meta: {
            title: 'Course Errors Board'
          }
        },
        {
          path: '/lists',
          component: NannysRoom,
          meta: {
            title: 'List Management'
          }
        },
        {
          path: '/status',
          component: StatusBoard,
          beforeEnter: auth.requiresAdmin,
          meta: {
            title: 'Status Board'
          }
        },
      ]
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          path: '/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        },
        {
          path: '/error',
          component: Error,
          meta: {
            title: 'Error'
          }
        },
        {
          path: '*',
          redirect: '/404'
        }
      ]
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
import _ from 'lodash'
import auth from './auth'
import BaseView from '@/views/BaseView.vue'
import Department from '@/views/Department.vue'
import Error from '@/views/Error.vue'
import Login from '@/views/Login.vue'
import Megiddo from '@/views/Megiddo.vue'
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
      redirect: '/home'
    },
    {
      path: '/login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        const currentUser = Vue.prototype.$currentUser
        if (_.get(currentUser, 'isAuthenticated')) {
          if (_.trim(to.query.redirect)) {
            next(to.query.redirect)
          } else {
            next('/home')
          }
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
          beforeEnter: (to: any, from: any, next: any) => {
            const currentUser = Vue.prototype.$currentUser
            if (currentUser.isAdmin) {
              next('/status')
            } else if (_.size(currentUser.departments)) {
              next(`/department/${currentUser.departments[0].id}`)
            } else {
              next({
                path: '/error',
                query: {
                  m: 'Sorry, we could not find any departments that you belong to.'
                }
              })
            }
          },
          path: '/home',
          name: 'home'
        },
        {
          path: '/department/:departmentId',
          component: Department,
          beforeEnter: auth.requiresDepartmentMembership,
          meta: {
            title: 'Department'
          }
        }
      ]
        },
    {
      path: '/',
      component: BaseView,
      beforeEnter: auth.requiresAdmin,
      children: [
        {
          path: '/departments',
          component: TheMonastery,
          meta: {
            title: 'Group Management'
          }
        },
        {
          path: '/publish',
            component: Megiddo,
          meta: {
            title: 'Publish'
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
          meta: {
            title: 'Status Board'
          }
        }
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
  if (_.get(Vue.prototype.$currentUser, 'isAuthenticated') && redirect) {
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

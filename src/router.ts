import _ from 'lodash'
import app from '@/main'
import auth from './auth'
import Error from '@/views/Error.vue'
import Home from '@/views/Home.vue'
import Login from '@/layouts/Login.vue'
import {createRouter, createWebHistory} from 'vue-router'

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        if (_.get(app.config.globalProperties.$currentUser, 'isAuthenticated')) {
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

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | Course Evaluations`
})

export default router
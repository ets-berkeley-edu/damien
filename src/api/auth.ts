import app from '@/main'
import axios from 'axios'

export function devAuthLogIn(password: string, userId: string) {
  return axios
      .post(`${app.config.globalProperties.$config.apiBaseUrl()}/api/auth/dev_auth_login`, {password, userId})
        .then(data => {
          app.config.globalProperties.$currentUser = data
          return app.config.globalProperties.$currentUser
        }).catch(error => {
          return error
        })
}
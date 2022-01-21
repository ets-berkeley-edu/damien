import axios from 'axios'
import Vue from 'vue'

export function devAuthLogIn(uid: string, password: string) {
  return axios
      .post(`${Vue.prototype.$config.apiBaseUrl}/api/auth/dev_auth_login`, {uid, password})
        .then(data => {
          Vue.prototype.$currentUser = data
          return Vue.prototype.$currentUser
        }).catch(error => {
          return error
        })
}
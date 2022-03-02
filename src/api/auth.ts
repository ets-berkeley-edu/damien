import axios from 'axios'
import Vue from 'vue'

export function devAuthLogIn(uid: string, password: string) {
  return axios
      .post(`${Vue.prototype.$config.apiBaseUrl}/api/auth/dev_auth_login`, {uid, password})
        .then(data => {
          Vue.prototype.$currentUser = data
          return Vue.prototype.$currentUser
        }, error => error)
}

export function getCasLoginURL() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/auth/cas_login_url`)
}

export function getCasLogoutUrl() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/auth/logout`)
}
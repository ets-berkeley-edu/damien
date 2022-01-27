import axios from 'axios'
import Vue from 'vue'

export function getDepartmentsEnrolled() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/departments/enrolled`)
}

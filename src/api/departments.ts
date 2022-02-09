import axios from 'axios'
import Vue from 'vue'

export function getDepartment(departmentId, termId) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}?term_id=${termId}`)
}

export function getDepartmentsEnrolled() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/departments/enrolled`)
}

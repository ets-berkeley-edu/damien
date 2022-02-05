import axios from 'axios'
import Vue from 'vue'

export function getDepartment(departmentId) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}`)
}

export function getDepartmentsEnrolled() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/departments/enrolled`)
}

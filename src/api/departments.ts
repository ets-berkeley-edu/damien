import axios from 'axios'
import Vue from 'vue'

export function getDepartment(departmentId, termId) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}?term_id=${termId}`)
}

export function getDepartmentsEnrolled() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/departments/enrolled`)
}

export function updateDepartment(departmentId: number, note: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}`, {note}).then(response => response.data, () => null)
}

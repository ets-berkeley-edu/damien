import axios from 'axios'
import Vue from 'vue'

export function deleteDepartmentForm(name: string) {
  return axios.delete(`${Vue.prototype.$config.apiBaseUrl}/api/department_form/${name}`)
}

export function getDepartmentForms() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department_forms`)
}

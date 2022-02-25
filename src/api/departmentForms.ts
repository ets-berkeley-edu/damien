import axios from 'axios'
import Vue from 'vue'

export function deleteDepartmentForm(id: number) {
  console.log(`TODO: delete ${id}`)
  return new Promise<void>(resolve => resolve)
}

export function getDepartmentForms() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department_forms`)
}

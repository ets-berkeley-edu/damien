import axios from 'axios'
import Vue from 'vue'

export function getDepartmentForms() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department_forms`)
}

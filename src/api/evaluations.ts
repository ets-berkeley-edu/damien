import axios from 'axios'
import Vue from 'vue'

export function getValidation() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/validate`)
}

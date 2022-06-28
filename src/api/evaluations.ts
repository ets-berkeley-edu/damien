import axios from 'axios'
import Vue from 'vue'

export function exportEvaluations() {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/export`)
}

export function getExports(termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/exports?term_id=${termId}`)
}

export function getValidation() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/validate`)
}

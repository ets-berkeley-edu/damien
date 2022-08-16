import axios from 'axios'
import Vue from 'vue'

export function exportEvaluations(termId: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/export?term_id=${termId}`)
}

export function getConfirmed(termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/confirmed?term_id=${termId}`)
}

export function getExportStatus() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/export/status`)
}

export function getExports(termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/exports?term_id=${termId}`)
}

export function getValidation(termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluations/validate?term_id=${termId}`)
}

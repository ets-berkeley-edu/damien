import axios from 'axios'
import Vue from 'vue'

export function getEvaluationTerm(termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_term/${termId}`)
}

export function lockEvaluationTerm(termId: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_term/lock`, {termId})
    .then(response => response)
}

export function unlockEvaluationTerm(termId: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_term/unlock`, {termId})
    .then(response => response)
}
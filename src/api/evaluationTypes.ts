import axios from 'axios'
import Vue from 'vue'

export function addEvaluationType(name) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_type/${name}`)
}

export function deleteEvaluationType(name) {
  return axios.delete(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_type/${name}`)
}

export function getEvaluationTypes() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_types`)
}

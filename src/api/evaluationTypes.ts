import axios from 'axios'
import Vue from 'vue'

export function getEvaluationTypes() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_types`)
}

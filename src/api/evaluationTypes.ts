import axios from 'axios'
import Vue from 'vue'

export function deleteEvaluationType(id: number) {
  console.log(`TODO: delete ${id}`)
  return new Promise<void>(resolve => resolve)
}

export function getEvaluationTypes() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/evaluation_types`)
}

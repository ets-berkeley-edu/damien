import axios from 'axios'
import Vue from 'vue'

export function getSection(courseNumber: string, termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/section/${courseNumber}?term_id=${termId}`)
}

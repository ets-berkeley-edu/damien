import axios from 'axios'
import Vue from 'vue'

export function addInstructor(instructor) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/instructor`, instructor).then(response => response, () => null)
}

export function deleteInstructor(uid) {
  return axios.delete(`${Vue.prototype.$config.apiBaseUrl}/api/instructor/${uid}`)
}

export function getInstructors() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/instructors`)
}

export function searchInstructors(snippet: string, excludeUids: string[]) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/instructor/search`, {snippet, excludeUids}).then(response => response, () => null)
}

import axios from 'axios'
import Vue from 'vue'

export function searchInstructors(snippet: string, excludeUids: string[]) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/user/search_instructors`, {snippet, excludeUids}).then(response => response, () => null)
}

export function searchUsers(snippet: string, excludeUids: string[]) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/user/search`, {snippet, excludeUids}).then(response => response, () => null)
}
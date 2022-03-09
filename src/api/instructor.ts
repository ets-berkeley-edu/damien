import axios from 'axios'
import Vue from 'vue'

export function searchInstructors(snippet: string, excludeUids: string[]) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/instructor/search`, {snippet, excludeUids}).then(response => response, () => null)
}

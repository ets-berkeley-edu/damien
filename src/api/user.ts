import axios from 'axios'
import Vue from 'vue'

export function searchUsers(snippet: string, excludeUids: string[]) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/user/search`, {snippet, excludeUids}).then(response => response, () => null)
}
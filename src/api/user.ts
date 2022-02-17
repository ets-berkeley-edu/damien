import axios from 'axios'
import Vue from 'vue'

export function searchUsers(snippet: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/user/search`, {snippet}).then(response => response, () => null)
}
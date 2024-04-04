import axios from 'axios'
import store from '../store'
import Vue from 'vue'

export function getAutoPublishStatus() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/auto_publish`)
}

export function setAutoPublishStatus(enabled) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/auto_publish/update`, {enabled})
}

export function getServiceAnnouncement() {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/service_announcement`)
}

export function updateServiceAnnouncement(text, isLive) {
  return axios
    .post(`${Vue.prototype.$config.apiBaseUrl}/api/service_announcement/update`, {text, isLive})
    .then(response => {
      store.commit('context/setServiceAnnouncement', response)
      return response
    })
    .catch(error => error)
}

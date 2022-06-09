import axios from 'axios'
import Vue from 'vue'

export function addSection(departmentId: number, courseNumber: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/section`, {courseNumber}).then(response => response.data, () => null)
}

export function deleteContact(departmentId: number, userId: number) {
  return axios.delete(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/contact/${userId}`)
}

export function getDepartment(departmentId: number, termId: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}?term_id=${termId}`)
}

export function getDepartmentsEnrolled(includeContacts: boolean, includeSections: boolean, includeStatus: boolean) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/departments/enrolled?c=${includeContacts ? 1 : 0}&s=${includeSections ? 1 : 0}&t=${includeStatus ? 1 : 0}`)
}

export function getSectionEvaluations(departmentId: number, courseNumber: string) {
  return axios.get(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/section_evaluations/${courseNumber}`)
}

export function notifyContacts(message: string, recipient: string[], subject: string) {
  return axios
    .post(`${Vue.prototype.$config.apiBaseUrl}/api/department/contacts/notify`, {message, recipient, subject})
    .then(response => response)
    .catch(() => null)
}

export function updateContact(departmentId: number, contact: any) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/contact`, contact).then(response => response.data, () => null)
}

export function updateDepartmentNote(departmentId: number, note: string, termId?: string) {
  return axios.post(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/note`, {termId, note}).then(response => response.data, () => null)
}

export function updateEvaluations(departmentId: number, action: string, evaluationIds: any[], fields?: Object) {
  return axios
    .post(`${Vue.prototype.$config.apiBaseUrl}/api/department/${departmentId}/evaluations`, {action, evaluationIds, fields})
    .then(response => response)
}

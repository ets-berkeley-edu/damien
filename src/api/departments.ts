import axios from 'axios'
import {getApiBaseUrl} from '@/api/api-utils'

export function addSection(departmentId: number, courseNumber: string, termId: string) {
  return axios.post(`${getApiBaseUrl()}/api/department/${departmentId}/section?term_id=${termId}`, {courseNumber})
    .then(response => response.data, () => null)
}

export function deleteContact(departmentId: number, userId: number) {
  return axios.delete(`${getApiBaseUrl()}/api/department/${departmentId}/contact/${userId}`)
}

export function getDepartment(departmentId: number, termId: string) {
  return axios.get(`${getApiBaseUrl()}/api/department/${departmentId}?term_id=${termId}`)
    .then(response => response.data)
}

export function getDepartmentsEnrolled(
  includeContacts: boolean,
  includeSections: boolean,
  includeStatus: boolean,
  termId: string
) {
  let url = `${getApiBaseUrl()}/api/departments/enrolled?c=${includeContacts ? 1 : 0}&s=${includeSections ? 1 : 0}&t=${includeStatus ? 1 : 0}`
  if (termId) {
    url = url + `&term_id=${termId}`
  }
  return axios.get(url).then(response => response.data)
}

export function getSectionEvaluations(departmentId: number, courseNumber: string, termId: string) {
  return axios.get(`${getApiBaseUrl()}/api/department/${departmentId}/section_evaluations/${courseNumber}?term_id=${termId}`)
    .then(response => response.data)
}

export function notifyContacts(message: string, recipient: string[], subject: string) {
  return axios.post(`${getApiBaseUrl()}/api/department/contacts/notify`, {message, recipient, subject})
    .then(response => response.data)
    .catch(() => null)
}

export function updateContact(departmentId: number, contact: any) {
  return axios.post(`${getApiBaseUrl()}/api/department/${departmentId}/contact`, contact)
    .then(response => response.data, () => null)
}

export function updateDepartmentNote(departmentId: number, note: string, termId?: string) {
  return axios.post(`${getApiBaseUrl()}/api/department/${departmentId}/note`, {termId, note})
    .then(response => response.data, () => null)
}

export function updateEvaluations(departmentId: number, action: string, evaluationIds: any[], termId: string, fields?: object) {
  const data = {action, evaluationIds, fields}
  return axios.post(`${getApiBaseUrl()}/api/department/${departmentId}/evaluations?term_id=${termId}`, data)
    .then(response => response.data)
}

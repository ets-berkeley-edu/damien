import {getDepartment} from '@/api/departments'

const $_refresh = (commit, departmentId, termId) => {
  return new Promise<void>(resolve => {
    getDepartment(departmentId, termId).then((dept: any) => {
      commit('reset', dept, termId)
      return resolve(dept)
    })
  })
}

const state = {
  contacts: [],
  departmentId: undefined,
  note: undefined
}

const getters = {
  contacts: (state: any): any[] => state.contacts,
  departmentId: (state: any): number => state.departmentId,
  note: (state: any): string => state.note,
  termId: (state: any): string => state.termId
}

const actions = {
  init: ({commit}, {departmentId, termId}) => new Promise<void>(resolve => $_refresh(commit, departmentId, termId).then(dept => resolve(dept)))
}

const mutations = {
  reset: (state: any, {department, termId}) => {
    if (department) {
      state.contacts = department.contacts
      state.departmentId = department.id
      state.note = department.note
    }
    state.termId = termId
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
import {getDepartment} from '@/api/departments'
import Vue from 'vue'

const $_refresh = (commit, departmentId) => {
  return new Promise<void>(resolve => {
    getDepartment(departmentId, Vue.prototype.$config.currentTermId).then((dept: any) => {
      commit('reset', dept)
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
  note: (state: any): string => state.note
}

const actions = {
  init: ({commit}, departmentId: number) => new Promise<void>(resolve => $_refresh(commit, departmentId).then(dept => resolve(dept)))
}

const mutations = {
  reset: (state: any, department: any) => {
    if (department) {
      state.contacts = department.contacts
      state.departmentId = department.id
      state.note = department.note
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
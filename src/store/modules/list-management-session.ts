import {addDepartmentForm, deleteDepartmentForm, getDepartmentForms} from '@/api/departmentForms'
import {addEvaluationType, deleteEvaluationType, getEvaluationTypes} from '@/api/evaluationTypes'
import store from '@/store'

const $_refreshAll = (commit) => {
  return Promise.all([getDepartmentForms(), getEvaluationTypes()]).then(response => {
    commit('setDepartmentForms', response[0])
    commit('setEvaluationTypes', response[1])
  })
}

const $_refreshDepartmentForms = (commit) => {
  return getDepartmentForms().then((departmentForms: any) => {
    commit('setDepartmentForms', departmentForms)
  })
}

const $_refreshEvaluationTypes = (commit) => {
  return getEvaluationTypes().then((evaluationTypes: any) => {
    commit('setEvaluationTypes', evaluationTypes)
  })
}

const state = {
  departmentForms: [],
  disableControls: false,
  evaluationTypes: [],
  isAddingDepartmentForm: false,
  isAddingEvaluationType: false,
  isConfirming: false,
  isSaving: false,
  itemToDelete: undefined,
  onDelete: () => {}
}

const getters = {
  departmentForms: (state: any): any[] => state.departmentForms,
  disableControls: (state: any): number => state.disableControls,
  evaluationTypes: (state: any): any[] => state.evaluationTypes,
  isAddingDepartmentForm: (state: any): boolean => state.isAddingDepartmentForm,
  isAddingEvaluationType: (state: any): boolean => state.isAddingEvaluationType,
  isConfirming: (state: any): boolean => state.isConfirming,
  isSaving: (state: any): boolean => state.isSaving,
  itemToDelete: (state: any): any => state.itemToDelete,
  onDelete: (state: any): Function => state.onDelete,
}

const actions = {
  addDepartmentForm: ({commit}, name: string) => {
    commit('setIsSaving', true)
    commit('setDisableControls', true)
    return addDepartmentForm(name).then(() => {
      $_refreshDepartmentForms(commit)
    }).finally(() => commit('reset'))
  },
  addEvaluationType: ({commit}, name: string) => {
    commit('setIsSaving', true)
    commit('setDisableControls', true)
    return addEvaluationType(name).then(() => {
      $_refreshEvaluationTypes(commit)
    }).finally(() => commit('reset'))
  },
  confirmDeleteDepartmentForm: ({commit}, itemToDelete: any) => {
    commit('setIsConfirming', true)
    commit('setItemToDelete', {
      ...itemToDelete,
      description: 'department form',
      elementId: `delete-dept-form-${itemToDelete.id}-btn`
    })
    commit('setOnDelete', () => store.dispatch('listManagementSession/deleteDepartmentForm'))
  },
  confirmDeleteEvaluationType: ({commit}, itemToDelete: any) => {
    commit('setIsConfirming', true)
    commit('setItemToDelete', {
      ...itemToDelete,
      description: 'evaluation type',
      elementId: `delete-eval-type-${itemToDelete.id}-btn`
    })
    commit('setOnDelete', () => store.dispatch('listManagementSession/deleteEvaluationType'))
  },
  deleteDepartmentForm: ({commit, state}) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      return deleteDepartmentForm(state.itemToDelete.name).then(() => {
        $_refreshDepartmentForms(commit)
        resolve(state.itemToDelete)
      }).finally(() => commit('reset'))
    })
  },
  deleteEvaluationType: ({commit, state}) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      return deleteEvaluationType(state.itemToDelete.name).then(() => {
        $_refreshEvaluationTypes(commit)
        resolve(state.itemToDelete)
      }).finally(() => commit('reset'))
    })
  },
  init: ({commit}) => {
    return $_refreshAll(commit)
  },
  reset: ({commit}) => commit('reset'),
  setAddingDepartmentForm: ({commit}) => {
    return new Promise<void>(resolve => {
      commit('reset')
      commit('setAddingDepartmentForm')
      resolve()
    })
  },
  setAddingEvaluationType: ({commit}) => {
    return new Promise<void>(resolve => {
      commit('reset')
      commit('setAddingEvaluationType')
      resolve()
    })
  }
}

const mutations = {
  reset: (state: any) => {
    state.disableControls = false
    state.isAddingDepartmentForm = false
    state.isAddingEvaluationType = false
    state.isConfirming = false
    state.isSaving = false
    state.itemToDelete = undefined
    state.onDelete = () => {}
  },
  setAddingDepartmentForm: (state: any) => state.isAddingDepartmentForm = true,
  setAddingEvaluationType: (state: any) => state.isAddingEvaluationType = true,
  setDepartmentForms: (state: any, departmentForms: any[]) => state.departmentForms = departmentForms,
  setDisableControls: (state: any, disable: boolean) => state.disableControls = disable,
  setEvaluationTypes: (state: any, evaluationTypes: any[]) => state.evaluationTypes = evaluationTypes,
  setIsConfirming: (state: any, isConfirming: boolean) => state.isConfirming = isConfirming,
  setIsSaving: (state: any, isSaving: boolean) => state.isSaving = isSaving,
  setItemToDelete: (state: any, item: any) => state.itemToDelete = item,
  setOnDelete: (state: any, onDelete: Function) => state.onDelete = onDelete,
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
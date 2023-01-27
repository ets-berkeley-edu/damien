import {addDepartmentForm, deleteDepartmentForm, getDepartmentForms} from '@/api/departmentForms'
import {addEvaluationType, deleteEvaluationType, getEvaluationTypes} from '@/api/evaluationTypes'
import {addInstructor, deleteInstructor, getInstructors} from '@/api/instructor'
import store from '@/store'
import Vue from 'vue'

const $_refreshAll = (commit) => {
  return Promise.all([getDepartmentForms(), getEvaluationTypes(), getInstructors()]).then(response => {
    Vue.prototype.$config.departmentForms = response[0]
    Vue.prototype.$config.evaluationTypes = response[1]
    commit('setDepartmentForms', response[0])
    commit('setEvaluationTypes', response[1])
    commit('setInstructors', response[2])
  })
}

const $_refreshDepartmentForms = (commit) => {
  return getDepartmentForms().then((departmentForms: any) => {
    Vue.prototype.$config.departmentForms = departmentForms
    commit('setDepartmentForms', departmentForms)
  })
}

const $_refreshEvaluationTypes = (commit) => {
  return getEvaluationTypes().then((evaluationTypes: any) => {
    Vue.prototype.$config.evaluationTypes = evaluationTypes
    commit('setEvaluationTypes', evaluationTypes)
  })
}

const $_refreshInstructors = (commit) => {
  return getInstructors().then((instructors: any) => {
    commit('setInstructors', instructors)
  })
}

const state = {
  departmentForms: [],
  disableControls: false,
  evaluationTypes: [],
  instructors: [],
  isAddingDepartmentForm: false,
  isAddingEvaluationType: false,
  isAddingInstructor: false,
  isConfirming: false,
  isSaving: false,
  itemToDelete: undefined,
  onDelete: () => {}
}

const getters = {
  departmentForms: (state: any): any[] => state.departmentForms,
  disableControls: (state: any): number => state.disableControls,
  evaluationTypes: (state: any): any[] => state.evaluationTypes,
  instructors: (state: any): any[] => state.instructors,
  isAddingDepartmentForm: (state: any): boolean => state.isAddingDepartmentForm,
  isAddingEvaluationType: (state: any): boolean => state.isAddingEvaluationType,
  isAddingInstructor: (state: any): boolean => state.isAddingInstructor,
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
  addInstructor: ({commit}, name: string) => {
    commit('setIsSaving', true)
    commit('setDisableControls', true)
    return addInstructor(name).then(() => {
      $_refreshInstructors(commit)
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
  confirmDeleteInstructor: ({commit}, itemToDelete: any) => {
    commit('setIsConfirming', true)
    commit('setItemToDelete', {
      ...itemToDelete,
      name: `${itemToDelete.firstName} ${itemToDelete.lastName} (${itemToDelete.uid})`,
      description: 'instructor',
      elementId: `delete-instructor-${itemToDelete.uid}-btn`
    })
    commit('setOnDelete', () => store.dispatch('listManagementSession/deleteInstructor'))
  },
  deleteDepartmentForm: ({commit, state}) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      return deleteDepartmentForm(state.itemToDelete.name).then(() => {
        $_refreshDepartmentForms(commit)
        resolve(state.itemToDelete)
      }).finally(() => {
        commit('reset')
        Vue.prototype.$putFocusNextTick('department-forms-card-title')
      })
    })
  },
  deleteEvaluationType: ({commit, state}) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      return deleteEvaluationType(state.itemToDelete.name).then(() => {
        $_refreshEvaluationTypes(commit)
        resolve(state.itemToDelete)
      }).finally(() => {
        commit('reset')
        Vue.prototype.$putFocusNextTick('evaluation-types-card-title')
      })
    })
  },
  deleteInstructor: ({commit, state}) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      return deleteInstructor(state.itemToDelete.uid).then(() => {
        $_refreshInstructors(commit)
        resolve(state.itemToDelete)
      }).finally(() => {
        commit('reset')
        Vue.prototype.$putFocusNextTick('manually-added-instructors-title')
      })
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
  },
  setAddingInstructor: ({commit}) => {
    return new Promise<void>(resolve => {
      commit('reset')
      commit('setAddingInstructor')
      resolve()
    })
  },
  setDisableControls: ({commit}, disable: boolean) => commit('setDisableControls', disable),
}

const mutations = {
  reset: (state: any) => {
    state.disableControls = false
    state.isAddingDepartmentForm = false
    state.isAddingEvaluationType = false
    state.isAddingInstructor = false
    state.isConfirming = false
    state.isSaving = false
    state.itemToDelete = undefined
    state.onDelete = () => {}
  },
  setAddingDepartmentForm: (state: any) => state.isAddingDepartmentForm = true,
  setAddingEvaluationType: (state: any) => state.isAddingEvaluationType = true,
  setAddingInstructor: (state: any) => state.isAddingInstructor = true,
  setDepartmentForms: (state: any, departmentForms: any[]) => state.departmentForms = departmentForms,
  setDisableControls: (state: any, disable: boolean) => state.disableControls = disable,
  setEvaluationTypes: (state: any, evaluationTypes: any[]) => state.evaluationTypes = evaluationTypes,
  setInstructors: (state: any, instructors: any[]) => state.instructors = instructors,
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

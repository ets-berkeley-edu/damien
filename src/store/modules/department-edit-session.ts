import _ from 'lodash'
import {
  addSection,
  deleteContact,
  getDepartment,
  getSectionEvaluations,
  updateContact,
  updateDepartmentNote,
  updateEvaluations
} from '@/api/departments'
import {getDepartmentForms} from '@/api/departmentForms'
import Vue from 'vue'

const $_decorateEvaluation = e => {
  e.isSelected = false
  // When sorting by course number, keep cross-listings with home sections.
  if (e.crossListedWith && e.foreignDepartmentCourse) {
    e.sortableCourseNumber = `${e.crossListedWith}-${e.courseNumber}`
  } else if (e.roomSharedWith && e.foreignDepartmentCourse) {
    e.sortableCourseNumber = `${e.roomSharedWith}-${e.courseNumber}`
  } else {
    e.sortableCourseNumber = e.courseNumber
  }
  e.sortableCourseName = `${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber} ${e.courseTitle}`
  if (e.instructor) {
    e.sortableInstructor = `${e.instructor.lastName} ${e.instructor.firstName} ${e.instructor.uid} ${e.instructor.emailAddress}`
  } else {
    e.sortableInstructor = ''
  }
  e.startDate = Vue.prototype.$moment(e.startDate).toDate()
  e.endDate = Vue.prototype.$moment(e.endDate).toDate()
  e.meetingDates.start = Vue.prototype.$moment(e.meetingDates.start).toDate()
  e.meetingDates.end = Vue.prototype.$moment(e.meetingDates.end).toDate()
}

const $_getDepartmentForms = async function(commit) {
  getDepartmentForms().then((departmentForms: any) => {
    commit('setAllDepartmentForms', departmentForms)
  })
}

const $_refresh = (commit, {departmentId, termId}) => {
  return new Promise<void>(resolve => {
    getDepartment(departmentId, termId).then((department: any) => {
      commit('reset', {department, termId})
      return resolve(department)
    })
  })
}

const state = {
  allDepartmentForms: [],
  contacts: [],
  department: undefined,
  disableControls: false,
  errorDialog: false,
  errorDialogText: null,
  evaluations: [],
  isSelectedTermLocked: false,
  note: undefined,
  selectedEvaluationIds: [],
  selectedTerm: undefined
}

const getters = {
  allDepartmentForms: (state: any): any[] => state.allDepartmentForms,
  contacts: (state: any): any[] => state.contacts,
  department: (state: any): number => state.department,
  disableControls: (state: any): boolean => state.disableControls,
  errorDialog: (state: any): boolean => state.errorDialog,
  errorDialogText: (state: any): boolean => state.errorDialogText,
  evaluations: (state: any): any[] => state.evaluations,
  isSelectedTermLocked: (state: any): boolean => state.isSelectedTermLocked,
  note: (state: any): string => state.note,
  selectedEvaluationIds: (state: any): any[] => state.selectedEvaluationIds,
  selectedTerm: (state: any): any => state.selectedTerm
}

const actions = {
  addSection: ({commit, state}, sectionId: string) => {
    commit('setDisableControls', true)
    return new Promise((resolve: Function, reject) => {
      addSection(state.department.id, sectionId)
      .then(() => {
        getSectionEvaluations(state.department.id, sectionId).then((data: any) => {
          const updatedEvaluations = _.each(data, $_decorateEvaluation)
          commit('setEvaluationUpdate', {sectionIndex: 0, sectionCount: 0, updatedEvaluations})
          resolve()
        })
      })
      .catch(error => reject(error))
    })
  },
  deleteContact: ({commit, state}, userId: number) => {
    commit('setDisableControls', true)
    return deleteContact(state.department.id, userId).then(() => {
      $_refresh(commit, {departmentId: state.department.id, termId: state.selectedTerm.id})
    })
  },
  dismissErrorDialog: ({commit}) => {
    commit('setErrorDialog', false)
    commit('setErrorDialogText', null)
  },
  editEvaluation: ({commit, state}, {evaluationId, sectionId, fields}) => {
    commit('setDisableControls', true)
    return new Promise((resolve: Function, reject) => {
      updateEvaluations(state.department.id, 'edit', [evaluationId], fields)
      .then(() => {
        getSectionEvaluations(state.department.id, sectionId).then((data: any) => {
          let sectionIndex = _.findIndex(state.evaluations, ['courseNumber', sectionId])
          if (sectionIndex === -1) {
            sectionIndex = state.evaluations.length
          }
          const sectionCount = _.filter(state.evaluations, ['courseNumber', sectionId]).length
          const updatedEvaluations = _.each(data, $_decorateEvaluation)
          commit('setEvaluationUpdate', {sectionIndex, sectionCount, updatedEvaluations})
          resolve()
        })
      })
      .catch(error => reject(error))
      .finally(() => commit('setDisableControls', false))
    })
  },
  init: ({commit}, {departmentId: departmentId, termId: termId}) => {
    $_getDepartmentForms(commit)
    return new Promise<void>(resolve => {
      $_refresh(commit, {departmentId, termId})
        .then(commit('updateSelectedEvaluationIds'))
        .then(department => resolve(department))
    })
  },
  refreshAll: ({commit, state}) => {
    return new Promise<void>(resolve => {
      $_refresh(commit, {departmentId: state.department.id, termId: state.selectedTerm.id}).then(dept => resolve(dept))
    })
  },
  setEvaluations: ({commit}, evaluations: any[]) => {
    commit('setEvaluations', evaluations)
  },
  setDisableControls: ({commit}, disable: boolean) => {
    commit('setDisableControls', disable)
  },
  showErrorDialog: ({commit}, text: string) => {
    commit('setErrorDialog', true)
    commit('setErrorDialogText', text)
  },
  toggleSelectEvaluation: ({commit}, evaluationId: any) => {
    commit('setIsSelected', evaluationId)
  },
  updateContact: ({commit, state}, contact: any) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      updateContact(state.department.id, contact).then(() => {
        $_refresh(commit, {departmentId: state.department.id, termId: state.selectedTerm.id}).then(dept => resolve(dept))
      })
    })
  },
  updateNote: ({commit, state}, note: string) => {
    commit('setDisableControls', true)
    return new Promise<void>(resolve => {
      updateDepartmentNote(state.department.id, note, state.selectedTerm.id).then(() => {
        $_refresh(commit, {departmentId: state.department.id, termId: state.selectedTerm.id}).then(dept => resolve(dept))
      })
    })
  },
  updateSelectedEvaluationIds: ({commit}) => {
    commit('updateSelectedEvaluationIds')
  }
}

const mutations = {
  reset: (state, {department, termId}) => {
    if (department) {
      state.contacts = department.contacts
      state.department = department
      _.each(department.evaluations, $_decorateEvaluation)
      state.evaluations = _.sortBy(department.evaluations, 'sortableCourseNumber')
      state.isSelectedTermLocked = true === _.get(department, 'evaluationTerm.isLocked')
      state.note = _.get(department.notes, [termId, 'note'])
    }
    state.selectedEvaluationIds = []
    state.selectedTerm = _.find(Vue.prototype.$config.availableTerms, {'id': termId})
    state.disableControls = false
  },
  setAllDepartmentForms: (state: any, departmentForms: any[]) => state.allDepartmentForms = departmentForms,
  setDisableControls: (state: any, disable: boolean) => state.disableControls = disable,
  setErrorDialog: (state: any, errorDialog: boolean) => state.errorDialog = errorDialog,
  setErrorDialogText: (state: any, errorDialogText: string) => state.errorDialogText = errorDialogText,
  setEvaluations: (state: any, evaluations: any[]) => state.evaluations = evaluations,
  setEvaluationUpdate: (state: any, {sectionIndex, sectionCount, updatedEvaluations}) => {
    const evaluations = _.sortBy(updatedEvaluations, 'sortableCourseNumber')
    state.evaluations.splice(sectionIndex, sectionCount, ...evaluations)
  },
  setIsSelected: (state: any, evaluationId: any) => {
    const evaluation = _.find(state.evaluations, {'id': evaluationId})
    if (evaluation) {
      evaluation.isSelected = !evaluation.isSelected
    }
  },
  updateSelectedEvaluationIds: (state: any) => {
    state.selectedEvaluationIds = _.reduce(state.evaluations, (ids, e) => {
      if (e.isSelected) {
        ids.push(e.id)
      }
      return ids
    }, [])
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
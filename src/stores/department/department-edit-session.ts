import {DateTime} from 'luxon'
import {defineStore} from 'pinia'
import {
  each,
  filter,
  find,
  findIndex,
  get,
  includes,
  indexOf,
  intersectionWith,
  isUndefined,
  reduce,
  reject,
  some,
  sortBy,
  toString
} from 'lodash'
import {
  addSection,
  deleteContact,
  getDepartment,
  getSectionEvaluations,
  updateContact,
  updateDepartmentNote,
  updateEvaluations
} from '@/api/departments'
import {alertScreenReader} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

export const EVALUATION_STATUSES = [
  {text: 'None', value: 'none'},
  {text: 'To-do', value: 'review'},
  {text: 'Done', value: 'confirmed'},
  {text: 'Ignore', value: 'ignore'}
]

export const NUMBER_OF_THE_BEAST = '666'

export type Department = {
  id: number,
  evaluations: any[]
}

export type DepartmentForm = {
  id: number,
  name: string,
  createdAt: string,
  updatedAt: string,
  deletedAt: string,
}

const $_decorateEvaluation = (e: any, allEvaluations: any[]) => {
  e.isSelected = false
  e.searchableCourseName = [
    e.subjectArea,
    e.catalogId,
    e.instructionFormat,
    e.sectionNumber,
    e.courseTitle
  ].join(' ')

  // Sort catalog ids by numeric portion first.
  const sortableCatalogId = `${e.catalogId.replace(/\D/g,'').padStart(3, '0')} ${e.catalogId}`
  e.sortableCourseName = [
    e.subjectArea,
    sortableCatalogId,
    e.instructionFormat,
    e.sectionNumber,
    e.courseTitle
  ].join(' ')
  e.sortableCourseNumber = e.courseNumber

  // When sorting by course number or name, keep cross-listings with home sections.
  if (e.crossListedWith || e.roomSharedWith) {
    let homeSection: any
    each((e.crossListedWith || e.roomSharedWith), s => {
      const candidateHomeSection = find(allEvaluations, {'courseNumber': s})
      if (candidateHomeSection && !candidateHomeSection.foreignDepartmentCourse && (e.foreignDepartmentCourse || e.courseNumber > candidateHomeSection.courseNumber)) {
        homeSection = candidateHomeSection
        return false
      }
    })
    if (homeSection) {
      e.sortableCourseNumber = `${homeSection.courseNumber}-${e.courseNumber}`
      const homeSectionSortableCatalogId = `${homeSection.catalogId.replace(/\D/g,'').padStart(3, '0')} ${homeSection.catalogId}`
      e.sortableCourseName = [
        homeSection.subjectArea,
        homeSectionSortableCatalogId,
        homeSection.instructionFormat,
        homeSection.sectionNumber,
        e.sortableCourseName
      ].join(' ')
    }
  }
  if (e.instructor) {
    e.searchableInstructor = `${e.instructor.firstName} ${e.instructor.lastName} ${e.instructor.uid} ${e.instructor.emailAddress}`
    e.sortableInstructor = `${e.instructor.lastName} ${e.instructor.firstName} ${e.instructor.uid} ${e.instructor.emailAddress}`
  } else {
    e.searchableInstructor = ''
    e.sortableInstructor = ''
  }
  const courseStartDate = DateTime.fromISO(e.meetingDates.start)
  const courseEndDate = DateTime.fromISO(e.meetingDates.end)
  const selectedTerm = find(useContextStore().config.availableTerms, {'id': e.termId})
  const defaultEndDate = DateTime.fromISO(get(selectedTerm, 'defaultDates.end'))
  const endDateDiff = courseEndDate.diff(courseStartDate, ['days'])
  let lastEndDate = courseEndDate > defaultEndDate ? courseEndDate : defaultEndDate
  if (lastEndDate === defaultEndDate && !selectedTerm.name.includes('Summer')) {
    lastEndDate = lastEndDate.plus({days: 2})
  }
  e.meetingDates.start = courseStartDate.toJSDate()
  e.meetingDates.end = courseEndDate.toJSDate()
  e.startDate = DateTime.fromISO(e.startDate).toJSDate()
  e.endDate = DateTime.fromISO(e.endDate).toJSDate()
  e.lastUpdated = DateTime.fromISO(e.lastUpdated).toJSDate()
  e.maxStartDate = endDateDiff.days < 90 ? lastEndDate.minus({days: 13}).toJSDate() : lastEndDate.minus({days: 20}).toJSDate()
}

const $_refresh = (departmentId: number) => {
  return new Promise<object>(resolve => {
    const termId = useContextStore().selectedTermId || useContextStore().config.currentTermId
    getDepartment(departmentId, termId).then((department: any) => {
      const departmentStore = useDepartmentStore()
      departmentStore.reset(department)
      departmentStore.updateSelectedEvaluationIds()
      return resolve(department)
    })
  })
}

export const useDepartmentStore = defineStore('department', {
  state: () => ({
    activeDepartmentForms: [] as DepartmentForm[],
    allDepartmentForms: [] as DepartmentForm[],
    contacts: [],
    department: undefined as Department | undefined,
    disableControls: false,
    errorDialog: false,
    errorDialogText: undefined as string | undefined,
    evaluations: [] as any[],
    note: undefined,
    selectedEvaluationIds: [] as any[],
    showTheOmenPoster: undefined as boolean | undefined
  }),
  actions: {
    addSection(sectionId: string, termId: string) {
      this.disableControls = true
      return new Promise((resolve: Function, reject) => {
        const departmentId = get(this.department, 'id', NaN)
        addSection(departmentId, sectionId, termId)
        .then(() => {
          getSectionEvaluations(departmentId, sectionId, termId).then((data: any) => {
            const updatedEvaluations = each(data, e => $_decorateEvaluation(e, this.evaluations))
            useDepartmentStore().replaceEvaluations(0, 0, updatedEvaluations)
            resolve()
          })
        })
        .catch(error => reject(error))
      })
    },
    deleteContact(userId: number) {
      this.disableControls = true
      const departmentId = get(this.department, 'id', NaN)
      return new Promise((resolve: Function) => {
        deleteContact(departmentId, userId).then(() => {
          $_refresh(departmentId).then(() => resolve())
        })
      })
    },
    deselectAllEvaluations() {
      this.selectedEvaluationIds = []
      each(this.evaluations, e => {
        e.isSelected = false
      })
    },
    dismissErrorDialog() {
      this.errorDialog = false
      this.errorDialogText = undefined
    },
    editEvaluation(evaluationId: number, sectionId: string, termId: string, fields: any[]) {
      return new Promise((resolve: Function, reject) => {
        const departmentId = get(this.department, 'id', NaN)
        updateEvaluations(departmentId, 'edit', [evaluationId], termId, fields).then(
          () => {
            getSectionEvaluations(departmentId, sectionId, termId).then((data: any) => {
              let sectionIndex = findIndex(this.evaluations, ['courseNumber', sectionId])
              if (sectionIndex === -1) {
                sectionIndex = this.evaluations.length
              }
              const sectionCount = filter(this.evaluations, ['courseNumber', sectionId]).length
              const updatedEvaluations = each(data, e => $_decorateEvaluation(e, this.evaluations))
              useDepartmentStore().replaceEvaluations(sectionIndex, sectionCount, updatedEvaluations)
              resolve()
            })
          },
          error => reject(error)
        )
      })
    },
    filterSelectedEvaluations(searchFilterResults: any[], enabledStatuses: any[]) {
      const selectedSearchFilterResultIds = intersectionWith(this.selectedEvaluationIds, searchFilterResults, (id: number | string, e: any) => {
        return toString(e.id) === toString(id)
      })
      const selectedEvaluationIds: any[] = []
      each(this.evaluations, e => {
        if (includes(enabledStatuses, e.status || 'unmarked') && includes(selectedSearchFilterResultIds, e.id)) {
          e.isSelected = true
          selectedEvaluationIds.push(e.id)
        } else {
          e.isSelected = false
        }
      })
      this.selectedEvaluationIds = selectedEvaluationIds
    },
    init(departmentId: number) {
      const config = useContextStore().config
      this.department = undefined
      this.activeDepartmentForms = reject(config.departmentForms, 'deletedAt')
      this.allDepartmentForms = config.departmentForms
      return new Promise<object>(resolve => {
        $_refresh(departmentId).then(department => {
          useDepartmentStore().updateSelectedEvaluationIds()
          resolve(department)
        })
      })
    },
    refreshAll() {
      return new Promise<object>(resolve => {
        $_refresh(get(this.department, 'id', NaN)).then(resolve)
      })
    },
    refreshSection(sectionId: string, termId: string, duplicatesCount: number) {
      return new Promise((resolve: Function) => {
        getSectionEvaluations(get(this.department, 'id', NaN), sectionId, termId).then((data: any) => {
          let sectionIndex = findIndex(this.evaluations, ['courseNumber', sectionId])
          if (sectionIndex === -1) {
            sectionIndex = this.evaluations.length
          }
          const updatedEvaluations = each(data, e => $_decorateEvaluation(e, this.evaluations))
          const deleteCount = updatedEvaluations.length - duplicatesCount
          useDepartmentStore().replaceEvaluations(sectionIndex, deleteCount, updatedEvaluations)
          resolve()
        })
      })
    },
    replaceEvaluations(startIndex: number, deleteCount: number, updatedEvaluations: any[]) {
      const evaluations = sortBy(updatedEvaluations, 'sortableCourseName')
      this.evaluations.splice(startIndex, deleteCount, ...evaluations)
    },
    reset(department: any){
      if (department) {
        this.contacts = department.contacts
        this.department = department
        each(department.evaluations, e => $_decorateEvaluation(e, department.evaluations))
        this.evaluations = sortBy(department.evaluations, 'sortableCourseName')
        this.note = get(department, 'note.note')
      }
      this.selectedEvaluationIds = []
      this.disableControls = false
    },
    selectAllEvaluations(searchFilterResults: any, enabledStatuses: string[]) {
      const selectedEvaluationIds: any[] = []
      each(this.evaluations, e => {
        if (includes(enabledStatuses, e.status || 'unmarked') && some(searchFilterResults, {'id': e.id})) {
          e.isSelected = true
          selectedEvaluationIds.push(e.id)
        }
      })
      this.selectedEvaluationIds = selectedEvaluationIds
    },
    setDisableControls(disableControls: boolean) {
      this.disableControls = disableControls
    },
    setEvaluations(evaluations: any[]) {
      each(evaluations, e => $_decorateEvaluation(e, evaluations))
      this.evaluations = evaluations
    },
    setIsSelected(evaluation: any) {
      const index = indexOf(this.selectedEvaluationIds, evaluation.id)
      if (index === -1 && !evaluation.isSelected) {
        evaluation.isSelected = true
        this.selectedEvaluationIds.push(evaluation.id)
      } else {
        evaluation.isSelected = false
        this.selectedEvaluationIds.splice(index, 1)
      }
    },
    setShowTheOmenPoster(show: boolean) {
      // This easter-egg flag can only be enabled once.
      if (!show || isUndefined(this.showTheOmenPoster)) {
        this.showTheOmenPoster = show
      }
    },
    showErrorDialog(text: string) {
      this.errorDialog = true
      this.errorDialogText = text
    },
    toggleSelectEvaluation(evaluation: any) {
      useDepartmentStore().setIsSelected(evaluation)
      const course = `${evaluation.subjectArea} ${evaluation.catalogId} ${evaluation.instructionFormat} ${evaluation.sectionNumber} (${evaluation.courseNumber})`
      const message = `${this.selectedEvaluationIds.includes(evaluation.id) ? '' : 'un'}selected ${course} evaluation`
      alertScreenReader(message)
    },
    updateContact(contact: any) {
      this.disableControls = true
      return new Promise<object>(resolve => {
        const departmentId = get(this.department, 'id', NaN)
        updateContact(departmentId, contact).then(() => {
          $_refresh(departmentId).then(resolve)
        })
      })
    },
    updateNote(note: any, termId: string) {
      this.disableControls = true
      return new Promise<object>(resolve => {
        const departmentId = get(this.department, 'id', NaN)
        updateDepartmentNote(departmentId, note, termId).then(() => {
          $_refresh(departmentId).then(resolve)
        })
      })
    },
    updateSelectedEvaluationIds() {
      this.selectedEvaluationIds = reduce(this.evaluations, (ids: any[], e) => {
        if (e.isSelected) {
          ids.push(e.id)
        }
        return ids
      }, [])
    }
  }
})

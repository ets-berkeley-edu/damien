import {defineStore} from 'pinia'
import {addDepartmentForm, deleteDepartmentForm, getDepartmentForms} from '@/api/departmentForms'
import {addEvaluationType, deleteEvaluationType, getEvaluationTypes} from '@/api/evaluationTypes'
import {addInstructor, deleteInstructor, getInstructors} from '@/api/instructor'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

export type ItemToDelete = {
  name: string | undefined,
  uid: string | undefined
}

function $_refreshDepartmentForms() {
  return getDepartmentForms().then((departmentForms: any) => {
    const contextStore = useContextStore()
    contextStore.setDepartmentForms(departmentForms)
    useListManagementStore().setDepartmentForms(contextStore.config.departmentForms)
  })
}

function $_refreshEvaluationTypes() {
  return getEvaluationTypes().then((evaluationTypes: any) => {
    useContextStore().setEvaluationTypes(evaluationTypes)
    useListManagementStore().setEvaluationTypes(useContextStore().config.evaluationTypes)
  })
}

function $_refreshInstructors() {
  return getInstructors().then(useListManagementStore().setInstructors)
}

const $_reset = () => {
  useListManagementStore().reset()
}

export const useListManagementStore = defineStore('listManagement', {
  state: () => ({
    departmentForms: [] as any[],
    disableControls: false,
    evaluationTypes: [] as any[],
    instructors: [] as any[],
    isAddingDepartmentForm: false,
    isAddingEvaluationType: false,
    isAddingInstructor: false,
    isConfirming: false,
    isSaving: false,
    itemToDelete: {} as ItemToDelete,
    onDelete: () => new Promise<any>(resolve => resolve(undefined))
  }),
  actions: {
    addDepartmentForm(name: string) {
      this.isSaving = true
      this.disableControls = true
      return addDepartmentForm(name).then($_refreshDepartmentForms).finally($_reset)
    },
    addEvaluationType(name: string) {
      this.isSaving = true
      this.disableControls = true
      return addEvaluationType(name).then(() => {
        $_refreshEvaluationTypes()
      }).finally($_reset)
    },
    addInstructor(name: string) {
      this.isSaving = true
      this.disableControls = true
      return addInstructor(name).then($_refreshInstructors).finally($_reset)
    },
    confirmDeleteDepartmentForm(itemToDelete: any) {
      this.isConfirming = true
      this.itemToDelete = {
        ...itemToDelete,
        description: 'department form',
        elementId: `delete-dept-form-${itemToDelete.id}-btn`
      }
      this.onDelete = useListManagementStore().deleteDepartmentForm
    },
    confirmDeleteEvaluationType(itemToDelete: any) {
      this.isConfirming = true
      this.itemToDelete = {
        ...itemToDelete,
        description: 'evaluation type',
        elementId: `delete-eval-type-${itemToDelete.id}-btn`
      }
      this.onDelete = useListManagementStore().deleteEvaluationType
    },
    confirmDeleteInstructor(itemToDelete: any) {
      this.isConfirming = true
      this.itemToDelete = {
        ...itemToDelete,
        name: `${itemToDelete.firstName} ${itemToDelete.lastName} (${itemToDelete.uid})`,
        description: 'instructor',
        elementId: `delete-instructor-${itemToDelete.uid}-btn`
      }
      this.onDelete = useListManagementStore().deleteInstructor
    },
    deleteDepartmentForm() {
      this.disableControls = true
      return new Promise<ItemToDelete | undefined>(resolve => {
        return deleteDepartmentForm(this.itemToDelete.name).then(() => {
          $_refreshDepartmentForms()
          resolve(this.itemToDelete)
        }).finally(() => {
          $_reset()
          putFocusNextTick('department-forms-card-title')
        })
      })
    },
    deleteEvaluationType() {
      this.disableControls = true
      return new Promise<object>(resolve => {
        return deleteEvaluationType(this.itemToDelete.name).then(() => {
          $_refreshEvaluationTypes()
          resolve(this.itemToDelete)
        }).finally(() => {
          $_reset()
          putFocusNextTick('evaluation-types-card-title')
        })
      })
    },
    deleteInstructor() {
      this.disableControls = true
      return new Promise<object>(resolve => {
        return deleteInstructor(this.itemToDelete.uid).then(() => {
          $_refreshInstructors()
          resolve(this.itemToDelete)
        }).finally(() => {
          $_reset()
          putFocusNextTick('manually-added-instructors-title')
        })
      })
    },
    init() {
      return Promise.all([getDepartmentForms(), getEvaluationTypes(), getInstructors()]).then(response => {
        const departmentForms: any[] = response[0]
        const evaluationTypes: any[] = response[1]
        const instructors: any[] = response[2]
        this.departmentForms = departmentForms
        useListManagementStore().setEvaluationTypes(evaluationTypes)
        useListManagementStore().setInstructors(instructors)
        const contextStore = useContextStore()
        contextStore.updateConfig('departmentForms', departmentForms)
        contextStore.updateConfig('evaluationTypes', evaluationTypes)
      })
    },
    reset() {
      this.disableControls = false
      this.isAddingDepartmentForm = false
      this.isAddingEvaluationType = false
      this.isAddingInstructor = false
      this.isConfirming = false
      this.isSaving = false
      this.itemToDelete = {name: undefined, uid: undefined}
      this.onDelete = () => new Promise<any>(resolve => resolve(undefined))
    },
    setAddingDepartmentForm() {
      return new Promise<void>(resolve => {
        $_reset()
        this.isAddingDepartmentForm = true
        resolve()
      })
    },
    setAddingEvaluationType() {
      return new Promise<void>(resolve => {
        $_reset()
        this.isAddingEvaluationType = true
        resolve()
      })
    },
    setAddingInstructor() {
      return new Promise<void>(resolve => {
        $_reset()
        this.isAddingInstructor = true
        resolve()
      })
    },
    setDepartmentForms(departmentForms: any[]) {
      this.departmentForms = departmentForms
    },
    setDisableControls(disable: boolean) {
      this.disableControls = disable
    },
    setEvaluationTypes(evaluationTypes: any[]) {
      this.evaluationTypes = evaluationTypes
    },
    setInstructors(instructors: any[]) {
      this.instructors = instructors
    }
  }
})

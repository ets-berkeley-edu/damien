import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {defineStore} from 'pinia'
import {find, get} from 'lodash'
import router from '@/router'

export type CurrentUser = {
  departments: any[],
  emailSupport: string,
  isAdmin: boolean,
  isAuthenticated: boolean,
  uid: string
}

export type DamienConfig = {
  apiBaseUrl: string,
  availableTerms: any[],
  currentTermId: string,
  currentTermName: string,
  departmentForms: any[],
  devAuthEnabled: false,
  easterEggMonastery: any,
  easterEggNannysRoom: string,
  evaluationTypes: any[],
  isVueAppDebugMode: boolean,
  scheduleLochRefresh: any
}

export const useContextStore = defineStore('context', {
  state: () => ({
    config: {} as DamienConfig,
    currentUser: {
      isAdmin: false,
      isAuthenticated: false
    } as CurrentUser,
    isModalOpen: false,
    isSelectedTermLocked: false,
    loading: false,
    screenReaderAlert: {
      message: '',
      politeness: 'polite'
    },
    selectedTermId: undefined as string | undefined,
    selectedTermName: undefined,
    serviceAnnouncement: {
      text: '',
      isLive: false
    },
    snackbar: {
      color: 'info',
      text: undefined as string | undefined,
      timeout: 8000
    },
    snackbarShow: false
  }),
  actions: {
    loadingComplete(pageTitle?: string, alert?: string) {
      document.title = `${pageTitle || 'UC Berkeley'} | Course Evaluations`
      this.loading = false
      if (alert) {
        alertScreenReader(alert)
      } else if (pageTitle) {
        alertScreenReader(`${pageTitle} loaded`)
      }
      putFocusNextTick('page-title')
    },
    loadingStart(srAlert?: string) {
      this.loading = true
      const route = router.currentRoute.value
      alertScreenReader(srAlert || `Loading ${String(get(route, 'name', ''))}.`)
    },
    selectTerm(termId: string|number) {
      return new Promise<void>((resolve, reject) => {
        const term = find(this.config.availableTerms, {'id': termId || this.config.currentTermId})
        if (term) {
          this.selectedTermId = term.id
          this.selectedTermName = term.name
          resolve(term)
        } else {
          reject()
        }
      })
    },
    setConfig(data: any) {
      this.config = data
    },
    setCurrentUser(currentUser: any) {
      this.currentUser = currentUser
    },
    setDepartmentForms(departmentForms: any) {
      this.config.departmentForms = departmentForms
    },
    setEvaluationTypes(evaluationTypes: any) {
      this.config.evaluationTypes = evaluationTypes
    },
    setIsModalOpen(isOpen: boolean) {
      this.isModalOpen = isOpen
    },
    setIsSelectedTermLocked(isLocked: boolean) {
      this.isSelectedTermLocked = isLocked
    },
    setScreenReaderAlert(screenReaderAlert: any) {
      this.screenReaderAlert = {
        message: screenReaderAlert.message,
        politeness: screenReaderAlert.politeness || 'polite'
      }
    },
    setServiceAnnouncement(data: any) {
      this.serviceAnnouncement = data
    },
    snackbarClose() {
      this.snackbarShow = false
      this.snackbar.text = undefined
      alertScreenReader('Message closed')
    },
    snackbarHide() {
      this.snackbarShow = false
      this.snackbar.text = undefined
    },
    snackbarOpen(text: string, color?: string) {
      this.snackbar.text = text
      this.snackbar.color = color || 'info'
      this.snackbarShow = true
    },
    snackbarReportError(text: string) {
      this.snackbar.text = text
      this.snackbar.color = 'error'
      this.snackbarShow = true
    },
    updateConfig(key: string, value: any) {
      this.config[key] = value
    }
  }
})

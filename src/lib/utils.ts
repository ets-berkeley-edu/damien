import {DateTime} from 'luxon'
import {concat, filter, head, initial, join, keys, last, split, trim} from 'lodash'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

let $_screenReaderAlertExpiry: number

const clearScreenReaderAlert = () => {
  window.clearInterval($_screenReaderAlertExpiry)
  useContextStore().setScreenReaderAlert({message: ''})
}

export function alertScreenReader(message: string, persistent?: boolean, politeness?: string) {
  clearScreenReaderAlert()
  nextTick(() => {
    useContextStore().setScreenReaderAlert({message, politeness})
    window.clearInterval($_screenReaderAlertExpiry)
    if (!persistent) {
      $_screenReaderAlertExpiry = window.setInterval(clearScreenReaderAlert, 5000)
    }
  })
}

export function getCatalogListings(department) {
  return filter(keys(department.catalogListings), trim)
}

export function oxfordJoin(arr: string[]) {
  switch(arr.length) {
  case 1: return head(arr)
  case 2: return `${head(arr)} and ${last(arr)}`
  default: return join(concat(initial(arr), ` and ${last(arr)}`), ', ')
  }
}

export function pluralize(noun: string, count: number, substitutions: any = {}, pluralSuffix: string = 's') {
  return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
}

export function putFocusNextTick(
  id: string,
  {scroll=true, scrollBlock='center', cssSelector=undefined}: {scroll?: boolean, scrollBlock?: any, cssSelector?: string}={}
) {
  const callable = () => {
    let el = document.getElementById(id)
    el = el && cssSelector ? el.querySelector(cssSelector) : el
    if (el) {
      el.focus()
      if (scroll) {
        el.scrollIntoView({behavior: 'smooth', block: scrollBlock})
      }
    }
    return !!el
  }
  nextTick(() => {
    let counter = 0
    const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
  })
}

// eslint-disable-next-line no-undef
export function scrollTo(anchor: string, scrollBlock?: ScrollLogicalPosition) {
  nextTick(() => {
    const element = document.getElementById(anchor)
    if (element) {
      element.classList.add('scroll-margins')
      element.scrollIntoView({behavior: 'smooth', block: scrollBlock || 'center'})
    }
  })
}

export function scrollToTop() {
  scrollTo('content', 'start')
}

export function stripAnchorRef(path: string) {
  return split(path, '#', 1)[0]
}

export function toFormatFromJsDate(jsDate: Date, format: string): string {
  // See https://moment.github.io/luxon/#/formatting?id=table-of-tokens
  return DateTime.fromJSDate(jsDate).toFormat(format)
}

export function toLocaleFromISO(isoString: string, luxonPreset?: any): string {
  // See https://moment.github.io/luxon/#/formatting?id=presets
  return DateTime.fromISO(isoString).toLocaleString(luxonPreset || DateTime.DATE_MED)
}

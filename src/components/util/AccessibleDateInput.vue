<template>
  <div class="date-picker d-flex position-relative">
    <DatePicker
      ref="datePicker"
      v-model.date="model"
      :disabled="disabled"
      :input-debounce="500"
      :max-date="maxDate"
      :min-date="minDate"
      :popover="{autoHide: false, placement: placement, visibility: 'focus'}"
      :step="1"
      @did-move="makeCalendarAccessible"
      @dayclick="() => putFocusNextTick(`${idPrefix}-clear-btn`)"
      @daykeydown="(day, e) => onDaykeydown(e)"
      @popover-did-hide="() => isPopoverVisible = false"
      @popover-did-show="onPopoverShown"
      @transition-start="() => onTransitionStart"
    >
      <template #default="{ inputValue, inputEvents }">
        <div class="v-theme--light custom-text-field" :class="{'disabled': disabled}">
          <input
            :id="inputId"
            type="text"
            :aria-controls="`${idPrefix}-popover`"
            :aria-describedby="ariaDescribedby"
            :aria-expanded="isPopoverVisible"
            aria-haspopup="dialog"
            :aria-invalid="!isValid(inputValue)"
            :aria-required="required"
            autocomplete="off"
            :class="{'error--text': !isValid(inputValue)}"
            :disabled="disabled"
            maxlength="10"
            placeholder="MM/DD/YYYY"
            :value="inputValue"
            @input="onInput($event, inputEvents)"
            @keyup="onInputKeyup($event, inputEvents)"
            @mouseleave="inputEvents.mouseleave"
            @mousemove="inputEvents.mousemove"
            @focus="() => onUpdateFocus(true, inputEvents)"
            @blur="() => onUpdateFocus(false, inputEvents)"
            @keydown="inputEvents.keydown"
            @paste="inputEvents.paste"
            @select="inputEvents.select"
            @change="inputEvents.change"
            @focusin="inputEvents.focusin"
            @focusout="inputEvents.focusout"
          >
        </div>
      </template>
    </DatePicker>
    <button
      v-if="model"
      :id="`${idPrefix}-clear-btn`"
      :aria-label="`Clear ${ariaLabel}`"
      class="v-btn clear-button"
      :disabled="disabled"
      @click.stop.prevent="event => onClickClear(event)"
    >
      <v-icon
        aria-hidden="true"
        color="secondary"
        :icon="mdiCloseCircle"
        size="1.25rem"
      />
    </button>
  </div>
</template>


<script setup>
import {DateTime} from 'luxon'
import {DatePicker} from 'v-calendar'
import {each} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  ariaLabel: {
    default: 'date',
    required: false,
    type: String
  },
  ariaDescribedby: {
    default: undefined,
    required: false,
    type: String
  },
  containerId: {
    required: true,
    type: String
  },
  disabled: {
    required: false,
    type: Boolean
  },
  getValue: {
    required: true,
    type: Function
  },
  idPrefix: {
    required: true,
    type: String
  },
  maxDate: {
    default: null,
    required: false,
    type: Date,
  },
  minDate: {
    default: null,
    required: false,
    type: Date,
  },
  placement: {
    default: 'top',
    required: false,
    type: String
  },
  required: {
    required: false,
    type: Boolean
  },
  setValue: {
    required: true,
    type: Function
  },
})

const model = defineModel({
  get() {
    return props.getValue()
  },
  set(v) {
    props.setValue(v)
  },
  type: Date
})
const dateInputEvents = ref(undefined)
const datePicker = ref()
const inputId = `${props.idPrefix}-input`
const isPopoverVisible = ref(false)
const popover = ref()

onBeforeUnmount(() => {
  const container = document.getElementById(props.containerId)
  if (container) {
    container.removeEventListener('keydown', onKeydownPreventClick)
  }
})

onMounted(() => {
  const container = document.getElementById(props.containerId)
  const popoverWrapper = container?.querySelector('.vc-popover-content-wrapper')
  if (popoverWrapper) {
    popoverWrapper.id = `${props.idPrefix}-popover`
  }
  // Setting this as a prop on the VTextField component breaks the "clear" button.
  document.getElementById(inputId)?.setAttribute('role', 'combobox')
  // Workaround for https://github.com/nathanreyes/v-calendar/issues/1459
  container?.addEventListener('keydown', onKeydownPreventClick)
  dateInputEvents.value = datePicker.value.inputEvents
})

const isMonthNavBtn = el => el.id === `${props.idPrefix}-popover-next-month-btn` || el.id === `${props.idPrefix}-popover-prev-month-btn`

const isSpaceOrEnter = key => {
  return key === ' ' || key === 'Spacebar' || key === 'Enter'
}

const isValid = dateString => {
  if (!dateString || dateString === '') {
    return true
  }
  const date = DateTime.fromFormat(dateString, 'MM/dd/yyyy')
  return date.isValid
}

const makeCalendarAccessible = () => {
  if (!popover.value) return

  const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const nextMonthBtn = popover.value.querySelector('.vc-next')
  const prevMonthBtn = popover.value.querySelector('.vc-prev')
  const srAlert = document.getElementById(`${props.idPrefix}-popover-sr-alert`)
  const title = popover.value.querySelector('.vc-title')
  const weeks = popover.value.querySelector('.vc-weeks')
  const weekdayLabels = popover.value.querySelectorAll('.vc-weekday')

  if (nextMonthBtn) {
    nextMonthBtn.ariaLabel = 'next month'
    nextMonthBtn.id = `${props.idPrefix}-popover-next-month-btn`
  }
  if (prevMonthBtn) {
    prevMonthBtn.ariaLabel = 'previous month'
    prevMonthBtn.id = `${props.idPrefix}-popover-prev-month-btn`
  }
  if (title) {
    title.id = `${props.idPrefix}-popover-title`
    title.classList.add('vc-focus')
    title.addEventListener('click', () => nextTick(makeNavAccessible))
    srAlert.innerText = title.innerText
  }
  if (weeks) {
    weeks.setAttribute('aria-labelledby', `${props.idPrefix}-popover-title`)
    weeks.role = 'grid'
  }
  each(weekdayLabels, (label, index) => {
    const abbr = document.createElement('abbr')
    abbr.innerText = label.innerText
    abbr.title = weekdays[index]
    label.innerHTML = abbr.outerHTML
  })
}

const makeNavAccessible = () => {
  const navPopover = popover.value ? popover.value.querySelector('.vc-nav-container') : null
  if (navPopover) {
    const nextYearButton = navPopover.querySelector('.vc-nav-arrow.is-right')
    const prevYearButton = navPopover.querySelector('.vc-nav-arrow.is-left')
    if (nextYearButton) {
      nextYearButton.ariaLabel = 'next year'
      nextYearButton.id = `${props.idPrefix}-popover-next-year-btn`
    }
    if (prevYearButton) {
      prevYearButton.ariaLabel = 'previous year'
      prevYearButton.id = `${props.idPrefix}-popover-prev-year-btn`
    }
  }
}

const onClickClear = (e) => {
  const inputElement = document.getElementById(inputId)
  if (inputElement) {
    inputElement.value = ''
    dateInputEvents.value.change(e)
    alertScreenReader('Cleared')
    putFocusNextTick(inputId)
    model.value = undefined
  }
}

const onDaykeydown = e => {
  if (e.code === 'Enter' || e.code === 'Space') {
    putFocusNextTick(`${props.idPrefix}-clear-btn`)
  }
}

const onInput = (event, inputEvents) => {
  inputEvents.input(event)
}

const onInputKeyup = (e, inputEvents) => {
  if (e.code === 'ArrowDown') {
    let selector
    if (model.value) {
      const selectedDate = DateTime.fromJSDate(model.value).toLocaleString({...DateTime.DATE_MED, weekday: 'long'})
      selector = `[aria-label="${selectedDate}"]`
    } else {
      selector = '[tabindex="0"]'
    }
    putFocusNextTick(`${props.idPrefix}-popover`, {cssSelector: selector})
  } else {
    inputEvents.keyup(e)
  }
}

const onKeydownPreventClick = e => {
  if (e && isMonthNavBtn(e.target) && isSpaceOrEnter(e.key)) {
    e.preventDefault()
  }
}

const onPopoverShown = popoverContent => {
  // Fill accessibility gaps in v-calendar date picker popover
  const helpContainer = popoverContent.querySelector('[data-helptext]')
  const liveRegion = document.createElement('span')
  popoverContent.ariaLabel = `choose ${props.ariaLabel}`
  popoverContent.ariaModal = false
  popoverContent.role = 'dialog'
  if (helpContainer) {
    const helpText = helpContainer.getAttribute('data-helptext')
    const helpEl = document.createElement('span')
    helpEl.className = 'sr-only'
    helpEl.ariaLive = 'polite'
    helpEl.id = `${props.idPrefix}-popover-help`
    helpContainer.prepend(helpEl)
    setTimeout(() => {
      helpEl.innerText = helpText
    }, 200)
  }
  liveRegion.className = 'sr-only'
  liveRegion.ariaLive = 'assertive'
  liveRegion.id = `${props.idPrefix}-popover-sr-alert`
  popoverContent.prepend(liveRegion)

  popover.value = popoverContent
  isPopoverVisible.value = true
  makeCalendarAccessible()
}

const onTransitionStart = () => {
  // When displaying a month, if maxDate falls within that month then the "next month" button
  // will be disabled (and similarly for minDate and the "previous month" button).
  // Prevent focus from landing on a disabled button and causing the popover to close prematurely.
  const prevMonthBtn = document.getElementById(`${props.idPrefix}-popover-prev-month-btn`)
  const nextMonthBtn = document.getElementById(`${props.idPrefix}-popover-next-month-btn`)

  if (prevMonthBtn && prevMonthBtn.disabled) {
    nextMonthBtn?.focus()
  } else if (nextMonthBtn && nextMonthBtn.disabled) {
    prevMonthBtn?.focus()
  }
}

const onUpdateFocus = (hasFocus, inputEvents) => {
  const el = document.getElementById(inputId)
  const event = {
    relatedTarget: hasFocus ? null : document.getElementById(props.containerId),
    srcElement: el,
    target: el,
    type: hasFocus ? 'focusin' : 'focusout'
  }
  dateInputEvents.value = inputEvents
  if (hasFocus) {
    inputEvents.focusin(event)
  } else {
    inputEvents.focusout(event)
  }
}
</script>

<style scoped>
.clear-button {
  background: transparent;
  border: none;
  border-radius: 100%;
  cursor: pointer;
  width: 1.75rem;
  height: 1.75rem;
  opacity: 0.9;
  position: absolute;
  right: 4px;
  top: 0.29rem;
  &:disabled {
    cursor: not-allowed;
    opacity: 0.26;
  }
  @supports not selector(:focus-visible) {
    &:focus {
      outline-color: rgba(var(--v-theme-secondary)) !important;
      outline-offset: -0.25rem;
      outline-style: solid;
      outline-width: 0.125rem;
      &::after {
        opacity: 0;
      }
    }
  }
  &:focus-visible {
    outline-color: rgba(var(--v-theme-secondary)) !important;
    outline-offset: -0.25rem;
    outline-style: solid;
    outline-width: 0.125rem;
    &::after {
      opacity: 0;
    }
  }
  &:hover {
    opacity: 1;
  }
}
.custom-text-field {
  align-items: center;
  display: flex;
  padding: .375rem .75rem;
  position: relative;
  transition: border-color 0.3s;
}
.custom-text-field input {
  background-color: transparent;
  border: none;
  flex: 1;
  outline: none;
  padding: 8px 0;
  width: 100%;
  &:disabled {
    color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
    cursor: not-allowed;
  }
}
.custom-text-field input::placeholder {
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.custom-text-field.error--text {
  border-color: rgb(var(--v-theme-error));
}
.custom-text-field.disabled {
  cursor: not-allowed;
  opacity: var(--v-disabled-opacity);
}
.date-picker {
  max-width: 15.625rem;
  min-width: 8.25rem;
}
</style>

<style>
.date-picker .vc-popover-content-wrapper {
  z-index: 1200;
}
@supports not selector(:focus-visible) {
  .vc-focus:focus {
    box-shadow: 0 0 0 0.125rem white;
    outline-color: rgba(var(--v-theme-secondary)) !important;
    outline-offset: 0.125rem;
    outline-style: solid;
    outline-width: 0.125rem;
  }
}
.vc-focus:focus-visible {
  box-shadow: 0 0 0 0.125rem white;
  outline-color: rgba(var(--v-theme-secondary)) !important;
  outline-offset: 0.125rem;
  outline-style: solid;
  outline-width: 0.125rem;
}
</style>


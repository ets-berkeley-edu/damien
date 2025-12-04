<template>
  <div :id="`${idPrefix}-container`" :class="containerClass">
    <component
      :is="isAutocomplete ? 'v-autocomplete' : 'v-combobox'"
      :id="`${idPrefix}-input`"
      ref="container"
      v-model="model"
      :aria-describedby="`${idPrefix}-desc`"
      autocomplete="off"
      :base-color="color"
      :bg-color="isAutocomplete ? 'white' : 'surface'"
      :class="clazz"
      clear-on-select
      :clearable="clearable"
      :color="color"
      :custom-filter="customFilter"
      density="compact"
      :debounce="500"
      :disabled="disabled"
      eager
      :error="error"
      :error-messages="errorMessages"
      hide-details
      :hide-no-data="isBusy || !query"
      :hide-selected="!isAutocomplete"
      :item-title="itemTitle"
      :item-value="itemValue"
      :items="items"
      :list-props="{ariaLive: ariaLive}"
      :menu-icon="isAutocomplete ? null : mdiChevronDown"
      :menu-props="menuProps"
      :multiple="!isAutocomplete"
      no-data-text="No results found."
      :no-filter="isAutocomplete || !query"
      :persistent-clear="clearable"
      :placeholder="placeholder || label"
      return-object
      :search="query"
      :variant="variant"
      @keydown.esc="onKeyDownEsc"
      @update:focused="onFocusInput"
      @update:menu="onToggleMenu"
      @update:search="onUpdateSearch"
    >
      <template #append-inner>
        <v-progress-circular
          v-if="isBusy"
          class="r-mx-2"
          color="tertiary"
          indeterminate
          size="x-small"
          width="2"
        />
      </template>
      <template #clear>
        <v-btn
          v-if="clearable && !isBusy"
          :id="`${idPrefix}-clear-btn`"
          :aria-label="`Clear ${label} input`"
          :class="{'disabled-opacity': !model}"
          color="secondary"
          density="compact"
          :disabled="!model"
          exact
          icon
          :ripple="false"
          variant="text"
          @keydown.enter.stop.prevent="onClearInput"
          @click.stop.prevent="onClearInput"
        >
          <v-icon
            color="secondary"
            :icon="mdiCloseCircle"
            size="21"
            aria-hidden="true"
          />
        </v-btn>
      </template>
      <template #item="{index, item}">
        <v-list-item
          :id="`${idPrefix}-option-${index}`"
          :aria-posinset="index"
          :aria-selected="index === focusedListItemIndex"
          :aria-setsize="itemCount || size(items)"
          base-color="secondary"
          class="font-size-18 autocomplete-list-item"
          role="option"
          @click="() => onSelectItem(item)"
          @focus="e => onFocusListItem(e, index)"
          @mouseenter="e => onFocusListItem(e, index)"
        >
          <template #title>
            <span v-html="itemLabel(item)" />
          </template>
        </v-list-item>
      </template>
      <template #selection="{item}">
        <slot name="selection" :item="item" />
      </template>
    </component>
  </div>
  <span aria-live="polite" class="sr-only">{{ resultsSummary }}</span>
</template>

<script setup>
import {get, size} from 'lodash'
import {mdiChevronDown, mdiCloseCircle} from '@mdi/js'
import {nextTick, onMounted, onUpdated, ref} from 'vue'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  ariaLabel: {
    default: undefined,
    required: false,
    type: String
  },
  ariaLive: {
    default: 'off',
    required: false,
    type: String
  },
  clazz: {
    default: '',
    required: false,
    type: [String, Object]
  },
  clearable: {
    required: false,
    type: Boolean
  },
  color: {
    default: 'secondary',
    required: false,
    type: String
  },
  containerClass: {
    default: '',
    required: false,
    type: [String, Object]
  },
  customFilter: {
    default: () => {},
    required: false,
    type: Function
  },
  disabled: {
    required: false,
    type: Boolean
  },
  error: {
    required: false,
    type: Boolean
  },
  errorMessages: {
    default: () => [],
    required: false,
    type: Array
  },
  getValue: {
    required: true,
    type: Function
  },
  idPrefix: {
    required: true,
    type: String
  },
  isAutocomplete: {
    required: false,
    type: Boolean
  },
  isBusy: {
    required: false,
    type: Boolean
  },
  itemCount: {
    default: undefined,
    required: false,
    type: Number
  },
  itemLabel: {
    default: v => v,
    required: false,
    type: Function
  },
  itemTitle: {
    default: 'title',
    required: false,
    type: String
  },
  itemValue: {
    default: 'value',
    required: false,
    type: String
  },
  items: {
    required: true,
    type: Array
  },
  label: {
    required: true,
    type: String
  },
  listLabel: {
    required: true,
    type: String
  },
  onClear: {
    default: () => {},
    required: false,
    type: Function
  },
  onKeyDownEsc: {
    default: () => {},
    required: false,
    type: Function
  },
  onUpdateSearch: {
    default: () => new Promise(resolve => resolve),
    required: false,
    type: Function
  },
  placeholder: {
    default: undefined,
    required: false,
    type: String
  },
  setValue: {
    required: true,
    type: Function
  },
  variant: {
    default: 'outlined',
    required: false,
    type: String
  },
  whenItemSelected: {
    default: () => {},
    required: false,
    type: Function
  }
})

const container = ref()
const filteredItemsCached = ref([])
const focusedListItemIndex = ref(undefined)
let menuProps = {}
const model = defineModel({
  get() {
    return props.getValue()
  },
  set(v) {
    props.setValue(v)
  },
  type: String
})
const query = ref(undefined)
const resultsSummary = ref(undefined)
const resultsSummaryInterval = ref(undefined)

onMounted(() => {
  const combobox = getComboboxElement()
  const input = getInputElement()
  if (combobox) {
    combobox.removeAttribute('role')
    combobox.removeAttribute('aria-expanded')
  }
  if (input) {
    input.setAttribute('role', 'combobox')
    input.setAttribute('aria-autocomplete', 'list')
    input.setAttribute('aria-controls', `${props.idPrefix}-menu`)
    input.setAttribute('aria-expanded', false)
    input.setAttribute('aria-label', props.ariaLabel || props.label)
  }
  menuProps = {
    closeOnContentClick: true,
    id: `${props.idPrefix}-menu`,
    openOnContentClick: !props.isAutocomplete
  }
  filteredItemsCached.value = container.value.filteredItems
})

onUpdated(() => {
  nextTick(() => {
    const combobox = getComboboxElement()
    if (combobox) {
      const menuId = combobox.getAttribute('aria-owns')
      combobox.removeAttribute('aria-expanded')
      if (menuId) {
        combobox.setAttribute('aria-controls', menuId)
        combobox.removeAttribute('aria-owns')
      }
    }
  })
})

const getComboboxElement = () => {
  const container = document.getElementById(`${props.idPrefix}-container`)
  return container ? container.querySelector('.v-field') : null
}

const getInputElement = () => {
  return document.getElementById(`${props.idPrefix}-input`)
}

const onClearInput = () => {
  model.value = null
  query.value = ''
  props.onClear()
  alertScreenReader('Cleared.')
  putFocusNextTick(`${props.idPrefix}-input`)
}

const onFocusInput = isFocused => {
  const input = getInputElement()
  input.removeAttribute('aria-activedescendant')
  focusedListItemIndex.value = null
  // Passing open-on-focus via menuProps (https://vuetifyjs.com/en/api/v-menu/#props-open-on-focus)
  // doesn't seem to have an effect, thus this workaround.
  if (isFocused) {
    // TODO: 'props.openOnFocus' is undefined. Can we remove it?
    // eslint-disable-next-line vue/no-undef-properties
    if (props.openOnFocus && !container.value.menu) {
      container.value.menu = true
    }
    container.value.filteredItems = filteredItemsCached.value
  }
}

const onFocusListItem = (event, index) => {
  const input = getInputElement()
  input.setAttribute('aria-activedescendant', event.target.id)
  focusedListItemIndex.value = index
}

const onSelectItem = item => {
  model.value = get(item.raw, 'value', item.raw)
  query.value = ''
  nextTick(props.whenItemSelected)
}

const onToggleMenu = isOpen => {
  nextTick(() => {
    const input = getInputElement()
    if (input) {
      if (isOpen) {
        const menu = document.getElementById(`${props.idPrefix}-menu`)
        const listbox = menu && menu.querySelector('[role="listbox"]')
        if (listbox) {
          listbox.setAttribute('aria-label', props.listLabel)
        }
        input.setAttribute('aria-expanded', true)
      } else {
        input.setAttribute('aria-expanded', false)
        input.removeAttribute('aria-activedescendant')
        clearInterval(resultsSummaryInterval.value)
      }
    }
  })
}

const onUpdateSearch = q => {
  query.value = q
  props.onUpdateSearch(q).then(() => {
    clearInterval(resultsSummaryInterval.value)
    resultsSummary.value = ''
    nextTick(() => {
      filteredItemsCached.value = container.value.filteredItems
      if (query.value) {
        resultsSummaryInterval.value = setInterval(setResultsSummary, 1000)
      }
    })
  })
}

const setResultsSummary = () => {
  clearInterval(resultsSummaryInterval.value)
  resultsSummary.value = pluralize('result', filteredItemsCached.value.length, {0: 'No'})
}
</script>

<style>
.autocomplete-list-item .highlight-match {
  background-color: rgba(var(--v-theme-primary), var(--v-pressed-opacity));
}
</style>

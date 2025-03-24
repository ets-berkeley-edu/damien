<template>
  <div :id="`${idPrefix}-container`" :class="containerClass">
    <component
      :is="isAutocomplete ? 'v-autocomplete' : 'v-combobox'"
      :id="`${idPrefix}-input`"
      ref="container"
      v-model="model"
      :aria-describedby="`${idPrefix}-desc`"
      :auto-select-first="!isAutocomplete"
      autocomplete="off"
      base-color="secondary"
      :bg-color="isAutocomplete ? 'white' : 'surface'"
      :class="clazz"
      color="secondary"
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
      :loading="isBusy"
      :menu-icon="null"
      :menu-props="{closeOnContentClick: true, id: `${idPrefix}-menu`}"
      :multiple="!isAutocomplete"
      no-data-text="No results found."
      :no-filter="isAutocomplete"
      :placeholder="placeholder || label"
      return-object
      :search="query"
      :variant="variant"
      @blur.stop.prevent="onBlur"
      @keydown.esc="onKeyDownEsc"
      @update:focused="onFocusInput"
      @update:menu="onToggleMenu"
      @update:search="onUpdateSearch"
    >
      <template #loader="{isActive}">
        <v-progress-circular
          v-if="isActive"
          class="mr-2"
          color="tertiary"
          indeterminate
          size="x-small"
          width="2"
        />
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
        <slot name="selection" :item="item"></slot>
      </template>
    </component>
  </div>
</template>

<script setup>
import {pluralize} from '@/lib/utils'
import {get, filter, includes, isEmpty, size} from 'lodash'
import {nextTick, onMounted, onUpdated, ref} from 'vue'

const props = defineProps({
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
  containerClass: {
    default: '',
    required: false,
    type: [String, Object]
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
  filterResults: {
    default: () => {},
    required: false,
    type: Function
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
const focusedListItemIndex = ref(undefined)
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
  if (combobox) {
    combobox.removeAttribute('role')
    combobox.removeAttribute('aria-expanded')
  }
  const input = getInputElement()
  if (input) {
    input.setAttribute('role', 'combobox')
    input.setAttribute('aria-autocomplete', 'list')
    input.setAttribute('aria-controls', `${props.idPrefix}-menu`)
    input.setAttribute('aria-expanded', false)
    input.setAttribute('aria-label', props.label)
  }
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

const onBlur = () => {
  const input = getInputElement()
  input.removeAttribute('aria-activedescendant')
  focusedListItemIndex.value = null
  if (isEmpty(query.value)) {
    props.onClear()
  }
}

const onFocusInput = isFocused => {
  if (isFocused) {
    const input = getInputElement()
    input.removeAttribute('aria-activedescendant')
    focusedListItemIndex.value = null
    // Passing open-on-focus via menuProps (https://vuetifyjs.com/en/api/v-menu/#props-open-on-focus)
    // doesn't seem to have an effect, thus this workaround.
    if (props.openOnFocus && !container.value.menu) {
      container.value.menu = true
    }
  }
}

const onFocusListItem = (event, index) => {
  const input = getInputElement()
  input.setAttribute('aria-activedescendant', event.target.id)
  focusedListItemIndex.value = index
}

const onSelectItem = item => {
  model.value = get(item.raw, 'value', item.raw)
  if (!model.value) {
    query.value = null
  }
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
  props.filterResults(q)
  clearInterval(resultsSummaryInterval.value)
  resultsSummaryInterval.value = setInterval(setResultsSummary, 1000)
}

const setResultsSummary = () => {
  const menuOverlay = document.getElementById(`${props.idPrefix}-menu`)
  const listbox = menuOverlay && menuOverlay.querySelector('[role="listbox"]')
  clearInterval(resultsSummaryInterval.value)
  if (listbox) {
    const suggestions = filter(listbox.children, child => includes(child.classList, 'v-list-item'))
    resultsSummary.value = pluralize('result', suggestions.length)
  } else {
    resultsSummary.value = ''
  }
}
</script>

<style>
.autocomplete-list-item .highlight-match {
  background-color: rgba(var(--v-theme-primary), var(--v-pressed-opacity));
}
</style>

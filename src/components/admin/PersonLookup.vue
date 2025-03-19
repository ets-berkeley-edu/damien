<template>
  <div :class="inline ? 'v-row d-flex align-center v-row--dense' : 'd-flex flex-column'">
    <div :class="{'v-col v-col-4': inline}">
      <label
        :id="`${idPrefix}-label`"
        :for="`${idPrefix}-input`"
        :class="labelClass"
      >
        <span v-if="label">{{ label }} <span class="sr-only">{{ placeholder }}</span></span>
      </label>
    </div>
    <div :id="`${idPrefix}-container`" :class="{'v-col v-col-6': inline}">
      <v-autocomplete
        :id="`${idPrefix}-input`"
        ref="container"
        v-model="selected"
        :aria-describedby="`${idPrefix}-error`"
        :aria-disabled="disabled"
        :aria-labelledby="`${idPrefix}-label`"
        autocomplete="off"
        class="person-lookup"
        :class="inputClass"
        clearable
        color="secondary"
        base-color="secondary"
        bg-color="white"
        density="compact"
        :disabled="disabled"
        eager
        :error="required && !suppressValidation && !!size(errors)"
        :error-messages="required && !suppressValidation ? errors : []"
        hide-details
        :hide-no-data="isSearching || !query"
        :items="suggestions"
        :list-props="{ariaLive: 'off'}"
        :loading="isSearching ? 'primary' : false"
        :menu-icon="null"
        :menu-props="{closeOnContentClick: true, id: `${idPrefix}-menu`}"
        no-data-text="No results found."
        no-filter
        persistent-clear
        :placeholder="placeholder"
        return-object
        :search="query"
        :variant="variant"
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
        <template #clear>
          <v-btn
            v-if="!isSearching"
            :id="`${idPrefix}-clear-btn`"
            :aria-label="`Clear ${label} input`"
            :class="{'disabled-opacity': !selected}"
            color="secondary"
            density="compact"
            :disabled="!selected"
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
            ></v-icon>
          </v-btn>
        </template>
        <template #item="{index, item}">
          <v-list-item
            :id="`${idPrefix}-option-${index}`"
            :aria-selected="index === focusedListItemIndex"
            base-color="secondary"
            class="font-size-18 person-lookup-result"
            @click="() => onSelectItem(item)"
            @focus="e => onFocusListItem(e, index)"
            @mouseenter="e => onFocusListItem(e, index)"
          >
            <template #title>
              <span v-html="suggest(item)" />
            </template>
          </v-list-item>
        </template>
        <template #selection="{item}">
          <span class="truncate-with-ellipsis">{{ getUserLabel(item.value) }}</span>
        </template>
      </v-autocomplete>
    </div>
    <div
      :id="`${idPrefix}-error`"
      aria-live="assertive"
      :class="{'v-col v-col-2 pl-0': inline}"
      role="alert"
    >
      <div
        v-if="required && !suppressValidation && errors && errors[0]"
        class="v-messages text-error px-3 mt-1"
        :class="theme.global.current.value.dark ? 'text-error-lighten-2' : ''"
      >
        {{ errors[0] }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {debounce, delay, each, get, replace, size, split, trim} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {nextTick, onMounted, onUpdated, ref} from 'vue'
import {pluralize} from '@/lib/utils'
import {searchInstructors} from '@/api/instructor'
import {searchUsers} from '@/api/user'
import {useTheme} from 'vuetify'

const props = defineProps({
  disabled: {
    required: false,
    type: Boolean
  },
  excludeUids: {
    default: () => [],
    required: false,
    type: Array
  },
  idPrefix: {
    default: 'person-lookup',
    required: false,
    type: String
  },
  inline: {
    required: false,
    type: Boolean
  },
  inputClass: {
    default: '',
    required: false,
    type: String
  },
  instructorLookup: {
    required: false,
    type: Boolean
  },
  label: {
    default: null,
    required: false,
    type: String
  },
  labelClass: {
    default: null,
    required: false,
    type: String
  },
  listLabel: {
    required: true,
    type: String
  },
  onKeyDownEsc: {
    default: () => {},
    required: false,
    type: Function
  },
  onSelectResult: {
    default: () => {},
    required: false,
    type: Function
  },
  placeholder: {
    default: 'Name or UID',
    required: false,
    type: String
  },
  required: {
    required: false,
    type: Boolean
  },
  variant: {
    default: 'outlined',
    required: false,
    type: String
  }
})

const container = ref()
const debouncedSearch = ref(v => v)
const errors = ref([])
const focusedListItemIndex = ref(undefined)
const isSearching = ref(false)
const query = ref(undefined)
// const selected = defineModel('selected', {default: {}, type: Object})
const selected = ref(undefined)
const suggestions = ref([])
const suppressValidation = ref(true)
const theme = useTheme()

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
  debouncedSearch.value = debounce(executeSearch, 300)
})

onUpdated(() => {
  const combobox = getComboboxElement()
  if (combobox) {
    combobox.removeAttribute('aria-expanded')
  }
})

const executeSearch = () => {
  const apiSearch = props.instructorLookup ? searchInstructors : searchUsers
  apiSearch(query.value, props.excludeUids).then(users => {
    suggestions.value = []
    each(users, user => {
      suggestions.value.push({
        title: getUserLabel(user),
        value: user
      })
    })
    isSearching.value = false
    alertScreenReader(pluralize('result', suggestions.value.length))
  })
}

const getComboboxElement = () => {
  const container = document.getElementById(`${props.idPrefix}-container`)
  return container ? container.querySelector('.v-field') : null
}

const getInputElement = () => {
  return document.getElementById(`${props.idPrefix}-input`)
}

const getUserLabel = user => `${user.firstName} ${user.lastName} (${user.uid})`

const onClearInput = () => {
  query.value = selected.value = null
  suggestions.value = []
  props.onSelectResult(null)
  alertScreenReader('Cleared.')
  putFocusNextTick(`${props.idPrefix}-input`)
}


const onFocusInput = isFocused => {
  // Passing open-on-focus via menuProps (https://vuetifyjs.com/en/api/v-menu/#props-open-on-focus)
  // doesn't seem to have an effect, thus this workaround.
  if (props.openOnFocus && isFocused && !container.value.menu) {
    container.value.menu = true
  }
}

const onFocusListItem = (event, index) => {
  const input = getInputElement()
  input.setAttribute('aria-activedescendant', event.target.id)
  focusedListItemIndex.value = index
}

const onSelectItem = item => {
  selected.value = get(item.raw, 'value', item.raw)
  validate(selected.value)
  if (!selected.value) {
    query.value = null
  }
  props.onSelectResult(selected.value)
  suggestions.value = []
  query.value = ''
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
      }
    }
  })
}

const onUpdateSearch = q => {
  const trimmed = trim(q)
  query.value = q
  suppressValidation.value = false
  if (trimmed) {
    isSearching.value = true
    debouncedSearch.value()
  } else {
    isSearching.value = false
    selected.value = null
    suggestions.value = []
  }
}

const suggest = item => {
  let label = item.title
  each(split(trim(query.value)), token => {
    label = replace(label, new RegExp(token, 'ig'), match => `<strong class="highlight-match">${match}</strong>`)
  })
  return label
}

const validate = suggestion => {
  delay(() => {
    errors.value = suggestion || !props.required || suppressValidation.value ? [] : ['Required']
  }, 300)
}
</script>

<style>
.person-lookup-result .highlight-match {
  background-color: rgba(var(--v-theme-primary), var(--v-pressed-opacity));
}
</style>
<style scoped>
.autocomplete-menu {
  z-index: 210 !important;
}
.person-lookup {
  overflow-x: clip;
  width: 100%;
}
:deep(.person-lookup .v-autocomplete__selection) {
  max-width: 110%;
}
:deep(.person-lookup .v-field) {
  padding: 0 !important;
}
:deep(.person-lookup .v-field__clearable) {
  height: 38px;
  max-height: 38px;
}
:deep(.person-lookup .v-field__input) {
  flex-wrap: nowrap;
  height: 38px;
  max-height: 38px;
  padding-inline-start: 12px !important;
}
:deep(.person-lookup .v-field__loader) {
  display: flex;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  padding-right: 1px;
  top: 0;
}
:deep(.person-lookup .v-input__control) {
  height: 38px;
}
</style>

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
    <AccessibleCombobox
      :clazz="`person-lookup ${inputClass}`"
      :container-class="{'v-col v-col-6': inline}"
      :disabled="disabled"
      :error="required && !suppressValidation && !!size(errors)"
      :error-messages="required && !suppressValidation ? errors : []"
      :filter-results="onUpdateSearch"
      :get-value="() => selected"
      :id-prefix="idPrefix"
      is-autocomplete
      :is-busy="isSearching"
      :item-label="suggest"
      :items="suggestions"
      :label="label"
      :list-label="listLabel"
      :on-clear="onClearInput"
      :on-key-down-esc="onKeyDownEsc"
      :placeholder="placeholder"
      :set-value="v => selected = v"
      :when-item-selected="onSelectItem"
    >
      <template #selection="{item}">
        <span class="truncate-with-ellipsis">{{ getUserLabel(item.value) }}</span>
      </template>
    </AccessibleCombobox>
    <div
      :id="`${idPrefix}-desc`"
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
import AccessibleCombobox from '@/components/util/AccessibleCombobox'
import {alertScreenReader} from '@/lib/utils'
import {debounce, delay, each, replace, size, split, trim} from 'lodash'
import {onMounted, ref} from 'vue'
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

const debouncedSearch = ref(v => v)
const errors = ref([])
const isSearching = ref(false)
const query = ref(undefined)
// const selected = defineModel('selected', {default: {}, type: Object})
const selected = ref(undefined)
const suggestions = ref([])
const suppressValidation = ref(true)
const theme = useTheme()

onMounted(() => {
  debouncedSearch.value = debounce(executeSearch, 300)
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

const getUserLabel = user => `${user.firstName} ${user.lastName} (${user.uid})`

const onClearInput = () => {
  query.value = null
  suggestions.value = []
  props.onSelectResult(null)
}

const onSelectItem = () => {
  validate(selected.value)
  if (!selected.value) {
    query.value = null
  }
  props.onSelectResult(selected.value)
  suggestions.value = []
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

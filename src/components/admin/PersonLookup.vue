<template>
  <div class="d-flex flex-column flex-grow-1">
    <label :id="`${id}-label`" class="sr-only" :for="id">Name or UID</label>
    <v-autocomplete
      :id="id"
      v-model="selected"
      :allow-overflow="false"
      :append-icon="null"
      :aria-disabled="disabled"
      :aria-labelledby="`${id}-label`"
      auto-select-first
      :background-color="disabled ? 'disabled' : 'white'"
      class="person-lookup"
      dense
      :disabled="disabled"
      :error="required && !!$_.size(errors)"
      :error-messages="required ? errors : []"
      hide-details
      :hide-no-data="isSearching || !search"
      :items="suggestions"
      :loading="isSearching ? 'tertiary' : false"
      :menu-props="menuProps"
      no-data-text="No results found."
      no-filter
      outlined
      :placeholder="placeholder"
      return-object
      :search-input.sync="search"
      single-line
      @blur="onBlur"
      @update:list-index="onHighlight"
    >
      <template #selection="data">
        <span class="text-nowrap">{{ toLabel(data.item) }}</span>
      </template>
      <template #item="data">
        <v-list-item
          v-bind="data.attrs"
          :aria-selected="data.item === highlightedItem"
          class="tertiary--text"
          v-on="data.on"
        >
          <v-list-item-content>
            <span v-html="suggest(data.item)" />
          </v-list-item-content>
        </v-list-item>
      </template>
    </v-autocomplete>
    <div
      v-if="required && errors && errors[0]"
      :id="`${id}-error`"
      class="v-messages error--text px-3 mt-1"
      :class="$vuetify.theme.dark ? 'text--lighten-2' : ''"
      role="alert"
    >
      {{ errors[0] }}
    </div>
  </div>
</template>

<script>
import {searchInstructors} from '@/api/instructor'
import {searchUsers} from '@/api/user'

export default {
  name: 'PersonLookup',
  props: {
    disabled: {
      required: false,
      type: Boolean
    },
    excludeUids: {
      default: () => [],
      required: false,
      type: Array
    },
    id: {
      default: 'input-person-lookup-autocomplete',
      required: false,
      type: String
    },
    instructorLookup: {
      required: false,
      type: Boolean
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
    }
  },
  data: () => ({
    errors: [],
    highlightedItem: undefined,
    isSearching: false,
    menuProps: {
      contentClass: 'v-sheet--outlined autocomplete-menu'
    },
    search: undefined,
    searchTokenMatcher: undefined,
    selected: undefined,
    suggestions: []
  }),
  watch: {
    search(snippet) {
      this.isSearching = true
      this.debouncedSearch(snippet)
    },
    selected(suggestion) {
      this.validate(suggestion)
      if (!suggestion) {
        this.search = null
      }
      this.onSelectResult(suggestion)
    }
  },
  methods: {
    executeSearch(snippet) {
      if (snippet) {
        const apiSearch = this.instructorLookup ? searchInstructors : searchUsers
        apiSearch(snippet, this.excludeUids).then(results => {
          const searchTokens = this.$_.split(this.$_.trim(snippet), /\W/g)
          this.searchTokenMatcher = RegExp(this.$_.join(searchTokens, '|'), 'gi')
          this.suggestions = results
          this.isSearching = false
        })
      } else {
        this.isSearching = false
        this.searchTokenMatcher = null
        this.selected = null
        this.suggestions = []
      }
    },
    onBlur() {
      if (!this.isSearching && !!this.search && this.suggestions.length && !this.selected) {
        this.selected = this.suggestions[0]
      }
    },
    onHighlight(index) {
      this.highlightedItem = this.suggestions[index]
    },
    suggest(user) {
      return this.toLabel(user).replace(this.searchTokenMatcher, match => `<strong>${match}</strong>`)
    },
    toLabel(user) {
      return user && user instanceof Object ? `${user.firstName || ''} ${user.lastName || ''} (${user.uid})`.trim() : user
    },
    validate(suggestion) {
      this.$_.delay(() => {
        if (!suggestion && this.required) {
          this.errors = ['Required']
        } else {
          this.errors = []
        }
      }, 300)
    }
  },
  created() {
    this.debouncedSearch = this.$_.debounce(this.executeSearch, 300)
  }
}
</script>

<style>
.autocomplete-menu {
  z-index: 203 !important;
}
.person-lookup {
  overflow-x: clip;
}
.person-lookup .v-select__selections,
.person-lookup .v-select__selections input {
  color: rgba(0, 0, 0, 0.87) !important;
}
.person-lookup.v-input--is-focused {
  appearance: auto !important;
  caret-color: #000 !important;
  color: -webkit-focus-ring-color !important;
  outline: auto !important;
  outline-color: -webkit-focus-ring-color !important;
  outline-offset: 0px !important;
  outline-style: auto !important;
  outline-width: 1px !important;
}
</style>
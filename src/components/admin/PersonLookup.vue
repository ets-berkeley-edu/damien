<template>
  <v-autocomplete
    :id="id"
    v-model="selected"
    :append-icon="null"
    class="autocomplete-input"
    dense
    :hide-no-data="true"
    :items="suggestions"
    :loading="isSearching"
    no-filter
    outlined
    placeholder="UID or CSID"
    return-object
    :search-input.sync="search"
    hide-details="auto"
  ></v-autocomplete>
</template>

<script>
import {searchInstructors, searchUsers} from '@/api/user'

export default {
  name: 'PersonLookup',
  props: {
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
    }
  },
  data: () => ({
    isSearching: false,
    search: undefined,
    selected: undefined,
    suggestions: undefined
  }),
  watch: {
    search(snippet) {
      this.debouncedSearch(snippet)
    },
    selected(suggestion) {
      if (suggestion) {
        this.onSelectResult(suggestion.value)
      }
    }
  },
  methods: {
    executeSearch(snippet) {
      if (snippet) {
        this.isSearching = true
        const apiSearch = this.instructorLookup ? searchInstructors : searchUsers
        apiSearch(snippet, this.excludeUids).then(results => {
          this.suggestions = this.$_.map(results, this.suggest)
          this.isSearching = false
        })
      } else {
        this.suggestions = []
      }
    },
    suggest(user) {
      return {
        text: `${user.firstName} ${user.lastName} (${user.uid})`,
        value: user
      }
    }
  },
  created() {
    this.debouncedSearch = this.$_.debounce(this.executeSearch, 300)
  }
}
</script>

<style>
.autocomplete-input {
  background-color: white !important;
}
</style>
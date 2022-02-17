<template>
  <v-autocomplete
    :id="id"
    v-model="selected"
    :append-icon="null"
    dense
    :hide-no-data="true"
    :items="suggestions"
    :loading="isSearching"
    no-filter
    outlined
    placeholder="UID or CSID"
    return-object
    :search-input.sync="search"
  ></v-autocomplete>
</template>

<script>
import {searchUsers} from '@/api/user'

export default {
  name: 'PersonLookup',
  props: {
    id: {
      default: 'input-person-lookup-autocomplete',
      required: false,
      type: String
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
      if (snippet) {
        this.isSearching = true
        searchUsers(snippet).then(results => {
          this.suggestions = this.$_.map(results, this.suggest)
          this.isSearching = false
        })
      } else {
        this.suggestions = []
      }
    },
    selected(suggestion) {
      if (suggestion) {
        this.onSelectResult(suggestion.value)
      }
    }
  },
  methods: {
    suggest(user) {
      let label = `${user.firstName} ${user.lastName} (${user.uid}`
      label += user.csid ? ` ${user.csid})` : ')'
      return {
        text: label,
        value: user
      }
    }
  }
}
</script>

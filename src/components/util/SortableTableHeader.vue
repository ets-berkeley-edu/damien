<template>
  <tr>
    <th
      v-for="column in columns"
      :key="column.key"
      :aria-label="column.title"
      :aria-sort="isSorted(column) ? (sortDesc ? 'descending' : 'ascending') : 'none'"
      class="px-0"
      :class="column.class"
      scope="col"
      :style="column.headerProps"
    >
      <v-btn
        v-if="column.sortable"
        :id="`sort-col-${id}${column.value}-btn`"
        :aria-label="`Sort by ${column.title} ${isSorted(column) && !sortDesc ? 'descending' : 'ascending'}`"
        :append-icon="sortIcon(column)"
        block
        class="sort-col-btn font-weight-bold text-no-wrap v-table-sort-btn-override"
        :class="{'icon-visible': isSorted(column)}"
        density="compact"
        size="small"
        variant="plain"
        @click="() => onSort(column)"
      >
        {{ column.title }}
      </v-btn>
      <div v-if="!column.sortable">
        {{ column.title }}
      </div>
    </th>
    <th class="compact-table-header" :colspan="columns.length">
      <select
        :id="`sort-col-${id}all-btn`"
        v-model="selectedSortColumn"
        autocomplete="off"
        class="mb-2 w-100 w-sm-50"
        :disabled="disableControls"
      >
        <option selected :value="selectedSortColumn">Sort by...</option>
        <option v-for="col in sortableColumns" :key="col.key" :value="col.title">{{ col.title }}</option>
      </select>
    </th>
  </tr>
</template>

<script setup>
import {filter} from 'lodash'
import {computed, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useDepartmentStore} from '@/stores/department/department-edit-session'

const props = defineProps({
  columns: {
    required: true,
    type: Array
  },
  id: {
    default: '',
    required: false,
    type: String
  },
  isSorted: {
    required: true,
    type: Function
  },
  onSort: {
    default: () => {},
    required: false,
    type: Function
  },
  sortDesc: {
    required: false,
    type: Boolean
  },
  sortIcon: {
    default: () => {},
    required: false,
    type: Function
  }
})

const {disableControls} = storeToRefs(useDepartmentStore())
const selectedSortColumn = ref(undefined)
const sortableColumns = computed(() => {
  return filter(props.columns, 'sortable')
})
</script>

<style scoped>
.compact-table-header {
  display: none;
}
.sort-col-btn {
  height: 28px !important;
  letter-spacing: normal !important;
  margin: 0 4px 0 -.1em;
  min-width: 0px !important;
  padding: 0 2px 0 4px;
}
</style>
<style>
.v-table-sort-btn-override .v-btn__append {
  margin-inline: 2px 1px !important;
}
.v-table-sort-btn-override .v-btn__append .v-icon {
  opacity: 0;
}
.v-table-sort-btn-override .v-btn__content {
  text-align: left;
}
.v-table-sort-btn-override:active .v-btn__append .v-icon,
.v-table-sort-btn-override:hover .v-btn__append .v-icon,
.v-table-sort-btn-override:focus .v-btn__append .v-icon {
  opacity: var(--v-medium-emphasis-opacity);
}
.v-table-sort-btn-override.icon-visible .v-btn__append .v-icon {
  opacity: 1;
}
</style>

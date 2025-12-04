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
  </tr>
</template>

<script setup>
defineProps({
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
</script>

<style scoped>
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
.v-table-sort-btn-override:active .v-btn__append .v-icon,
.v-table-sort-btn-override:hover .v-btn__append .v-icon,
.v-table-sort-btn-override:focus .v-btn__append .v-icon {
  opacity: var(--v-disabled-opacity);
}
.v-table-sort-btn-override.icon-visible .v-btn__append .v-icon {
  opacity: 1;
}
</style>

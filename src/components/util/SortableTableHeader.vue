<template>
  <thead class="v-data-table-header">
    <tr>
      <th
        v-for="(item, index) in headers"
        :key="index"
        :aria-sort="sortBy && item.value === sortBy ? (sortDesc ? 'descending' : 'ascending') : 'none'"
        class="sortable px-0"
        :class="columnHeaderClass(item)"
        scope="col"
        :style="`width: ${item.width}; min-width: ${item.width};`"
      >
        <template v-if="item.value === 'select'">
          <slot name="select">
            <v-btn
              :id="`sort-col-${id}${item.value}-btn`"
              :aria-label="`${item.text}: ${item.value === sortBy ? (sortDesc ? 'Sorted descending' : 'Sorted ascending') : 'Not sorted'}. Activate to sort ${item.value === sortBy && !sortDesc ? 'descending' : 'ascending'}.`"
              class="sort-col-btn font-weight-bold text-capitalize text-nowrap px-1"
              small
              text
              @click="onColumnHeaderClick(item.value)"
            >
              {{ item.text }}
              <v-icon class="v-data-table-header__icon" small>mdi-arrow-up</v-icon>
            </v-btn>
          </slot>
        </template>
        <template v-else>
          <v-btn
            :id="`sort-col-${id}${item.value}-btn`"
            :aria-label="`${item.text}: ${item.value === sortBy ? (sortDesc ? 'Sorted descending' : 'Sorted ascending') : 'Not sorted'}. Activate to sort ${item.value === sortBy && !sortDesc ? 'descending' : 'ascending'}.`"
            class="sort-col-btn font-weight-bold text-capitalize text-nowrap px-1"
            small
            text
            @click="onColumnHeaderClick(item.value)"
          >
            {{ item.text }}
            <v-icon class="v-data-table-header__icon" small>mdi-arrow-up</v-icon>
          </v-btn>
        </template>
      </th>
    </tr>
  </thead>
</template>

<script>
export default {
  name: 'SortableTableHeader',
  props: {
    headers: {
      type: Array,
      required: true
    },
    id: {
      default: '',
      type: String,
      required: false
    },
    onSort: {
      default: () => {},
      type: Function,
      required:false
    }
  },
  data: () => ({
    sortBy: null,
    sortDesc: false
  }),
  methods: {
    columnHeaderClass(item) {
      let klass = item.class
      if (item.value === this.sortBy) {
        klass += ` active ${this.sortDesc ? 'desc' : 'asc'}`
      }
      return klass
    },
    onColumnHeaderClick(value) {
      if (value === this.sortBy) {
        if (this.sortDesc) {
          this.sortBy = null
          this.sortDesc = false
        } else {
          this.sortDesc = true
        }
      } else {
        this.sortDesc = false
        this.sortBy = value
      }
      this.onSort(this.sortBy, this.sortDesc)
    }
  }
}
</script>

<style scoped>
.sort-col-btn {
  color: inherit !important;
  letter-spacing: normal !important;
}
.sort-col-btn:focus .v-data-table-header__icon {
  opacity: 1;
}
</style>

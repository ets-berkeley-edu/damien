<template>
  <div>
    <h2 class="pb-1">Notes</h2>
    <div v-if="item">{{ item }}</div>
  </div>
</template>

<script>
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'DepartmentNote',
  mixins: [DepartmentEditSession],
  data: () => ({
    item: undefined
  }),
  created() {
    this.item = this.note
  }
}
</script>
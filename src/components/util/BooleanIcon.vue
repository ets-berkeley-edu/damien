<template>
  <v-icon
    class="pb-1"
    :class="model ? 'success--text' : 'muted--text'"
    small
  >
    {{ model ? 'mdi-check-circle' : 'mdi-minus-circle' }}
  </v-icon>
</template>

<script>
export default {
  name: 'BooleanIcon',
  props: {
    model: {
      required: true,
      type: Boolean
    }
  }
}
</script>
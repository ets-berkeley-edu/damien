<template>
  <div :class="`evaluation-error ${color}--text text--${shade} d-flex my-1`">
    <v-icon
      small
      class="align-self-start mr-1"
      :class="`text--${shade}`"
      :color="color"
    >
      mdi-alert-circle
    </v-icon>
    <span>{{ message }}</span>
  </div>
</template>

<script>
export default {
  name: 'EvaluationError',
  props: {
    color: {
      default: 'error',
      required: false,
      type: String
    },
    message: {
      required: true,
      type: String
    },
    hover: {
      required: false,
      type: Boolean
    }
  },
  computed: {
    shade() {
      return this.$vuetify.theme.dark && !this.hover ? 'lighten-3' : 'darken-1'
    }
  }
}
</script>

<style scoped>
.evaluation-error {
  font-size: 0.9em;
  font-style: italic;
  line-height: 1.2em;
}
</style>
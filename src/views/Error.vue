<template>
  <v-banner class="pa-8">
    <v-icon
      slot="icon"
      color="warning"
      x-large
    >
      mdi-alert
    </v-icon>
    <div>
      <h2>Error</h2>
      <div
        id="error-message"
        class="pt-4"
        aria-live="polite"
        role="alert"
      >
        {{ message || 'Uh oh, there was a problem.' }}
      </div>
    </div>
  </v-banner>
</template>

<script>
export default {
  name: 'Error',
  data: () => ({
    message: undefined
  }),
  mounted() {
    this.message = this.$route.query.m
    this.$ready('Error')
  }
}
</script>
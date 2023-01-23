<template>
  <v-snackbar
    v-model="snackbarShow"
    aria-live="assertive"
    :color="snackbar.color"
    content-class="align-center"
    light
    max-width="unset"
    multi-line
    :timeout="snackbar.timeout"
    text
    :top="true"
  >
    <div class="d-flex align-center justify-space-between">
      <div
        id="alert-text"
        aria-live="polite"
        class="ml-4 mr-4 font-size-18 text-condensed"
        role="alert"
        v-html="snackbar.text"
      >
      </div>
      <div>
        <v-btn
          id="btn-close-alert"
          aria-label="Close this dialog box."
          :color="snackbar.color"
          text
          @click="snackbarClose"
          @keypress.enter.prevent="snackbarClose"
        >
          Close
        </v-btn>
      </div>
    </div>
  </v-snackbar>
</template>

<script>
import Context from '@/mixins/Context'
export default {
  name: 'Snackbar',
  mixins: [Context]
}
</script>

<template>
  <v-snackbar
    v-model="snackbarShow"
    :color="snackbar.color"
    content-class="align-center bg-white"
    location="top"
    max-width="unset"
    multi-line
    :timeout="snackbar.timeout"
    variant="tonal"
  >
    <div class="d-flex align-center justify-space-between">
      <div
        id="alert-text"
        class="font-size-18 mx-4 text-condensed"
        v-html="snackbar.text"
      />
      <div>
        <v-btn
          id="btn-close-alert"
          aria-label="Close this notification."
          :color="snackbar.color"
          text="Close"
          @click="contextStore.snackbarClose"
        />
      </div>
    </div>
  </v-snackbar>
</template>

<script setup>
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const {snackbar, snackbarShow} = storeToRefs(contextStore)
</script>

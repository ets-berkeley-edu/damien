<template>
  <v-alert
    class="evaluation-error px-1"
    density="compact"
    :role="undefined"
    :text="message"
    type="error"
    :variant="hover ? 'flat' : 'text'"
  >
    <template #prepend>
      <v-icon
        :icon="mdiAlertCircle"
        size="18"
      />
    </template>
  </v-alert>
</template>

<script setup>
import {mdiAlertCircle} from '@mdi/js'

defineProps({
  message: {
    required: true,
    type: String
  },
  hover: {
    required: false,
    type: Boolean
  }
})
</script>

<style>
.evaluation-error .v-alert__prepend {
  margin-inline-end: 4px !important;
  margin-right: 4px !important;
}
</style>

<style scoped>
.evaluation-error {
  font-size: 0.9em;
  font-style: italic;
  font-weight: 600;
  line-height: 1.3em;
  margin-left: -6px;
  max-width: 12.5rem;
  min-width: 5.8rem;
  word-break: normal;
}
</style>

<template>
  <v-footer
    id="footer"
    app
    class="footer font-size-14 bg-secondary pa-0"
    name="footer"
  >
    <div class="d-flex flex-wrap justify-space-between w-100">
      <div class="px-3 py-1">
        Problem? Question?
        <a
          id="damien-support-mailto"
          class="footer-link"
          :href="`mailto:${emailSupport}`"
          target="_blank"
        >
          Email us at {{ emailSupport }}
          <span class="sr-only"> (opens a new window)</span>
        </a>
      </div>
      <div class="ml-auto px-3 py-1">
        <span v-if="contextStore.config.isVueAppDebugMode && screenReaderAlert.message">
          {{ screenReaderAlert.message }}
        </span>
        <span v-if="!contextStore.config.isVueAppDebugMode || !screenReaderAlert.message">
          <v-icon :icon="mdiCopyright" size="small" aria-hidden="true" /><span class="sr-only">Copyright:</span> {{ new Date().getFullYear() }}
          The Regents of the University of California
        </span>
      </div>
    </div>
  </v-footer>
</template>

<script setup>
import {mdiCopyright} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const emailSupport = contextStore.config.emailSupport
const screenReaderAlert = contextStore.screenReaderAlert
</script>

<style scoped>
.footer {
  left: calc(var(--v-layout-left) + 8px) !important;
  width: calc(100vw - calc(var(--v-layout-left) + 8px)) !important;
}

.footer-link {
  color: rgb(var(--v-theme-on-secondary));
  text-decoration: underline;
}
</style>

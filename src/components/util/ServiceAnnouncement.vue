<template>
  <div id="service-announcement" aria-live="polite" class="service-announcement">
    <v-banner
      v-if="contextStore.serviceAnnouncement && contextStore.serviceAnnouncement.isLive && route.path !== '/404'"
      class="service-announcement-content"
    >
      <h2 class="sr-only">Course Evaluations Annoucement.</h2>
      <pre>
        <span
          id="service-announcement"
          v-linkified
          v-html="contextStore.serviceAnnouncement.text"
        />
      </pre>
    </v-banner>
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import {useRoute} from 'vue-router'
import {getServiceAnnouncement} from '@/api/config'
import {useContextStore} from '@/stores/context'

const route = useRoute()

const contextStore = useContextStore()

onMounted(() => {
  getServiceAnnouncement().then(data => {
    contextStore.setServiceAnnouncement(data)
  })
})
</script>

<style>
.service-announcement a {
  color: rgb(var(--v-theme-primary)) !important;
}
</style>

<style scoped>
.service-announcement {
  margin: 0;
  position: sticky;
  top: var(--v-layout-top);
  width: 100%;
  z-index: 2;
}
.service-announcement-content {
  background-image: linear-gradient(
    rgba(var(--v-theme-alert), 0.2),
    rgba(var(--v-theme-alert), 0.2)) !important;
  border: solid max(1px, 0.06rem) rgba(var(--v-theme-alert), 0.4);
  border-left: 0;
  border-right: 0;
  padding: 8px 20px;
}
pre {
  font-size: 15px !important;
  white-space: pre-line;
}
</style>

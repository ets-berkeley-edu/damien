<template>
  <div>
    <div
      id="screen-reader-alert"
      class="sr-only"
      :aria-live="contextStore.screenReaderAlert.politeness"
    >
      {{ contextStore.screenReaderAlert.message }}
    </div>
    <router-view />
  </div>
</template>

<script setup>
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
</script>

<style>
  @import 'v-calendar/style.css';
  @import '@/assets/styles/vcalendar-custom.css';
  @import '@/assets/styles/vuetify-overrides.css';
  @import '@/assets/styles/damien-global.css';
</style>

<template>
  <div>
    <span
      v-if="screenReaderAlert"
      id="screen-reader-alert"
      class="sr-only"
      aria-live="polite"
      role="alert"
    >
      {{ screenReaderAlert }}
    </span>
    <router-view />
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'App',
  mixins: [Context]
}
</script>

<style>
  @import './assets/styles/damien-global.css';
</style>
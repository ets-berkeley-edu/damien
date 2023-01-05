<template>
  <v-footer
    id="footer"
    app
    class="footer"
    color="secondary darken-1"
    dark
  >
    <v-container fluid class="pa-1">
      <v-row no-gutters justify="space-between">
        <v-col aria-label="Feedback">
          Problem? Question?
          <a
            id="damien-support-mailto"
            class="white--text"
            :href="`mailto:${$config.emailSupport}`"
            target="_blank"
          >
            Email us at {{ $config.emailSupport }}
            <span class="sr-only"> (opens a new window)</span>
          </a>
        </v-col>
        <v-col>
          <div class="float-right">
            <span v-if="$config.isVueAppDebugMode && screenReaderAlert">
              {{ screenReaderAlert }}
            </span>
            <span v-if="!$config.isVueAppDebugMode || !screenReaderAlert">
              <v-icon small>mdi-copyright</v-icon> {{ new Date().getFullYear() }}
              The Regents of the University of California
            </span>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script>
  import Context from '@/mixins/Context'
  export default {
    name: 'Footer',
    mixins: [Context]
  }
</script>

<style scoped>
.footer {
  z-index: 205;
}
</style>

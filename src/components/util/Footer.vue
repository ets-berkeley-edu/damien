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
        <v-col>
          Problem? Question? Email us at
          <a
            id="damien-support-mailto"
            aria-label="Open new window to send email"
            class="white--text"
            :href="`mailto:${$config.emailSupport}`"
            target="_blank"
          >
            {{ $config.emailSupport }}
          </a>
        </v-col>
        <v-col>
          <div class="float-right">
            <v-icon small>mdi-copyright</v-icon> {{ new Date().getFullYear() }}
            The Regents of the University of California
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
  z-index: 10;
}
</style>
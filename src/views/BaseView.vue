<template>
  <v-app :style="{background: this.$vuetify.theme.dark ? this.$vuetify.theme.themes.dark.background : this.$vuetify.theme.themes.light.background}">
    <v-navigation-drawer
      app
      permanent
      color="secondary"
      :expand-on-hover="true"
      :mini-variant="true"
      :clipped="$vuetify.breakpoint.lgAndUp"
      :right="false"
      dark
    >
      <v-list nav>
        <v-list-item
          v-for="(item, index) in navItems"
          :id="`sidebar-link-${item.title}`"
          :key="index"
          class="primary-contrast--text"
          link
          @click="toRoute(item.path)"
        >
          <v-list-item-icon>
            <component :is="item.icon" />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item class="primary-contrast--text" @click="$vuetify.theme.dark = !$vuetify.theme.dark">
          <v-list-item-icon>
            <DarkModeIcon />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ $vuetify.theme.dark ? 'Light' : 'Dark' }} mode</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar
      app
      :clipped-left="$vuetify.breakpoint.lgAndUp"
      color="primary"
      dark
    >
      <div class="display-1">
        Course Evaluation
        <a
          id="skip-to-content-link"
          href="#content"
          class="sr-only sr-only-focusable"
          tabindex="0"
        >
          Skip to main content
        </a>
      </div>
      <v-spacer class="d-flex justify-center">
        <v-chip
          v-if="$config.isVueAppDebugMode && screenReaderAlert"
          id="screen-reader-alert-debug"
          class="sr-debug font-italic"
          color="primary-contrast"
          outlined
        >
          {{ screenReaderAlert }}
        </v-chip>
      </v-spacer>
      <v-menu offset-y rounded="lg">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            id="btn-main-menu"
            v-bind="attrs"
            color="primary"
            dark
            v-on="on"
          >
            {{ $currentUser.firstName }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item id="menu-item-log-out" link @click="logOut">
            <v-list-item-content>Log Out</v-list-item-content>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-main id="content" class="ma-3">
      <Spinner v-if="loading" />
      <router-view :key="stripAnchorRef($route.fullPath)" class="px-4"></router-view>
    </v-main>
    <Footer />
  </v-app>
</template>

<script>
  import Context from '@/mixins/Context'
  import DarkModeIcon from '../assets/lightbulb-outline.svg'
  import ErrorIcon from '../assets/exclamation-circle-solid.svg'
  import Footer from '@/components/util/Footer'
  import GroupIcon from '../assets/account-group.svg'
  import ListIcon from '../assets/playlist-edit.svg'
  import Spinner from '@/components/util/Spinner'
  import StatusIcon from '../assets/list-status.svg'
  import Util from '@/mixins/Util'
  import {getCasLogoutUrl} from '@/api/auth'
  export default {
    name: 'BaseView',
    components: {DarkModeIcon, ErrorIcon, Footer, GroupIcon, ListIcon, Spinner, StatusIcon},
    mixins: [Context, Util],
    data: () => ({
      navItems: undefined,
    }),
    created() {
      this.prefersColorScheme()
      this.navItems = [
        { title: 'Status Board', icon: StatusIcon, path: '/status' },
        { title: 'Course Errors Board', icon: ErrorIcon, path: '/errors' },
        { title: 'Group Management', icon: GroupIcon, path: '/departments' },
        { title: 'List Management', icon: ListIcon, path: '/lists' }
      ]
    },
    methods: {
      logOut() {
        this.alertScreenReader('Logging out')
        getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
      },
      prefersColorScheme() {
        const mq = window.matchMedia('(prefers-color-scheme: dark)')
        this.$vuetify.theme.dark = mq.matches
        if (typeof mq.addEventListener === 'function') {
          mq.addEventListener('change', e => this.$vuetify.theme.dark = e.matches)
        }
      },
      toRoute(path) {
        this.$router.push({ path }, this.$_.noop)
      }
    }
  }
</script>

<style scoped>
.sr-debug {
  width: fit-content;
}
</style>
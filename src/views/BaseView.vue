<template>
  <v-app>
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
          link
          @click="toRoute(item.path)"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item @click="$vuetify.theme.dark = !$vuetify.theme.dark">
          <v-list-item-icon>
            <v-icon>mdi-lightbulb-outline</v-icon>
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
      <v-spacer></v-spacer>
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
      <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
    </v-main>
    <Footer />
  </v-app>
</template>

<script>
  import Context from '@/mixins/Context'
  import Footer from '@/components/util/Footer'
  import Spinner from '@/components/util/Spinner'
  import Util from '@/mixins/Util'
  import {getCasLogoutUrl} from '@/api/auth'
  export default {
    name: 'BaseView',
    components: {Footer, Spinner},
    mixins: [Context, Util],
    data: () => ({
      navItems: undefined,
    }),
    created() {
      this.prefersColorScheme()
      this.navItems = [{ title: 'Home', icon: 'mdi-home', path: '/home' }]
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
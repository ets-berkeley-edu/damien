<template>
  <a
    id="skip-to-content-link"
    :aria-hidden="contextStore.isModalOpen"
    href="#content"
    class="sr-only sr-only-focusable"
    tabindex="0"
  >
    Skip to main content
  </a>
  <v-layout ref="layout" :aria-hidden="contextStore.isModalOpen">
    <v-app-bar
      id="app-bar"
      app
      class="topbar"
      clipped-left
      color="topbar"
    >
      <router-link class="home-link my-1 mx-2 py-1 px-2 on-topbar text-truncate" :to="`/`">
        <div class="text-h4 text-no-wrap cursor-pointer text-truncate">
          Course Evaluations
        </div>
      </router-link>
      <div v-if="contextStore.config.isVueAppDebugMode && get(contextStore.screenReaderAlert, 'message')" class="mx-auto">
        <span v-if="contextStore.screenReaderAlert.politeness === 'assertive'">ALERT: </span> {{ contextStore.screenReaderAlert.message }}
      </div>
      <div class="ml-auto pr-4">
        <v-menu eager offset-y rounded="lg">
          <template #activator="{props: menuProps}">
            <v-btn
              id="btn-main-menu"
              :aria-label="`User profile for ${currentUser.firstName}`"
              min-width="2rem !important"
              variant="outlined"
              v-bind="menuProps"
            >
              <span class="d-none d-sm-block">{{ currentUser.firstName }}</span>
              <span class="d-block d-sm-none">{{ first(currentUser.firstName) }}</span>
            </v-btn>
          </template>
          <v-list density="comfortable">
            <v-list-item
              id="dark-mode-toggle"
              link
              role="option"
              @click="toggleColorScheme"
            >
              <v-list-item-title class="font-weight-medium">
                {{ theme.global.current.value.dark ? 'Light' : 'Dark' }} mode
              </v-list-item-title>
            </v-list-item>
            <v-list-item
              id="menu-item-log-out"
              :append-icon="mdiLogout"
              link
              role="option"
              @click="logOut"
            >
              <v-list-item-title class="font-weight-medium">Log Out</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </v-app-bar>
    <v-navigation-drawer
      v-if="currentUser.isAdmin"
      id="nav-drawer"
      aria-labelledby="nav-header"
      class="font-size-14"
      color="tertiary"
      permanent
      :rail="isSidebarCollapsed"
      role="navigation"
      :scrim="false"
      style="height: calc(100% - max(64px, 2.75rem)); top: max(64px, 2.75rem);"
      tag="nav"
    >
      <template #prepend>
        <h2 id="nav-header" class="sr-only" tabindex="-1">Main Menu</h2>
      </template>
      <template #append>
        <div class="d-flex justify-end pa-2">
          <v-btn
            id="sidebar-toggle-btn"
            aria-controls="nav-drawer"
            :aria-expanded="!isSidebarCollapsed"
            :aria-label="`${isSidebarCollapsed ? 'expand' : 'collapse'} navigation`"
            class="font-size-16 nav-item px-0"
            color="on-tertiary"
            min-height="2.5rem"
            min-width="2.5rem !important"
            variant="tonal"
            @click="toggleSidebarCollapsed"
          >
            <v-icon
              :icon="isSidebarCollapsed ? mdiArrowExpandRight : mdiArrowCollapseLeft"
              size="x-large"
              aria-hidden="true"
            />
          </v-btn>
        </div>
      </template>
      <v-list-item
        v-for="(item, index) in navItems"
        :id="`sidebar-link-${item.id}`"
        :key="index"
        :active="startsWith(route.path, item.path)"
        active-class="active"
        :aria-current="startsWith(route.path, item.path) ? 'page' : null"
        class="font-size-16 nav-item nav-link"
        base-color="tertiary"
        link
        role="link"
        variant="flat"
        @click="toRoute(item.path)"
      >
        <div class="align-center d-flex">
          <v-icon
            :class="startsWith(route.path, item.path) ? 'text-white' : 'text-on-tertiary'"
            :icon="item.icon"
            size="x-large"
            aria-hidden="true"
          />
          <div
            class="nav-drawer-item-label text-no-wrap"
            :class="startsWith(route.path, item.path) ? 'font-weight-bold text-white' : 'font-weight-medium text-on-tertiary'"
          >
            {{ item.title }}
          </div>
        </div>
      </v-list-item>
    </v-navigation-drawer>
    <v-main
      id="content"
      class="mb-4"
      :style="`--v-layout-bottom: ${footerHeight}px; --v-layout-top: max(64px, 2.75rem); --v-layout-left: ${layoutLeft}`"
    >
      <Snackbar />
      <Spinner v-if="contextStore.loading" />
      <ServiceAnnouncement />
      <router-view :key="stripAnchorRef(route.fullPath)" class="page-margins mx-xl-6" />
    </v-main>
    <DamienFooter :style="`--v-layout-left: ${layoutLeft}`" />
  </v-layout>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {first, get, startsWith} from 'lodash'
import {
  mdiAccountGroup,
  mdiAlertCircle,
  mdiArrowCollapseLeft,
  mdiArrowExpandRight,
  mdiListStatus,
  mdiLogout,
  mdiPlaylistEdit
} from '@mdi/js'
import {useTheme} from 'vuetify'
import {useRoute, useRouter} from 'vue-router'
import DamienFooter from '@/components/util/DamienFooter'
import ServiceAnnouncement from '@/components/util/ServiceAnnouncement'
import Snackbar from '@/components/util/Snackbar'
import Spinner from '@/components/util/Spinner'
import {alertScreenReader, putFocusNextTick, stripAnchorRef} from '@/lib/utils'
import {getCasLogoutUrl} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isSidebarCollapsed = ref(false)
const layout = ref()
const navItems = ref([])
const route = useRoute()
const router = useRouter()
const theme = useTheme()

const footerHeight = computed(() => {
  const footer = layout.value ? layout.value.getLayoutItem('footer') : null
  return get(footer, 'size', 60)
})

const layoutLeft = computed(() => {
  if (currentUser.isAdmin) {
    return isSidebarCollapsed.value ? '3rem' : '11.5rem'
  } else {
    return '0px'
  }
})

onMounted(() => {
  setPreferredColorScheme()
  setPreferredSidebarState()
  if (currentUser.isAdmin) {
    navItems.value = [
      {id: 'status', title: 'Status', icon: mdiListStatus, path: '/status'},
      {id: 'publish', title: 'Publish', icon: mdiAlertCircle, path: '/publish'},
      {id: 'departments', title: 'Departments', icon: mdiAccountGroup, path: '/departments'},
      {id: 'settings', title: 'Settings', icon: mdiPlaylistEdit, path: '/lists'}
    ]
  }
})

const logOut = () => {
  alertScreenReader('Logging out')
  getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
}

const setPreferredColorScheme = () => {
  let prefersDarkMode
  if (window.localStorage.getItem('prefersDarkMode')) {
    prefersDarkMode = window.localStorage.getItem('prefersDarkMode') === 'true'
  } else {
    prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  theme.change(prefersDarkMode ? 'dark' : 'light')
}

const setPreferredSidebarState = () => {
  if (window.localStorage.getItem('prefersSidebarCollapsed')) {
    isSidebarCollapsed.value = window.localStorage.getItem('prefersSidebarCollapsed') === 'true'
  }
}

const toggleColorScheme = () => {
  const getDark = !theme.global.current.value.dark
  theme.change(getDark ? 'dark' : 'light')
  window.localStorage.setItem('prefersDarkMode', `${getDark}`)
  putFocusNextTick('btn-main-menu')
}

const toggleSidebarCollapsed = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  window.localStorage.setItem('prefersSidebarCollapsed', isSidebarCollapsed.value)
}

const toRoute = path => router.push({path})

</script>

<style>
@supports not selector(:focus-visible) {
  .home-link:focus {
    background-color: rgba(var(--v-theme-on-topbar), var(--v-focus-opacity));
    box-shadow: 0 0 0 0.125rem white !important;
    outline-color: rgba(var(--v-theme-topbar)) !important;
  }
  .nav-item:focus::after {
    box-shadow: inset 0 0 0 0.125rem white !important;
    outline: none !important;
  }
}
.home-link:focus-visible {
  background-color: rgba(var(--v-theme-on-topbar), var(--v-focus-opacity));
  box-shadow: 0 0 0 0.125rem white !important;
  outline-color: rgba(var(--v-theme-topbar)) !important;
}
.home-link:hover {
  opacity: var(--v-high-emphasis-opacity);
  text-decoration: none;
}
.nav-drawer-item-label {
  letter-spacing: 0.1em;
  margin-left: 0.5rem;
}
.nav-item:focus-visible::after {
  box-shadow: inset 0 0 0 0.125rem white !important;
  outline: none !important;
}
.nav-item.active,
.nav-item:focus,
.nav-item:focus-visible {
  color: white !important;
}
.nav-item.nav-link {
  padding: 16px calc(0.5rem + 4px);
}
.sr-only-focusable:active, .sr-only-focusable:focus {
  background-color: color-mix(in srgb, rgb(var(--v-theme-topbar)) 80%, white 20%);
  box-shadow: inset 0 0 0 0.125rem white !important;
  color: white;
  height: auto !important;
  left: 0 !important;
  outline: none !important;
  padding: 10px;
  white-space: normal;
  width: auto !important;
  z-index: 2000;
}
.topbar {
  width: 100vw !important;
  .v-toolbar__content {
    height: max(64px, 2.75rem) !important;
  }
}
</style>

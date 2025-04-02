<template>
  <a
    id="skip-to-content-link"
    :aria-hidden="contextStore.isModalOpen"
    href="#content"
    class="sr-only"
    tabindex="0"
  >
    Skip to main content
  </a>
  <v-layout ref="layout" :aria-hidden="contextStore.isModalOpen">
    <v-app-bar
      app
      clipped-left
      color="topbar"
    >
      <router-link class="home-link ml-2 px-1 on-topbar" :to="`/`">
        <div class="text-h4 text-no-wrap cursor-pointer">
          Course Evaluations
        </div>
      </router-link>
      <div v-if="contextStore.config.isVueAppDebugMode && get(contextStore.screenReaderAlert, 'message')" class="mx-auto">
        <span v-if="contextStore.screenReaderAlert.politeness === 'assertive'">ALERT: </span> {{ contextStore.screenReaderAlert.message }}
      </div>
      <div class="ml-auto pr-4">
        <v-menu offset-y rounded="lg">
          <template #activator="{props: menuProps}">
            <v-btn
              id="btn-main-menu"
              variant="outlined"
              v-bind="menuProps"
            >
              <span class="sr-only">User profile for </span>{{ currentUser.firstName }}
            </v-btn>
          </template>
          <v-list density="comfortable">
            <v-list-item
              id="dark-mode-toggle"
              link
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
      :rail-width="navDrawerRailWidth"
      role="navigation"
      :scrim="false"
      tag="nav"
      width="13.75rem"
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
            min-width="2.5rem"
            variant="tonal"
            @click="toggleSidebarCollapsed"
          >
            <v-icon :icon="isSidebarCollapsed ? mdiArrowExpandRight : mdiArrowCollapseLeft" size="x-large" />
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
        class="font-size-16 nav-item"
        :class="{
          'py-4 px-3': isSidebarCollapsed,
          'pa-4': !isSidebarCollapsed
        }"
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
            :title="isSidebarCollapsed ? item.title : undefined"
          />
          <div
            class="font-weight-medium text-on-tertiary ml-4 nav-drawer-letter-spacing text-no-wrap"
            :class="{
              'font-weight-bold text-white': startsWith(route.path, item.path),
              'sr-only': isSidebarCollapsed}"
          >
            {{ item.title }}
          </div>
        </div>
      </v-list-item>
    </v-navigation-drawer>
    <v-main id="content" class="mb-4" :style="`--v-layout-bottom: ${footerHeight}px; --v-layout-left: ${navDrawerRailWidth}px`">
      <Snackbar />
      <Spinner v-if="contextStore.loading" />
      <ServiceAnnouncement />
      <router-view :key="stripAnchorRef(route.fullPath)" class="px-4" />
    </v-main>
    <DamienFooter />
  </v-layout>
</template>

<script setup>
import DamienFooter from '@/components/util/DamienFooter'
import ServiceAnnouncement from '@/components/util/ServiceAnnouncement'
import Snackbar from '@/components/util/Snackbar'
import Spinner from '@/components/util/Spinner'
import {alertScreenReader, stripAnchorRef} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {get, startsWith} from 'lodash'
import {getCasLogoutUrl} from '@/api/auth'
import {
  mdiAccountGroup,
  mdiAlertCircle,
  mdiArrowCollapseLeft,
  mdiArrowExpandRight,
  mdiListStatus,
  mdiLogout,
  mdiPlaylistEdit
} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useTheme} from 'vuetify'
import {useRoute, useRouter} from 'vue-router'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const fontSize = ref('16px')
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
const navDrawerRailWidth = computed(() => {
  const fontSizeNum = parseInt(fontSize.value.replace('px', ''))
  return (56 * fontSizeNum / 16) - (fontSizeNum - 16)
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
  const setFontSize = () => {
    if (layout.value) {
      const computedFontSize = getComputedStyle(layout.value.$el).fontSize
      if (computedFontSize && computedFontSize !== fontSize.value) {
        fontSize.value = computedFontSize
      }
    }
    requestAnimationFrame(setFontSize)
  }
  requestAnimationFrame(setFontSize)
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
  theme.global.name.value = prefersDarkMode ? 'dark' : 'light'
}

const setPreferredSidebarState = () => {
  if (window.localStorage.getItem('prefersSidebarCollapsed')) {
    isSidebarCollapsed.value = window.localStorage.getItem('prefersSidebarCollapsed') === 'true'
  }
}

const toggleColorScheme = () => {
  const getDark = !theme.global.current.value.dark
  theme.global.name.value = getDark ? 'dark' : 'light'
  window.localStorage.setItem('prefersDarkMode', `${getDark}`)
}

const toggleSidebarCollapsed = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  window.localStorage.setItem('prefersSidebarCollapsed', isSidebarCollapsed.value)
}

const toRoute = path => router.push({path})

</script>

<style scoped>
.home-link {
  border: 2px solid transparent;
}
.home-link:focus, .home-link:focus-visible {
  background-color: rgba(var(--v-theme-on-topbar), var(--v-focus-opacity));
  border-color: rgba(var(--v-theme-on-topbar), var(--v-focus-opacity));
  border-radius: 4px;
  border-style: solid;
  border-width: 2px;
  outline: none;
}
.home-link:hover {
  opacity: var(--v-high-emphasis-opacity);
  text-decoration: none;
}
.nav-drawer-letter-spacing {
  letter-spacing: 0.1em;
}
</style>

<style>
.nav-item.v-list-item.active,
.nav-item.v-list-item:focus,
.nav-item.v-list-item:focus-visible {
  color: white !important;
}
.nav-item.v-list-item.active > .v-list-item__overlay,
.nav-item.v-list-item:focus > .v-list-item__overlay,
.nav-item.v-list-item:focus-visible > .v-list-item__overlay {
  opacity: calc(var(--v-focus-opacity)) !important;
}
</style>

<template>
  <div class="background-fade d-flex justify-space-around" :class="{'sidebar-offset': get(contextStore, 'currentUser.isAdmin')}">
    <v-card flat class="foreground">
      <span
        aria-live="polite"
        role="alert"
      ><span class="sr-only">Sorry, page not found. Contact us if the system is misbehaving.</span></span>
      <v-img
        alt="404 Page Not Found, with superimposed quote: 'It is the greatest mystery of all because no human being will ever solve it."
        src="@/assets/404_page_foreground_text.png"
      />
    </v-card>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {onMounted} from 'vue'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()

onMounted(() => {
  useContextStore().loadingComplete('Page not found')
})
</script>

<style scoped>
.background-fade {
  background: url('@/assets/background_fade.png') no-repeat center center;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  height: 100%;
  padding: 0px !important;
  position: fixed;
  top: 60px;
  max-width: unset;
  overflow-y: scroll;
  width: 100vw;
}
.foreground {
  background: transparent;
  max-height: 75%;
  max-width: 1200px;
  width: 90%;
}
.sidebar-offset {
  left: 26px;
}
</style>

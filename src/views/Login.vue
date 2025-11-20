<template>
  <v-app class="background-lecture-hall">
    <Snackbar />
    <v-main class="align-center d-flex flex-column h-100">
      <div class="my-auto">
        <v-slide-y-transition>
          <v-card v-show="showCard" class="accent-border frosted mx-auto pb-9 pt-6 px-10" variant="outlined">
            <v-card-text class="text-center">
              <h1 id="page-title" class="text-accent">
                <strong>Welcome to Course Evaluations</strong>
                {{ config.currentTermName }}
              </h1>
            </v-card-text>
            <v-card-actions class="d-flex flex-column">
              <v-btn
                id="log-in"
                aria-label="Log in to Course Evaluations. (You will be sent to CalNet login page.)"
                class="w-100"
                color="accent"
                size="large"
                variant="flat"
                @click.stop="logIn"
              >
                Sign In
                <div class="pl-2">
                  <v-icon :icon="mdiArrowRightCircleOutline" />
                </div>
              </v-btn>
              <DevAuth v-if="config.devAuthEnabled" class="mb-2 mt-8" />
            </v-card-actions>
          </v-card>
        </v-slide-y-transition>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import {mdiArrowRightCircleOutline} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import DevAuth from '@/components/admin/DevAuth'
import Snackbar from '@/components/util/Snackbar'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getCasLoginURL} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const config = contextStore.config
const route = useRoute()
const showCard = ref(false)

onMounted(() => {
  setTimeout(
    () => {
      showCard.value = true
      alertScreenReader('Page not found')
      putFocusNextTick(config.devAuthEnabled ? 'dev-auth-uid' : 'page-title')
    },
    100
  )
  putFocusNextTick('page-title')
  const error = route.query.error
  if (error) {
    contextStore.snackbarReportError(error)
  } else {
    alertScreenReader(`Welcome to Course Evaluations - ${config.currentTermName}. Please log in.`)
  }
})

const logIn = () => getCasLoginURL().then(data => window.location.href = data.casLoginUrl)
</script>

<style scoped>
.accent-border {
  border: 1px solid #F04A00 !important;
}
.background-lecture-hall {
  background: url('@/assets/lecture_hall_background.jpg') no-repeat center center fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.frosted {
  background-color: rgba(255, 255, 255, 0.8) !important;
}
h1 strong {
  display: block;
  font-size: 65%;
}
</style>

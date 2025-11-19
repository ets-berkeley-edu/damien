<template>
  <v-form class="dev-auth" @submit.prevent="logIn">
    <div class="mt-3">
      <v-text-field
        id="dev-auth-uid"
        v-model="uid"
        :aria-describedby="undefined"
        autocomplete="off"
        bg-color="surface"
        density="comfortable"
        flat
        hide-details
        light
        placeholder="UID"
        :rules="[v => !!v || 'Required']"
        variant="outlined"
        @keyup.enter="logIn"
      />
    </div>
    <div class="mt-3">
      <v-text-field
        id="dev-auth-password"
        v-model="password"
        :aria-describedby="undefined"
        autocomplete="off"
        bg-color="surface"
        density="comfortable"
        flat
        hide-details
        light
        placeholder="Password"
        :rules="[v => !!v || 'Required']"
        type="password"
        variant="outlined"
        @keyup.enter="logIn"
      />
    </div>
    <div class="mt-3">
      <v-btn
        id="btn-dev-auth-login"
        block
        color="secondary"
        :disabled="!uid || !password"
        :style="!uid || !password ? {background: `${themes.light.secondary} !important`, color: '#FFF !important'} : {}"
        variant="flat"
        @click="logIn"
      >
        Dev Auth
        <img alt="Damien, the son of the Devil" src="@/assets/damien.svg" class="ml-2 damien-icon">
      </v-btn>
    </div>
  </v-form>
</template>

<script setup>
import {devAuthLogIn} from '@/api/auth'
import {putFocusNextTick} from '@/lib/utils'
import {ref} from 'vue'
import {trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useTheme} from 'vuetify'
import {useRoute, useRouter} from 'vue-router'

const contextStore = useContextStore()
const uid = ref(undefined)
const password = ref(undefined)
const route = useRoute()
const router = useRouter()
const themes = useTheme().themes.value

const logIn = () => {
  const credentials = {
    uid: trim(uid.value),
    password: trim(password.value)
  }
  if (credentials.uid && credentials.password) {
    devAuthLogIn(credentials.uid, credentials.password).then(user => {
      if (user.isAuthenticated) {
        const redirect = route.query.redirect
        router.push({path: redirect || '/start'})
      } else {
        contextStore.snackbarReportError('Sorry, user is not authorized to use Course Evaluations.')
        putFocusNextTick('dev-auth-uid')
      }
    })
  } else if (credentials.uid) {
    contextStore.snackbarReportError('Password required')
    putFocusNextTick('dev-auth-password')
  } else {
    contextStore.snackbarReportError('Both UID and password are required')
    putFocusNextTick('dev-auth-uid')
  }
}
</script>

<style scoped>
.damien-icon {
  height: 20px;
  width: 20px;
}
.dev-auth {
  width: 100%;
}
</style>

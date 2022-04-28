<template>
  <v-form class="mb-4 dev-auth" @submit.prevent="logIn">
    <div class="my-8" color="secondary">
      <v-divider />
    </div>
    <v-text-field
      id="dev-auth-uid"
      v-model="uid"
      flat
      light
      outlined
      solo
      placeholder="UID"
      :rules="[v => !!v || 'Required']"
      @keyup.enter="logIn"
    ></v-text-field>
    <v-text-field
      id="dev-auth-password"
      v-model="password"
      flat
      light
      outlined
      solo
      placeholder="Password"
      :rules="[v => !!v || 'Required']"
      type="password"
      @keyup.enter="logIn"
    ></v-text-field>
    <v-btn
      id="btn-dev-auth-login"
      block
      :style="!uid || !password ? {background: `${$vuetify.theme.themes.light.secondary} !important`, color: '#FFF !important'} : {}"
      class="secondary"
      :disabled="!uid || !password"
      large
      @click="logIn"
      @keypress.enter.prevent="logIn"
    >
      Dev Auth
      <Damien class="ml-2 damien-icon" />
    </v-btn>
  </v-form>
</template>

<script>
import Context from '@/mixins/Context'
import {devAuthLogIn} from '@/api/auth'
import Damien from '../../assets/damien.svg'

export default {
  name: 'DevAuth',
  mixins: [Context],
  components: {
    Damien
  },
  data: () => ({
    uid: null,
    password: null
  }),
  methods: {
    logIn() {
      let uid = this.$_.trim(this.uid)
      let password = this.$_.trim(this.password)
      if (uid && password) {
        devAuthLogIn(uid, password).then(user => {
          if (user.isAuthenticated) {
            const redirect = this.$_.get(this.$router, 'currentRoute.query.redirect')
            this.$router.push({path: redirect || '/'}, this.$_.noop)
          } else {
            this.reportError('Sorry, user is not authorized to use Course Evaluations.')
          }
        })
      } else if (uid) {
        this.reportError('Password required')
        this.$putFocusNextTick('dev-auth-password')
      } else {
        this.reportError('Both UID and password are required')
        this.$putFocusNextTick('dev-auth-uid')
      }
    }
  }
}
</script>

<style scoped>
.damien-icon {
  height: 20px;
  width: 20px;
}
.damien-icon .cls-1 {
  fill: transparent;
}
.damien-icon .cls-2 {
  fill: currentColor;
}
.dev-auth {
  width: 100%;
}
</style>

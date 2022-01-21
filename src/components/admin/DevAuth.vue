<template>
  <v-form class="mb-4 dev-auth" @submit.prevent="logIn">
    <div class="my-8" color="secondary">
      <v-divider />
    </div>
    <v-text-field
      id="dev-auth-uid"
      v-model="uid"
      background-color="white"
      outlined
      placeholder="UID"
      :rules="[v => !!v || 'Required']"
    ></v-text-field>
    <v-text-field
      id="dev-auth-password"
      v-model="password"
      background-color="white"
      outlined
      placeholder="Password"
      :rules="[v => !!v || 'Required']"
      type="password"
    ></v-text-field>
    <v-btn
      id="btn-dev-auth-login"
      block
      :color="!uid || !password ? 'secondary lighten-1' : 'secondary'"
      dark
      large
      @click="logIn"
    >
      Dev Auth
      <Damien class="ml-2 damien-icon" />
    </v-btn>
  </v-form>
</template>

<script>
import {devAuthLogIn} from '@/api/auth'
import Damien from '../../assets/damien.svg'

export default {
  name: 'DevAuth',
  components: {
    Damien
  },
  props: {
    reportError: {
      required: true,
      type: Function
    }
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
            this.reportError('Sorry, user is not authorized to use Damien.')
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

<template>
  <form @submit.prevent="logIn">
    <div class="d-flex dev-auth">
      <div>
        <input
          id="dev-auth-uid"
          v-model="uid"
          placeholder="UID"
          type="text"
          aria-required="true"
          aria-label="Input UID of an authorized user"
          size="8"
        >
      </div>
      <div class="ml-1">
        <input
          id="dev-auth-password"
          v-model="password"
          :aria-invalid="!!password"
          placeholder="Password"
          type="password"
          aria-required="true"
          aria-label="Password"
          autocomplete="off"
          size="8"
        >
      </div>
      <div class="ml-1">
        <v-btn
          id="dev-auth-submit"
          color="secondary"
          @click="logIn"
        >
          DevAuth!
        </v-btn>
      </div>
    </div>
  </form>
</template>

<script>
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'DevAuth',
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
.dev-auth {
  justify-content: center;
  padding-top: 10px;
  white-space: nowrap;
}
</style>

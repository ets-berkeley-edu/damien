<template>
  <v-app>
    <v-main>
      <v-container class="background-lecture-hall" fluid>
        <v-card
          class="mx-auto"
          elevation="24"
          max-width="400"
        >
          <v-system-bar class="accent--text pa-8" color="secondary">
            <div>
              <h1>Welcome to Course Evaluation</h1>
            </div>
          </v-system-bar>
          <DevAuth v-if="$config.devAuthEnabled" :report-error="reportError" />
        </v-card>
        <div class="copyright" role="contentinfo">
          <span>&copy; 2021 The Regents of the University of California</span>
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import DevAuth from '@/components/admin/DevAuth'

export default {
  name: 'Login',
  components: {
    DevAuth
  },
  data: () => ({
    error: undefined,
    showError: false
  }),
  created() {
    this.reportError(this.$route.query.error)
  },
  methods: {
    // logIn() {
    //   getCasLoginURL().then(data => window.location.href = data.casLoginUrl)
    // },
    onHidden() {
      this.error = null
      this.showError = false
    },
    reportError(error) {
      error = this.$_.trim(error)
      if (error.length) {
        this.error = error
        this.showError = true
      }
    }
  }
}
</script>

<style scoped>
.background-lecture-hall {
  background: url('~@/assets/lecture_hall_background.jpg') no-repeat center;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.copyright {
  height: 40px;
  width: 320px;
  padding-top: 10px;
  text-align: center;
  white-space: nowrap;
}
</style>

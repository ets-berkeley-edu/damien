<template>
  <v-app>
    <v-container class="background-lecture-hall" fill-height fluid>
      <v-main>
        <v-card
          class="mx-auto px-8 py-6 semi-transparent accent-border accent--text"
          max-width="600"
          outlined
        >
          <div class="text-center">
            <h1>
              <strong>Welcome to Course Evaluation</strong>
              Spring 2022
            </h1>
          </div>
          <v-card-actions class="px-16 pt-12 d-flex flex-column">
            <v-btn
              id="log-in"
              aria-label="Log in to Course Evaluation. (You will be sent to CalNet login page.)"
              block
              color="accent"
              large
            >
              Sign In
              <v-icon class="pl-2">mdi-arrow-right-circle-outline</v-icon>
            </v-btn>
            <DevAuth v-if="$config.devAuthEnabled" :report-error="reportError" />
          </v-card-actions>
        </v-card>
      </v-main>
    </v-container>
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
.accent-border {
  border: 1px solid #F04A00 !important;
}
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
h1 strong {
  display: block;
  font-size: 65%;
}
.semi-transparent {
  background-color: rgba(255, 255, 255, 0.8) !important;
}
</style>

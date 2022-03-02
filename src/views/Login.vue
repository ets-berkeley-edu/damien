<template>
  <v-app>
    <v-snackbar
      v-model="snackbarShow"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      content-class="align-center"
      :top="true"
    >
      <div class="d-flex align-center justify-space-between">
        <div
          id="alert-text"
          aria-live="polite"
          class="ml-4 mr-4 title"
          role="alert"
        >
          {{ snackbar.text }}
        </div>
        <div>
          <v-btn
            id="btn-close-alert"
            aria-label="Close this dialog box."
            text
            @click="snackbarClose"
          >
            Close
          </v-btn>
        </div>
      </div>
    </v-snackbar>
    <v-container class="background-lecture-hall" fill-height fluid>
      <v-main>
        <v-card
          class="mx-auto px-8 py-6 frosted accent-border accent--text"
          max-width="600"
          outlined
        >
          <div class="text-center">
            <h1 id="page-title">
              <strong>Welcome to Course Evaluation</strong>
              {{ currentTermName }}
            </h1>
          </div>
          <v-card-actions class="px-16 pt-12 d-flex flex-column">
            <v-btn
              id="log-in"
              aria-label="Log in to Course Evaluation. (You will be sent to CalNet login page.)"
              block
              color="accent"
              large
              @click="logIn"
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
import Context from '@/mixins/Context'
import DevAuth from '@/components/admin/DevAuth'
import {getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  mixins: [Context],
  components: {
    DevAuth
  },
  data: () => ({
    currentTermName: undefined
  }),
  created() {
    this.$putFocusNextTick('page-title')
    this.currentTermName = this.$_.get(this.$_.find(this.$config.availableTerms, {'id': this.$config.currentTermId}), 'name')
    const error = this.$_.get(this.$route, 'query.error')
    if (error) {
      this.reportError(error)
    } else {
      this.alertScreenReader(`Welcome to Course Evaluation - ${this.currentTermName}. Please log in.`)
    }

  },
  methods: {
    logIn() {
      getCasLoginURL().then(data => window.location.href = data.casLoginUrl)
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
.frosted {
  background-color: rgba(255, 255, 255, 0.8) !important;
}
h1 strong {
  display: block;
  font-size: 65%;
}
</style>

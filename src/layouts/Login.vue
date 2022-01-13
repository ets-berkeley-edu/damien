<template>
  <div class="background-lecture-hall fill-viewport">
    <div>{{ error }}</div>
    <div class="container">
      <div class="sign-in" role="main">
        <DevAuth v-if="$config.devAuthEnabled" :report-error="reportError" />
      </div>
      <div class="box-container" role="banner">
        <div class="header">
          <h1>Welcome to Course Evaluation</h1>
        </div>
      </div>
      <div class="copyright pt-2" role="contentinfo">
        <span class="font-size-12 text-white">&copy; 2021 The Regents of the University of California</span>
      </div>
    </div>
  </div>
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
  background: url('~@/assets/lecture_hall_background.jpg') no-repeat center center
    fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.btn-sign-in {
  height: 50px;
  width: 256px;
  font-size: 20px;
  top: 4.7em;
}
.box-container {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.5);
  flex: 1;
  height: 360px;
  min-height: 360px;
  width: 320px;
  opacity: 0.8;
  padding: 0 25px 0 25px;
  z-index: -1;
}
.copyright {
  background-color: #3b80bf;
  height: 40px;
  width: 320px;
  padding-top: 10px;
  text-align: center;
  white-space: nowrap;
}
.header {
  padding-top: 40px;
  text-align: center;
}
.sign-in {
  position: absolute;
  top: 460px;
  left: 50%;
  text-align: center;
  transform: translate(-50%, -50%);
}
.contact-us {
  padding: 20px 40px 10px 40px;
  width: 320px;
  text-align: left;
}
.container {
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 24em;
  padding-top: 200px;
  position: relative;
  z-index: 999;
}
button {
  background-color: #3b80bf;
}
h1 {
  color: #0275d8;
  font-weight: 200;
  font-size: 81px;
  letter-spacing: 8px;
  padding-top: 14px;
}
</style>

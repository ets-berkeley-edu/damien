<template>
  <div class="background-fade d-flex justify-space-around">
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

<script>
export default {
  name: 'NotFound',
  created() {
    this.$ready('404')
  }
}
</script>

<style scoped>
.background-fade {
  background: url('~@/assets/background_fade.png') no-repeat center center;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  height: 100%;
  padding: 0px !important;
  position: fixed;
  top: 50px;
  left: 26px;
  max-width: unset;
  overflow-y: scroll;
  width: 100%;
}
.foreground {
  background: transparent;
  max-height: 75%;
  max-width: 1200px;
  width: 90%;
}
</style>
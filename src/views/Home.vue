<template>
  <div v-if="!loading" class="body">
    <v-card outlined>
      <h1>Damien Welcomes You.</h1>
      <div>
        <img alt="Harvey Stephens as Damien in The Omen (1976)" src="@/assets/damien_cemetary.png">
      </div>
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Home',
  mixins: [Context]
}
</script>
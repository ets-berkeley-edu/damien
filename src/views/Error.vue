<template>
  <div class="align-center d-flex ml-12 mt-14">
    <div class="mr-4">
      <img
        alt="Frustrated crow on a branch"
        aria-label="Frustrated crow on a branch"
        class="frustrated-crow"
        src="@/assets/frustrated-crow.png"
      >
    </div>
    <div>
      <h1 id="page-title" tabindex="-1">{{ message ? 'Uh-oh, error!' : 'Error' }}</h1>
      <div
        id="error-message"
        class="mt-3"
        aria-live="polite"
        role="alert"
      >
        {{ message || 'Uh-oh, there was a problem.' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import {useRoute} from 'vue-router'
import {useContextStore} from '@/stores/context'

const message = useRoute().query.m

onMounted(() => {
  useContextStore().loadingComplete('Error')
})
</script>

<style scoped>
.frustrated-crow {
  width: 124px;
}
</style>

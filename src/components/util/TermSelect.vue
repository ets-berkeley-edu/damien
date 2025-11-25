<template>
  <div class="align-center d-flex flex-wrap">
    <div class="pr-3">
      <select
        id="select-term"
        aria-label="Term"
        autocomplete="off"
        class="font-size-18 select-term my-2"
        :disabled="contextStore.loading"
        :value="contextStore.selectedTermId"
        @change="onChangeTerm"
      >
        <option
          v-for="term in contextStore.config.availableTerms"
          :id="`term-option-${term.id}`"
          :key="term.id"
          :disabled="termIds && !includes(termIds, term.id)"
          :value="term.id"
        >
          {{ term.name }}
        </option>
      </select>
    </div>
    <v-btn
      v-if="contextStore.currentUser.isAdmin"
      id="toggle-term-locked"
      :disabled="isTogglingLock || contextStore.loading"
      icon
      :title="`${contextStore.isSelectedTermLocked ? 'Unlock' : 'Lock'} ${contextStore.selectedTermName} for editing`"
      @click="toggleTermLocked"
    >
      <v-progress-circular
        v-if="isTogglingLock"
        class="spinner"
        color="primary"
        :indeterminate="true"
        rotate="5"
        size="24"
        width="4"
      />
      <v-icon
        v-if="!isTogglingLock"
        :color="contextStore.isSelectedTermLocked ? 'error' : 'success'"
        :icon="contextStore.isSelectedTermLocked ? mdiLock : mdiLockOpen"
        size="large"
      />
    </v-btn>
    <v-icon
      v-if="!contextStore.currentUser.isAdmin"
      id="term-locked-indicator"
      :color="contextStore.isSelectedTermLocked ? 'error' : 'success'"
      :icon="contextStore.isSelectedTermLocked ? mdiLock : mdiLockOpen"
      size="large"
      :title="`${contextStore.selectedTermName} is ${contextStore.isSelectedTermLocked ? 'locked' : 'unlocked'} for editing.`"
    />
  </div>
</template>

<script setup>
import {ref} from 'vue'
import {includes} from 'lodash'
import {mdiLock, mdiLockOpen} from '@mdi/js'
import {useRoute, useRouter} from 'vue-router'
import {useContextStore} from '@/stores/context'
import {getEvaluationTerm, lockEvaluationTerm, unlockEvaluationTerm} from '@/api/evaluationTerms'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'

defineProps({
  termIds: {
    default: null,
    required: false,
    type: Array
  }
})

const contextStore = useContextStore()
const isTogglingLock = ref(false)
const query = useRoute().query
const router = useRouter()

const onChangeTerm = event => {
  const termId = event.target.value
  if (termId && termId !== query.term) {
    router.push({
      query: {...query, term: termId}
    })
    contextStore.selectTerm(termId).then(term => {
      getEvaluationTerm(term.id).then(data => {
        contextStore.setIsSelectedTermLocked(data.isLocked === true)
      })
    })
    putFocusNextTick('select-term')
  }
}

const toggleTermLocked = () => {
  isTogglingLock.value = true
  if (!contextStore.isSelectedTermLocked) {
    alertScreenReader(`Locking ${contextStore.selectedTermName}`)
    lockEvaluationTerm(contextStore.selectedTermId).then(data => {
      contextStore.setIsSelectedTermLocked(data.isLocked === true)
      alertScreenReader(`Locked ${contextStore.selectedTermName}`)
      putFocusNextTick('toggle-term-locked')
      isTogglingLock.value = false
    })
  } else {
    unlockEvaluationTerm(contextStore.selectedTermId).then(data => {
      alertScreenReader(`Unlocking ${contextStore.selectedTermName}`)
      contextStore.setIsSelectedTermLocked(data.isLocked === true)
      alertScreenReader(`Unlocked ${contextStore.selectedTermName}`)
      putFocusNextTick('toggle-term-locked')
      isTogglingLock.value = false
    })
  }
}
</script>

<style scoped>
.select-term {
  max-width: 200px;
}
</style>

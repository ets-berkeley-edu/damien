<template>
  <div class="align-center d-flex flex-wrap">
    <div>
      <select
        id="select-term"
        aria-label="Term"
        autocomplete="off"
        class="font-size-18 select-term my-2 r-mr-3"
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
    <v-switch
      v-if="contextStore.currentUser.isAdmin"
      id="toggle-term-locked"
      v-model="termLocked"
      :aria-label="`Toggle lock for ${contextStore.selectedTermName}`"
      class="r-ml-3"
      density="comfortable"
      :disabled="isTogglingLock || contextStore.loading"
      :false-icon="mdiLockOpen"
      hide-details
      inset
      :loading="isTogglingLock"
      :title="`${termLocked ? 'Lock' : 'Unlocked'} ${contextStore.selectedTermName} for editing.`"
      :true-icon="mdiLock"
      @update:model-value="toggleTermLocked"
    />
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
import {ref, watch} from 'vue'
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
const termLocked = ref(false)

watch(
  () => contextStore.isSelectedTermLocked,
  v => {
    if (!isTogglingLock.value) termLocked.value = !!v
  },
  {immediate: true}
)


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

const toggleTermLocked = desiredLocked => {
  if (isTogglingLock.value || contextStore.loading) return

  isTogglingLock.value = true
  const termName = contextStore.selectedTermName
  const prev = contextStore.isSelectedTermLocked

  if (desiredLocked) {
    alertScreenReader(`Locking ${termName}`)
    lockEvaluationTerm(contextStore.selectedTermId)
      .then(data => {
        const locked = data.isLocked === true
        contextStore.setIsSelectedTermLocked(locked)
        termLocked.value = locked
        alertScreenReader(`Locked ${termName}`)
      })
      .catch(() => {
        contextStore.setIsSelectedTermLocked(prev)
        termLocked.value = !!prev
        alertScreenReader(`Unable to update lock state for ${termName}`)
      })
      .finally(() => {
        isTogglingLock.value = false
        putFocusNextTick('toggle-term-locked')
      })
  } else {
    alertScreenReader(`Unlocking ${termName}`)
    unlockEvaluationTerm(contextStore.selectedTermId)
      .then(data => {
        const locked = data.isLocked === true
        contextStore.setIsSelectedTermLocked(locked)
        termLocked.value = locked
        alertScreenReader(`Unlocked ${termName}`)
      })
      .catch(() => {
        contextStore.setIsSelectedTermLocked(prev)
        termLocked.value = !!prev
        alertScreenReader(`Unable to update lock state for ${termName}`)
      })
      .finally(() => {
        isTogglingLock.value = false
        putFocusNextTick('toggle-term-locked')
      })
  }
}
</script>

<style scoped>
.select-term {
  max-width: 12.5rem;
}
:deep(.v-switch .v-selection-control:not(.v-selection-control--dirty) .v-selection-control__input .v-icon) {
  color: rgb(var(--v-theme-success));
}

:deep(.v-switch .v-selection-control.v-selection-control--dirty .v-selection-control__input .v-icon) {
  color: rgb(var(--v-theme-error));
}

:deep(.v-switch .v-selection-control__input .v-icon) {
  font-size: 1.5rem;
}
</style>

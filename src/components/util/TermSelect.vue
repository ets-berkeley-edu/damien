<template>
  <div class="d-flex align-center justify-end flex-wrap">
    <div class="float-right mr-3">
      <label
        id="select-term-label"
        for="select-term"
        class="sr-only"
      >
        Term:
      </label>
      <select
        id="select-term"
        v-model="selectedTermId"
        class="native-select-override select-term my-2"
        :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
        :disabled="loading"
        @change="onChangeTerm"
      >
        <option
          v-for="term in $config.availableTerms"
          :id="`term-option-${term.id}`"
          :key="term.id"
          :value="term.id"
          :disabled="termIds && !$_.includes(termIds, term.id)"
        >
          {{ term.name }}
        </option>
      </select>
    </div>
    <div class="flex-md-shrink-0">
      <label for="toggle-term-locked" class="sr-only">
        Evaluation term is {{ isSelectedTermLocked ? 'locked' : 'unlocked' }}.
      </label>
      <v-btn
        id="toggle-term-locked"
        class="px-0"
        :disabled="isTogglingLock || loading"
        icon
        @click="toggleTermLocked"
        @keydown.enter="toggleTermLocked"
      >
        <span class="sr-only">
          {{ isTogglingLock ? 'Toggling...' : (isSelectedTermLocked ? 'Unlock' : 'Lock') }}
        </span>
        <v-progress-circular
          v-if="isTogglingLock"
          class="spinner"
          :indeterminate="true"
          rotate="5"
          size="24"
          width="4"
          color="primary"
        />
        <v-icon
          v-if="!isTogglingLock"
          :color="isSelectedTermLocked ? 'error' : 'success'"
          large
        >
          {{ isSelectedTermLocked ? 'mdi-lock' : 'mdi-lock-open' }}
        </v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import {getEvaluationTerm, lockEvaluationTerm, unlockEvaluationTerm} from '@/api/evaluationTerms'
import Context from '@/mixins/Context.vue'

export default {
  name: 'TermSelect',
  mixins: [Context],
  props: {
    afterSelect: {
      default: () => {},
      required: false,
      type: Function
    },
    termIds: {
      default: null,
      required: false,
      type: Array
    }
  },
  data: () => ({
    isTogglingLock: false
  }),
  created() {
    const termId = this.$_.get(this.$route.query, 'term')
    if (termId && this.$_.find(this.$config.availableTerms, {id: termId})) {
      this.setTerm(termId)
    } else {
      this.$router.push({
        query: {...this.$route.query, term: this.selectedTermId || this.$config.currentTermId}
      })
    }
  },
  methods: {
    onChangeTerm(event) {
      const termId = event.target.value
      if (termId && termId !== this.$_.get(this.$route.query, 'term')) {
        this.$router.push({
          query: {...this.$route.query, term: termId}
        })
        this.selectTerm(termId)
        this.$putFocusNextTick('select-term')
      }
    },
    setTerm(termId) {
      this.selectTerm(termId).then(() => {
        if (this.selectedTermId) {
          getEvaluationTerm(this.selectedTermId).then(data => {
            this.setIsSelectedTermLocked(data.isLocked === true)
          })
        }
        this.afterSelect()
      })
    },
    toggleTermLocked() {
      this.isTogglingLock = true
      if (!this.isSelectedTermLocked) {
        lockEvaluationTerm(this.selectedTermId).then(data => {
          this.setIsSelectedTermLocked(data.isLocked === true)
          this.alertScreenReader(`Locked ${this.selectedTermName}`)
          this.isTogglingLock = false
        })
      } else {
        unlockEvaluationTerm(this.selectedTermId).then(data => {
          this.setIsSelectedTermLocked(data.isLocked === true)
          this.alertScreenReader(`Unlocked ${this.selectedTermName}`)
          this.isTogglingLock = false
        })
      }
    }
  }
}
</script>

<style scoped>
.lock-label {
  min-width: 6.5rem;
  text-align: end;
}
.select-term {
  max-width: 200px;
}
</style>

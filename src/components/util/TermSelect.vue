<template>
  <div class="d-flex align-center justify-end flex-wrap">
    <div v-if="$currentUser.isAdmin" class="d-flex align-baseline mr-3">
      <label
        id="select-term-label"
        for="select-term"
        class="align-self-baseline text-nowrap pr-3"
      >
        Term:
      </label>
      <select
        id="select-term"
        v-model="selectedTermId"
        class="native-select-override select-term my-2 px-3"
        :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
        :disabled="loading"
        @change="onChangeTerm"
      >
        <option
          v-for="term in $config.availableTerms"
          :id="`term-option-${term.id}`"
          :key="term.id"
          :value="term.id"
        >
          {{ term.name }}
        </option>
      </select>
    </div>
    <div class="d-flex ml-4">
      <label for="toggle-term-locked" class="lock-label text-nowrap pr-4 py-2">
        {{ `${isSelectedTermLocked ? 'Unlock' : 'Lock'} term` }}
      </label>
      <v-switch
        id="toggle-term-locked"
        class="my-auto"
        color="tertiary"
        dense
        :disabled="loading"
        hide-details
        :input-value="isSelectedTermLocked"
        inset
        @change="toggleTermLocked"
      />
      <div class="lock-indicator">
        <div v-if="isSelectedTermLocked" class="ml-auto">
          <span class="sr-only">Evaluation term is locked.</span>
          <v-icon large>
            mdi-lock
          </v-icon>
        </div>
      </div>
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
    }
  },
  created() {
    const termId = this.$_.get(this.$route.query, 'term')
    if (termId) {
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
        this.$putFocusNextTick('select-term')
      }
    },
    setTerm(termId) {
      this.selectTerm(termId).then(() => {
        getEvaluationTerm(this.selectedTermId).then(data => {
          this.setIsSelectedTermLocked(data.isLocked === true)
        })
        this.afterSelect()
      })
    },
    toggleTermLocked() {
      if (!this.isSelectedTermLocked) {
        lockEvaluationTerm(this.selectedTermId).then(data => {
          this.setIsSelectedTermLocked(data.isLocked === true)
          this.alertScreenReader(`Locked ${this.selectedTermName}`)
        })
      } else {
        unlockEvaluationTerm(this.selectedTermId).then(data => {
          this.setIsSelectedTermLocked(data.isLocked === true)
          this.alertScreenReader(`Unlocked ${this.selectedTermName}`)
        })
      }
    }
  }
}
</script>

<style scoped>
.lock-indicator {
  min-width: 50px;
}
.lock-label {
  min-width: 6.5rem;
  text-align: end;
}
.select-term {
  max-width: 200px;
}
</style>

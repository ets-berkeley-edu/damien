<template>
  <div v-if="!loading">
    <v-row>
      <v-col cols="12" md="7" class="d-flex justify-start">
        <h1>
          Course Errors Dashboard - {{ $config.currentTermName }}
        </h1>
      </v-col>
    </v-row>
    <v-card outlined class="elevation-1">
      <EvaluationTable :evaluations="evaluations" />
    </v-card>
  </div>
</template>

<script>
import {getValidation} from '@/api/evaluations'
import Context from '@/mixins/Context.vue'
import EvaluationTable from '@/components/evaluation/EvaluationTable'

export default {
  name: 'CourseErrors',
  components: {
    EvaluationTable
  },
  mixins: [Context],
  data: () => ({
    evaluations: [],
  }),
  created() {
    this.refresh()
  },
  methods: {
    refresh() {
      this.$loading()
      getValidation().then(data => {
        this.evaluations = this.$_.sortBy(data, 'sortableCourseNumber')
        this.$ready('Course Errors')
      })
    }
  }
}
</script>

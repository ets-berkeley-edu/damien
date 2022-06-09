<template>
  <div class="pt-2">
    <v-row>
      <v-col cols="12" md="7" class="d-flex justify-start">
        <h1 id="page-title">
          Course Errors Dashboard<span v-if="$config.currentTermName"> - {{ $config.currentTermName }}</span>
        </h1>
      </v-col>
    </v-row>
    <v-card v-if="!loading" outlined class="elevation-1">
      <EvaluationTable :readonly="true" />
    </v-card>
  </div>
</template>

<script>
import {getValidation} from '@/api/evaluations'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationTable from '@/components/evaluation/EvaluationTable'

export default {
  name: 'CourseErrors',
  components: {
    EvaluationTable
  },
  mixins: [Context, DepartmentEditSession],
  created() {
    this.refresh()
  },
  methods: {
    refresh() {
      this.$loading()
      getValidation().then(data => {
        this.setEvaluations(this.$_.sortBy(data, 'sortableCourseNumber'))
        this.$ready('Course Errors')
      })
    }
  }
}
</script>

<template>
  <div>
    <div class="pb-2">
      <h1>{{ department.deptName }} ({{ $_.keys(department.catalogListings).join(', ') }}) - {{ this.$config.currentTermId }}</h1>
    </div>
    <v-card outlined class="elevation-1">
      <EvaluationTable :sections="sections" />
    </v-card>
  </div>
</template>

<script>
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import {getDepartment} from '@/api/departments'

export default {
  name: 'Department',
  components: {EvaluationTable},
  data: () => ({
    department: {},
    departmentId: null,
    sections: [],
  }),
  created() {
    this.$loading()
    this.departmentId = this.$_.get(this.$route, 'params.departmentId')
    getDepartment(this.departmentId, this.$config.currentTermId).then(data => {
      this.department = data
      this.sections = data.sections
      this.$ready()
    })
  }
}
</script>

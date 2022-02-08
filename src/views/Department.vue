<template>
  <div v-if="!loading">
    <div class="pb-2">
      <h1>{{ department.deptName }} ({{ $_.keys(department.catalogListings).join(', ') }}) - {{ this.$config.currentTermId }}</h1>
    </div>
    <DepartmentContacts />
    <v-card outlined class="elevation-1">
      <EvaluationTable :sections="sections" />
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentContacts from '@/components/admin/DepartmentContacts'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationTable from '@/components/evaluation/EvaluationTable'

export default {
  name: 'Department',
  components: {DepartmentContacts, EvaluationTable},
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    department: {},
    sections: []
  }),
  created() {
    this.$loading()
    const departmentId = this.$_.get(this.$route, 'params.departmentId')
    this.init(departmentId, this.$config.currentTermId).then(data => {
      this.department = data
      this.sections = data.sections
      this.$ready()
    })
  }
}
</script>

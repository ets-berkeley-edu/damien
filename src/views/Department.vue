<template>
  <div v-if="!loading">
    <v-row>
      <v-col cols="12" md="7" class="d-flex justify-start">
        <h1>{{ department.deptName }} ({{ $_.keys(department.catalogListings).join(', ') }}) - {{ this.selectedTerm.name }}</h1>
      </v-col>
      <v-col
        v-if="$currentUser.isAdmin"
        cols="12"
        md="5"
        class="d-flex justify-end"
      >
        <label id="select-term-label" for="select-term" class="pa-3">
          Previous terms:
        </label>
        <v-select
          id="select-term"
          v-model="selectedTermId"
          item-text="name"
          item-value="id"
          :items="availableTerms"
          label="Select..."
          solo
        >
          <span :id="`term-option-${data.item.id}`" slot="item" slot-scope="data">{{ data.item.name }}</span>
        </v-select>
        <v-btn class="ma-2" :disabled="!selectedTerm" @click="refresh">Apply</v-btn>
      </v-col>
    </v-row>
    <v-container v-if="$currentUser.isAdmin" class="mx-0 px-0 pb-6">
      <v-row justify="start">
        <v-col cols="12" md="4"><DepartmentContacts /></v-col>
        <v-col cols="12" md="8"><DepartmentNote /></v-col>
      </v-row>
    </v-container>
    <v-card outlined class="elevation-1">
      <EvaluationTable :sections="sections" />
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentContacts from '@/components/admin/DepartmentContacts'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EvaluationTable from '@/components/evaluation/EvaluationTable'

export default {
  name: 'Department',
  components: {DepartmentContacts, DepartmentNote, EvaluationTable},
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    availableTerms: undefined,
    department: {},
    sections: [],
    selectedTerm: undefined,
    selectedTermId: undefined
  }),
  created() {
    this.availableTerms = this.$config.availableTerms
    this.selectedTermId = this.$config.currentTermId
    this.refresh()
  },
  methods: {
    refresh() {
      this.$loading()
      const departmentId = this.$_.get(this.$route, 'params.departmentId')
      const termId = this.selectedTermId
      this.init({departmentId, termId}).then(department => {
        this.department = department
        this.sections = department.sections
        this.selectedTerm = this.$_.find(this.availableTerms, {'id': termId})
        this.$ready()
      })
    }
  }
}
</script>

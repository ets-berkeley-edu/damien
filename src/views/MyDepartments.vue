<template>
  <v-app>
    <v-container class="background-lecture-hall" fill-height fluid>
      <v-main>
        <v-card
          class="mx-auto px-8 py-6 frosted accent-border accent--text"
          max-width="600"
          outlined
        >
          <div class="text-center">
            <h1 id="page-title">
              <strong>Select Department</strong>
            </h1>
          </div>
          <v-card-actions class="px-16 pt-12 d-flex flex-column">
            <v-btn
              v-for="(department, index) in departments"
              :id="`select-dept-${index}-btn`"
              :key="index"
              block
              class="mx-0 my-2 text-capitalize"
              color="accent"
              large
              :href="`/department/${department.id}`"
            >
              {{ department.name }}
              <v-icon class="pl-2">mdi-arrow-right-circle-outline</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-main>
    </v-container>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'MyDepartments',
  mixins: [Context],
  data: () => ({
    departments: []
  }),
  created() {
    this.departments = this.$_.get(this.$currentUser, 'departments')
    this.$ready('My Departments')
    this.$putFocusNextTick('select-dept-0-btn')
  },
  methods: {

  }
}
</script>

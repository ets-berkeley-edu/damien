<template>
  <div>
    <div class="pb-2">
      <h1>Evaluation Status Dashboard - Spring 2022</h1>
    </div>
    <v-card outlined class="elevation-1">
      <v-data-table
        id="department-table"
        disable-pagination
        :headers="headers"
        hide-default-footer
        :items="departments"
        show-select
      >
        <template #header.data-table-select="{ on, props }">
          <v-simple-checkbox
            id="checkbox-select-dept-all"
            :ripple="false"
            v-bind="props"
            v-on="on"
          ></v-simple-checkbox>
        </template>
        <template #body="{items}">
          <tbody>
            <template v-for="(department, index) in items">
              <tr :id="`department-${index}`" :key="department.name">
                <td>
                  <v-simple-checkbox
                    :id="`checkbox-select-dept-${$_.kebabCase(department.deptName)}`"
                    v-model="department.isSelected"
                    :ripple="false"
                    @input="select($event)"
                  ></v-simple-checkbox>
                </td>
                <td class="department-name">
                  <router-link :id="`link-to-dept-${$_.kebabCase(department.deptName)}`" :to="`/department/${department.id}`">
                    {{ department.deptName }}
                    ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})
                  </router-link>
                </td>
                <td class="department-lastUpdated">
                  {{ department.updatedAt }}
                </td>
                <td class="department-errors">
                  <span class="font-italic muted--text">TODO</span>
                </td>
                <td class="department-confirmed">
                  <span class="font-italic muted--text">TODO</span>
                </td>
                <td class="department-note">
                  {{ $_.get(department, `notes.${$config.currentTermId}.note`) }}
                </td>
              </tr>
            </template>
          </tbody>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import {getDepartmentsEnrolled} from '@/api/departments'

export default {
  name: 'StatusBoard',
  data: () => ({
    departments: [],
    headers: [
      {text: 'Department', value: 'deptName'},
      {text: 'Last Updated', value: 'updatedAt'},
      {text: 'Errors', value: 'errors'},
      {text: 'Confirmed', value: 'confirmed'},
      {text: 'Notes', value: 'notes'},
    ],
  }),
  created() {
    this.$loading()
    getDepartmentsEnrolled().then(data => {
      this.departments = data
      this.$ready()
    })
  },
  methods: {
    select(e) {
      //TODO:
      console.log(e)
    }
  }
}
</script>

<style scoped>
.department-confirmed {
  width: 10%;
}
.department-errors {
  width: 10%;
}
.department-lastUpdated {
  width: 20%;
}
.department-name {
  width: 25%;
}
.department-note {
  width: 35%;
}
</style>

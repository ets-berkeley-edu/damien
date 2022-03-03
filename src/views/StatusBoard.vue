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
      >
        <template #body="{items}">
          <tbody>
            <template v-for="(department, index) in items">
              <tr :key="department.name">
                <td :id="`department-name-${index}`">
                  <router-link :to="`/department/${department.id}`">
                    {{ department.deptName }}
                    ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})
                  </router-link>
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
      {text: 'Last Updated', value: 'lastUpdated'},
      {text: 'Errors', value: 'errors'},
      {text: 'Confirmed', value: 'confirmed'},
      {text: 'Notes', value: 'note'},
    ],
  }),
  created() {
    this.$loading()
    getDepartmentsEnrolled().then(data => {
      this.departments = data
      this.$ready()
    })
  }
}
</script>

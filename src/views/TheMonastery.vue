<template>
  <div>
    <div class="pb-2 d-flex">
      <h1>Group Management</h1>
      <v-spacer class="d-flex justify-center"></v-spacer>
      <v-banner
        v-if="$config.isVueAppDebugMode && $config.easterEggMonastery && $vuetify.theme.dark"
        shaped
        single-line
        class="pr-4 my-auto"
      >
        Welcome to <a :href="$config.easterEggMonastery" target="_blank">The Monastery</a>
      </v-banner>
    </div>
    <v-card outlined class="elevation-1">
      <v-data-table
        id="department-table"
        dense
        disable-pagination
        :headers="headers"
        hide-default-footer
        :items="departments"
      >
        <template #body="{items}">
          <tbody>
            <template v-for="(department, deptIndex) in items">
              <tr
                v-for="(contact, contactIndex) in department.contacts"
                :key="`${deptIndex}-${contactIndex}`"
                class="compact-row"
              >
                <td
                  v-if="contactIndex === 0"
                  :id="`department-${deptIndex}-name`"
                  class="dept-name"
                  :rowspan="department.contacts.length"
                >
                  <router-link :to="`/department/${department.id}`">
                    {{ department.deptName }} ({{ $_.keys(department.catalogListings).join(', ') }})
                  </router-link>
                </td>
                <td
                  v-if="contactIndex === 0"
                  :id="`department-${deptIndex}-courses`"
                  class="dept-courses"
                  :rowspan="department.contacts.length"
                >
                  {{ department.totalSections }}
                </td>
                <td
                  :id="`department-${deptIndex}-contact-${contactIndex}-name`"
                  :class="subRowClass(contactIndex, department.contacts)"
                >
                  {{ contact.firstName }} {{ contact.lastName }}
                </td>
                <td :id="`department-${deptIndex}-contact-${contactIndex}-uid`" :class="subRowClass(contactIndex, department.contacts)">{{ contact.uid }}</td>
                <td :id="`department-${deptIndex}-contact-${contactIndex}-email`" :class="subRowClass(contactIndex, department.contacts)">{{ contact.email }}</td>
                <td :id="`department-${deptIndex}-contact-${contactIndex}-comms`" :class="subRowClass(contactIndex, department.contacts)">
                  <span class="sr-only">{{ `${contact.canReceiveCommunications ? 'Receives' : 'Does not receive'} notifications` }}</span>
                  <BooleanIcon :model="contact.canReceiveCommunications" />
                </td>
                <td
                  :id="`department-${deptIndex}-contact-${contactIndex}-blue`"
                  :class="subRowClass(contactIndex, department.contacts)"
                  class="font-italic d-flex flex-row-reverse justify-end"
                >
                  <span v-if="!contact.canViewReports" class="sr-only">No Blue access</span>
                  <span v-if="contact.canViewReports">
                    {{ `Reports ${contact.canViewResponseRates ? 'and response rates ' : ''}` }}
                  </span>
                  <BooleanIcon :model="contact.canViewReports" />
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
import BooleanIcon from '@/components/util/BooleanIcon'
import {getDepartmentsEnrolled} from '@/api/departments'

export default {
  name: 'TheMonastery',
  components: {BooleanIcon},
  data: () => ({
    departments: [],
    headers: [
      {text: 'Department'},
      {text: 'Courses'},
      {text: 'Contacts'},
      {text: 'UID'},
      {text: 'Email Address'},
      {text: 'Receives Notifications'},
      {text: 'Blue Access'},
    ],
  }),
  created() {
    this.$loading()
    getDepartmentsEnrolled(true, true).then(data => {
      this.departments = data
      this.$ready('Group management')
    })
  },
  methods: {
    subRowClass(subIndex, subItems) {
      return subIndex + 1 < subItems.length ? 'borderless' : ''
    }
  }
}
</script>

<style scoped>
.compact-row td {
  height: unset !important;
}
.dept-courses {
  vertical-align: top;
}
.dept-name {
  vertical-align: top;
  width: 20%;
}
</style>
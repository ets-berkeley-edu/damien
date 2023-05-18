<template>
  <div class="pt-2">
    <div class="pb-2 d-flex">
      <h1 id="page-title" :style="{color: titleHexColor}">Group Management</h1>
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
        :loading="loading"
        must-sort
      >
        <template #body="{items}">
          <tbody class="h-100vh" @mouseleave="() => hoveredDept = null" @focusout="() => hoveredDept = null">
            <template v-for="(department, deptIndex) in items">
              <tr
                v-if="$_.isEmpty(department.contacts)"
                :key="`${deptIndex}-0`"
                class="compact-row"
                @mouseover="() => hoveredDept = department.id"
                @focusin="() => hoveredDept = department.id"
              >
                <th
                  :id="`department-${deptIndex}-name`"
                  class="dept-name"
                  :class="{hovered: hoveredDept === department.id}"
                  rowspan="1"
                  scope="row"
                >
                  <router-link :to="`/department/${department.id}`">
                    {{ department.deptName }}
                    <span v-if="$_.size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
                  </router-link>
                </th>
                <td
                  :id="`department-${deptIndex}-courses`"
                  class="dept-courses"
                  :class="{hovered: hoveredDept === department.id}"
                  rowspan="1"
                >
                  {{ department.totalSections }}
                </td>
                <td colspan="5" :class="{hovered: hoveredDept === department.id}"></td>
              </tr>
              <tr
                v-for="(contact, contactIndex) in department.contacts"
                :key="`${deptIndex}-${contactIndex}`"
                class="compact-row"
                @mouseover="() => hoveredDept = department.id"
                @focusin="() => hoveredDept = department.id"
              >
                <th
                  v-if="contactIndex === 0"
                  :id="`department-${deptIndex}-name`"
                  class="dept-name"
                  :class="{hovered: hoveredDept === department.id}"
                  :rowspan="department.contacts.length"
                  scope="row"
                >
                  <router-link :to="`/department/${department.id}`">
                    {{ department.deptName }}
                    <span v-if="$_.size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
                  </router-link>
                </th>
                <td
                  v-if="contactIndex === 0"
                  :id="`department-${deptIndex}-courses`"
                  class="dept-courses"
                  :class="{hovered: hoveredDept === department.id}"
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
                  <BooleanIcon class="pr-1" :model="contact.canReceiveCommunications" />
                </td>
                <td
                  :id="`department-${deptIndex}-contact-${contactIndex}-blue`"
                  :class="subRowClass(contactIndex, department.contacts)"
                >
                  <div class="font-italic d-flex flex-row-reverse justify-end">
                    <span v-if="!contact.canViewReports" class="sr-only">No Blue access</span>
                    <span v-if="contact.canViewReports" class="text-condensed">
                      {{ `Reports ${contact.canViewResponseRates ? 'and response rates ' : ''}` }}
                    </span>
                    <BooleanIcon class="pr-1" :model="contact.canViewReports" />
                  </div>
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
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {getDepartmentsEnrolled} from '@/api/departments'

export default {
  name: 'TheMonastery',
  mixins: [Context, Util],
  components: {BooleanIcon},
  data: () => ({
    departments: [],
    headers: [
      {class: 'text-nowrap', text: 'Department', value: 'deptName'},
      {class: 'text-nowrap', sortable: false, text: 'Courses'},
      {class: 'text-nowrap', sortable: false, text: 'Contacts'},
      {class: 'text-nowrap', sortable: false, text: 'UID'},
      {class: 'text-nowrap', sortable: false, text: 'Email Address'},
      {sortable: false, text: 'Receives Notifications'},
      {class: 'text-nowrap', sortable: false, text: 'Blue Access'},
    ],
    hoveredDept: undefined
  }),
  created() {
    this.$loading()
    getDepartmentsEnrolled(true, true).then(data => {
      this.departments = data
      this.$ready('Group Management')
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
  vertical-align: middle;
}
.dept-name {
  font-size: 0.875rem !important;
  vertical-align: middle;
  width: 20%;
}
</style>

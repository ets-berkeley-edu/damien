<template>
  <div class="page-margins">
    <PageHeader>
      Departments
      <template #append>
        <v-banner
          v-if="config.isVueAppDebugMode && config.easterEggMonastery && theme.current.value.dark"
          border="sm"
          class="text-no-wrap"
          single-line
          max-width="12rem"
          min-width="12rem"
        >
          Welcome to&nbsp;<a :href="config.easterEggMonastery" target="_blank">The Monastery</a>
        </v-banner>
      </template>
    </PageHeader>
    <v-card v-if="!contextStore.loading">
      <v-data-table
        id="department-table"
        density="compact"
        disable-pagination
        :headers="headers"
        hide-default-footer
        :items="departments"
        :items-per-page="-1"
        must-sort
        :sort-by="sortBy"
        @mouseleave="() => hoveredDept = null"
        @focusout="() => hoveredDept = null"
        @update:sort-by="onUpdateSortBy"
      >
        <template #body="{items}">
          <template v-for="(department, deptIndex) in items">
            <tr
              v-if="isEmpty(department.contacts)"
              :key="`${deptIndex}-0`"
              class="compact-row"
              @mouseover="() => hoveredDept = department.id"
              @focusin="() => hoveredDept = department.id"
            >
              <th
                :id="`department-${deptIndex}-name`"
                class="dept-name pa-3"
                :class="{'bg-hovered': hoveredDept === department.id}"
                rowspan="1"
                scope="row"
              >
                <router-link :to="`/department/${department.id}`">
                  {{ department.deptName }}
                  <span v-if="size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
                </router-link>
              </th>
              <td
                :id="`department-${deptIndex}-courses`"
                class="dept-courses pt-3"
                :class="{'bg-hovered': hoveredDept === department.id}"
                rowspan="1"
              >
                {{ department.totalSections }}
              </td>
              <td colspan="5" :class="{'bg-hovered': hoveredDept === department.id}" />
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
                class="dept-name pt-3 vertical-align-top"
                :class="{'bg-hovered': hoveredDept === department.id}"
                :rowspan="department.contacts.length"
                scope="row"
              >
                <router-link :to="`/department/${department.id}`">
                  {{ department.deptName }}
                  <span v-if="size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
                </router-link>
              </th>
              <td
                v-if="contactIndex === 0"
                :id="`department-${deptIndex}-courses`"
                class="dept-courses pt-3 vertical-align-top"
                :class="{'bg-hovered': hoveredDept === department.id}"
                :rowspan="department.contacts.length"
              >
                {{ department.totalSections }}
              </td>
              <td
                :id="`department-${deptIndex}-contact-${contactIndex}-name`"
                class="vertical-align-top"
                :class="subRowClass(contactIndex, department.contacts)"
              >
                <div
                  :class="{
                    'pt-3': contactIndex === 0,
                    'pb-3': contactIndex === department.contacts.length - 1
                  }"
                >
                  {{ contact.firstName }} {{ contact.lastName }}
                </div>
              </td>
              <td
                :id="`department-${deptIndex}-contact-${contactIndex}-uid`"
                class="vertical-align-top"
                :class="subRowClass(contactIndex, department.contacts)"
              >
                <div
                  :class="{
                    'pt-3': contactIndex === 0,
                    'pb-3': contactIndex === department.contacts.length - 1
                  }"
                >
                  {{ contact.uid }}
                </div>
              </td>
              <td
                :id="`department-${deptIndex}-contact-${contactIndex}-email`"
                class="vertical-align-top"
                :class="subRowClass(contactIndex, department.contacts)"
              >
                <div
                  :class="{
                    'pt-3': contactIndex === 0,
                    'pb-3': contactIndex === department.contacts.length - 1
                  }"
                >
                  {{ contact.email }}
                </div>
              </td>
              <td
                :id="`department-${deptIndex}-contact-${contactIndex}-comms`"
                class="vertical-align-top"
                :class="subRowClass(contactIndex, department.contacts)"
              >
                <div
                  :class="{
                    'pt-3': contactIndex === 0,
                    'pb-3': contactIndex === department.contacts.length - 1
                  }"
                >
                  <span class="sr-only">{{ `${contact.canReceiveCommunications ? 'Receives' : 'Does not receive'} notifications` }}</span>
                  <BooleanIcon class="pr-1" :model="contact.canReceiveCommunications" />
                </div>
              </td>
              <td
                :id="`department-${deptIndex}-contact-${contactIndex}-blue`"
                class="vertical-align-top"
                :class="subRowClass(contactIndex, department.contacts)"
              >
                <div
                  class="font-italic d-flex flex-row-reverse justify-end"
                  :class="{
                    'pt-3': contactIndex === 0,
                    'pb-3': contactIndex === department.contacts.length - 1
                  }"
                >
                  <span v-if="!contact.canViewReports" class="sr-only">No Blue access</span>
                  <span v-if="contact.canViewReports" class="text-condensed">
                    {{ `Reports ${contact.canViewResponseRates ? 'and response rates ' : ''}` }}
                  </span>
                  <BooleanIcon class="pr-1" :model="contact.canViewReports" />
                </div>
              </td>
            </tr>
          </template>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import {find, isEmpty, size} from 'lodash'
import {onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useTheme} from 'vuetify'
import BooleanIcon from '@/components/util/BooleanIcon'
import PageHeader from '@/components/util/PageHeader'
import {alertScreenReader, getCatalogListings} from '@/lib/utils'
import {getDepartmentsEnrolled} from '@/api/departments'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const {config} = storeToRefs(contextStore)
const departments = ref([])
const headers = [
  {key: 'deptName', class: 'text-no-wrap', sortable: true, title: 'Department', value: 'deptName', width: 100},
  {class: 'text-no-wrap', sortable: false, title: 'Courses', width: 10},
  {class: 'text-no-wrap', sortable: false, title: 'Contacts', width: 200},
  {class: 'text-no-wrap', sortable: false, title: 'UID', width: 10},
  {class: 'text-no-wrap', sortable: false, title: 'Email Address', width: 20},
  {sortable: false, title: 'Receives Notifications', width: 10},
  {class: 'text-no-wrap', sortable: false, title: 'Blue Access', width: 190},
]
const hoveredDept = ref(undefined)
const sortBy = ref([])
const theme = useTheme()

onMounted(() => {
  contextStore.loadingStart()
  getDepartmentsEnrolled(true, true).then(data => {
    departments.value = data
    contextStore.loadingComplete()
  })
})

const onUpdateSortBy = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(headers, {key: key})
  const order = primarySortBy[0].order
  sortBy.value = primarySortBy
  if (header) {
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${order}ending`)
  }
}

const subRowClass = (subIndex, subItems) => {
  return subIndex + 1 < subItems.length ? 'borderless' : ''
}
</script>

<style scoped>
.compact-row td {
  padding-top: 3px;
  height: unset !important;
}
.compact-row:hover {
  background-color: rgb(var(--v-theme-hovered));
}
.dept-courses {
  vertical-align: middle;
}
.dept-name {
  font-size: 0.875rem !important;
  font-weight: 700 !important;
  vertical-align: middle;
}
</style>

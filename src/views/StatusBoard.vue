<template>
  <div class="page-margins">
    <PageHeader>
      Evaluation Status Dashboard &mdash;&nbsp;{{ contextStore.selectedTermName }}
      <template #append>
        <TermSelect />
      </template>
    </PageHeader>
    <v-card v-if="!contextStore.loading">
      <v-data-table
        id="department-table"
        density="compact"
        :disable-sort="contextStore.loading"
        :headers="departmentHeaders"
        hide-default-footer
        :items="departments"
        :items-per-page="-1"
        :loading="contextStore.loading || !contextStore.selectedTermId"
        must-sort
        :sort-by="sortBy"
        @update:sort-by="onUpdateSortBy"
      >
        <template #top>
          <div class="align-center d-flex pl-3 py-2">
            <v-checkbox
              id="checkbox-select-dept-all"
              aria-controls="open-notification-form-btn"
              aria-describedby="checkbox-select-dept-all-desc"
              color="primary"
              :disabled="contextStore.loading"
              hide-details
              :indeterminate="someDepartmentsSelected"
              :model-value="allDepartmentsSelected"
              title="Select All Departments"
              @update:model-value="toggleSelectAll"
            />
            <div id="checkbox-select-dept-all-desc">Send notification</div>
            <v-btn
              id="open-notification-form-btn"
              class="mx-2r text-capitalize"
              color="secondary"
              density="comfortable"
              :disabled="isCreatingNotification || isEmpty(selectedDepartmentIds) || contextStore.loading"
              text="Apply"
              @click="() => isCreatingNotification = true"
            />
          </div>
        </template>
        <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: _sortBy}">
          <SortableTableHeader
            :columns="columns"
            :is-sorted="isSorted"
            :on-sort="toggleSort"
            :sort-desc="get(_sortBy, 'order') === 'desc'"
            :sort-icon="getSortIcon"
          />
        </template>
        <template #body="{items}">
          <template v-for="(department, index) in items" :key="department.name">
            <tr :id="`department-${index}`">
              <td>
                <label class="sr-only" :for="`checkbox-select-dept-${department.id}`">
                  {{ department.deptName }}
                </label>
                <v-checkbox
                  :id="`checkbox-select-dept-${department.id}`"
                  aria-controls="open-notification-form-btn"
                  :aria-describedby="undefined"
                  class="align-center mt-0 pt-0"
                  color="primary"
                  :disabled="contextStore.loading"
                  hide-details
                  :model-value="isSelected(department)"
                  @update:model-value="toggleSelect(department)"
                />
              </td>
              <td class="department-name">
                <div class="d-flex align-top">
                  <router-link
                    :id="`link-to-dept-${kebabCase(department.deptName)}`"
                    class="text-accent font-weight-bold"
                    :to="`/department/${department.id}`"
                  >
                    {{ department.deptName }}
                    <span v-if="size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
                  </router-link>
                </div>
              </td>
              <td :id="`last-updated-dept-${department.id}`" class="department-lastUpdated">
                <span v-if="department.lastUpdated">
                  {{ toLocaleFromISO(department.lastUpdated) }}
                </span>
              </td>
              <td class="department-errors">
                <v-badge
                  v-if="department.totalInError"
                  :id="`errors-count-dept-${department.id}`"
                  aria-hidden="true"
                  :aria-live="null"
                  class="error-count"
                  color="error"
                  :content="department.totalInError"
                  inline
                />
                <span v-if="department.totalInError" class="sr-only">{{ pluralize('error', department.totalInError) }}</span>
                <v-icon
                  v-if="!department.totalInError"
                  alt="no errors"
                  :aria-hidden="null"
                  class="text-success ml-1"
                  :icon="mdiCheckCircle"
                />
              </td>
              <td class="department-confirmed">
                <v-icon
                  v-if="department.totalConfirmed > 0 && department.totalConfirmed === department.totalEvaluations"
                  alt="all confirmed"
                  class="text-success ml-1"
                  :icon="mdiCheckCircle"
                />
                <span v-if="department.totalConfirmed === 0 || department.totalConfirmed < department.totalEvaluations">
                  <span aria-hidden="true">{{ department.totalConfirmed }} / {{ department.totalEvaluations }}</span>
                  <span class="sr-only">{{ department.totalConfirmed }} of {{ department.totalEvaluations }} confirmed</span>
                </span>
              </td>
              <td class="department-note">
                <pre class="text-condensed truncate-with-ellipsis">{{ get(department, 'note.note') }}</pre>
              </td>
            </tr>
          </template>
        </template>
      </v-data-table>
    </v-card>
    <ModalDialog
      id-prefix="send-notification"
      :is-open="isCreatingNotification"
      max-width="1200"
      min-width="800"
      persistent
      role="dialog"
      width="90%"
    >
      <NotificationForm
        :after-send="afterSendNotification"
        min-width="800"
        :on-cancel="cancelSendNotification"
        :recipients="notificationRecipients"
      />
    </ModalDialog>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {filter as _filter, each, find, get, includes, indexOf, isEmpty, kebabCase, map, size} from 'lodash'
import {mdiCheckCircle} from '@mdi/js'
import ModalDialog from '@/components/util/ModalDialog'
import NotificationForm from '@/components/admin/NotificationForm'
import PageHeader from '@/components/util/PageHeader'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import TermSelect from '@/components/util/TermSelect'
import {alertScreenReader, getCatalogListings, pluralize, putFocusNextTick, toLocaleFromISO} from '@/lib/utils'
import {getDepartmentsEnrolled} from '@/api/departments'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const blockers = ref({})
const departments = ref([])
const departmentHeaders = [
  {key: 'select', ariaLabel: 'Selected', class: 'text-start px-4', headerProps: {width: '30px'}, sortable: true, title: 'Select', value: 'select'},
  {key: 'deptName', class: 'px-2', headerProps: {width: '50%'}, sortable: true, title: 'Department', value: 'deptName'},
  {key: 'lastUpdated', class: 'px-2', headerProps: {width: '20%'}, sortable: true, title: 'Last Updated', value: 'lastUpdated'},
  {key: 'totalInError', class: 'px-2', headerProps: {width: '10%'}, sortable: true, title: 'Errors', value: 'totalInError'},
  {key: 'totalConfirmed', class: 'px-2', headerProps: {width: '10%'}, sortable: true, title: 'Confirmed', value: 'totalConfirmed'},
  {key: 'note', class: 'px-2', headerProps: {width: '30%'}, sortable: true, title: 'Notes', value: 'note.note'}
]
const isCreatingNotification = ref(false)
const selectedDepartmentIds = ref([])
const sortBy = ref([{key: 'deptName', order: 'asc'}])

const allDepartmentsSelected = computed(() => {
  return !!(size(selectedDepartmentIds.value) && size(selectedDepartmentIds.value) === size(departments.value))
})
const notificationRecipients = computed(() => {
  const recipients = []
  each(departments.value, d => {
    if (isSelected(d)) {
      const departmentRecipients = _filter(d.contacts, 'canReceiveCommunications')
      if (departmentRecipients.length) {
        recipients.push({
          'deptId': d.id,
          'deptName': d.deptName,
          'recipients': _filter(d.contacts, 'canReceiveCommunications')
        })
      }
    }
  })
  return recipients
})
const someDepartmentsSelected = computed(() => {
  return !!(size(selectedDepartmentIds.value) && size(selectedDepartmentIds.value) < size(departments.value))
})

onMounted(() => {
  contextStore.loadingStart(`Loading ${contextStore.selectedTermName} Status Dashboard`)
  departments.value = []
  getDepartmentsEnrolled(true, false, true, contextStore.selectedTermId).then(data => {
    departments.value = data
    loadBlockers().then(() => {
      contextStore.loadingComplete(`${contextStore.selectedTermName} Status Dashboard`)
      putFocusNextTick('page-title')
    })
  })
})

const afterSendNotification = () => {
  selectedDepartmentIds.value = []
  isCreatingNotification.value = false
  alertScreenReader('Notification sent.')
  putFocusNextTick('open-notification-form-btn')
}

const cancelSendNotification = () => {
  isCreatingNotification.value = false
  alertScreenReader('Notification canceled.')
  putFocusNextTick('open-notification-form-btn')
}

const isSelected = department => {
  return includes(selectedDepartmentIds.value, department.id)
}

const loadBlockers = () => {
  return new Promise(resolve => {
    blockers.value = {}
    each(departments.value, d => {
      if (d.totalBlockers) {
        blockers.value[d.deptName] = d.totalBlockers
      }
    })
    resolve()
  })
}

const onUpdateSortBy = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(departmentHeaders, {key: key})
  const order = primarySortBy[0].order
  sortBy.value = primarySortBy
  if (header) {
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${order}ending`)
  }
}

const toggleSelect = department => {
  const index = indexOf(selectedDepartmentIds.value, department.id)
  const isSelecting = index === -1
  if (isSelecting) {
    selectedDepartmentIds.value.push(department.id)
  } else {
    selectedDepartmentIds.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  selectedDepartmentIds.value = allDepartmentsSelected.value ? [] : map(departments.value, 'id')
}
</script>

<style scoped>
.department-confirmed {
  min-width: 100px;
}
.department-errors {
  min-width: 80px;
}
.department-lastUpdated {
  min-width: 130px;
}
.department-name {
  min-width: 250px;
}
.department-note {
  max-width: 400px;
}
</style>

<style>
.v-badge--inline .v-badge__badge {
  font-weight: bold;
}
</style>

<template>
  <div class="page-margins pb-6">
    <PageHeader>
      Settings
      <template #append>
        <v-banner
          v-if="config.isVueAppDebugMode && config.easterEggMonastery && theme.current.value.dark"
          border="sm"
          class="text-no-wrap"
          single-line
          max-width="14.5rem"
          min-width="14.5rem"
        >
          Welcome to&nbsp;<a :href="config.easterEggNannysRoom" target="_blank">The Nanny's Room</a>
        </v-banner>
      </template>
    </PageHeader>
    <v-container v-if="!contextStore.loading" class="pa-0 mx-0" fluid>
      <v-row>
        <v-col cols="12" md="6" lg="3">
          <v-card
            height="100%"
            min-width="fit-content"
          >
            <v-card-title
              id="department-forms-card-title"
              class="pb-0"
              tabindex="-1"
            >
              Department Forms
            </v-card-title>
            <v-card-actions class="py-0">
              <v-btn
                v-if="!isAddingDepartmentForm"
                id="add-dept-form-btn"
                class="font-weight-bold"
                color="primary"
                :disabled="disableControls"
                :prepend-icon="mdiPlusThick"
                text="Add new department form"
                variant="text"
                @click="onClickAddDepartmentForm"
              />
              <v-form v-if="isAddingDepartmentForm" class="pa-2 w-100" @submit.prevent="onSubmitAddDepartmentForm">
                <label :for="'input-dept-form-name'" class="form-label">
                  Form name
                </label>
                <v-text-field
                  :id="'input-dept-form-name'"
                  v-model="newItemName"
                  class="mt-1"
                  color="primary"
                  density="compact"
                  :disabled="isSaving"
                  hide-details="auto"
                  required
                  variant="outlined"
                  @keydown.esc="cancelAdd('add-dept-form-btn')"
                />
                <div class="align-center d-flex mt-2">
                  <ProgressButton
                    :id="'save-dept-form-btn'"
                    :action="onSubmitAddDepartmentForm"
                    class="mr-2"
                    :disabled="!trim(newItemName) || isSaving"
                    :in-progress="isSaving"
                    :text="isSaving ? 'Saving' : 'Save'"
                  />
                  <v-btn
                    :id="'cancel-save-dept-form-btn'"
                    color="primary"
                    :disabled="isSaving"
                    text="Cancel"
                    variant="outlined"
                    @click="cancelAdd('add-dept-form-btn')"
                  />
                </div>
              </v-form>
            </v-card-actions>
            <v-card-text class="pt-0">
              <div class="nannys-list overflow-y-auto">
                <v-data-table
                  id="dept-forms-table"
                  density="compact"
                  disable-pagination
                  :headers="departmentFormHeaders"
                  hide-default-footer
                  :items="departmentForms"
                  :items-per-page="-1"
                  item-key="name"
                  must-sort
                  :sort-by="sortBy.departmentForms"
                  @update:sort-by="onSortDepartmentForms"
                >
                  <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: _sortBy}">
                    <SortableTableHeader
                      :id="'form-'"
                      :columns="columns"
                      :is-sorted="isSorted"
                      :on-sort="toggleSort"
                      :sort-desc="get(_sortBy, 'order') === 'desc'"
                      :sort-icon="getSortIcon"
                    />
                  </template>
                  <template #item.name="{item}">
                    <div class="d-flex justify-space-between">
                      <span>{{ item.name }}</span>
                      <v-btn
                        :id="`delete-dept-form-${item.id}-btn`"
                        class="font-weight-bold text-capitalize px-2 py-0"
                        color="primary"
                        :disabled="disableControls"
                        height="unset"
                        min-width="unset"
                        text="Delete"
                        variant="text"
                        @click.stop="() => listStore.confirmDeleteDepartmentForm(item)"
                      />
                    </div>
                  </template>
                </v-data-table>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6" lg="3">
          <v-card
            height="100%"
            min-width="fit-content"
          >
            <v-card-title
              id="evaluation-types-card-title"
              class="pb-0"
              tabindex="-1"
            >
              Evaluation Types
            </v-card-title>
            <v-card-actions class="py-0">
              <v-btn
                v-if="!isAddingEvaluationType"
                id="add-eval-type-btn"
                class="font-weight-bold"
                color="primary"
                :disabled="disableControls"
                :prepend-icon="mdiPlusThick"
                text="Add new evaluation type"
                variant="text"
                @click="onClickAddEvaluationType"
              />
              <v-form v-if="isAddingEvaluationType" class="pa-2 w-100" @submit.prevent="onSubmitAddEvaluationType">
                <label for="input-eval-type-name" class="form-label">
                  Type name
                </label>
                <v-text-field
                  id="input-eval-type-name"
                  v-model="newItemName"
                  class="mt-1"
                  color="primary"
                  density="compact"
                  :disabled="isSaving"
                  hide-details="auto"
                  required
                  variant="outlined"
                  @keydown.esc="cancelAdd('add-eval-type-btn')"
                />
                <div class="align-center d-flex mt-2">
                  <ProgressButton
                    id="save-eval-type-btn"
                    :action="onSubmitAddEvaluationType"
                    class="mr-2"
                    :disabled="!trim(newItemName) || isSaving"
                    :in-progress="isSaving"
                    :text="isSaving ? 'Saving' : 'Save'"
                  />
                  <v-btn
                    id="cancel-save-eval-type-btn"
                    color="primary"
                    :disabled="isSaving"
                    text="Cancel"
                    variant="outlined"
                    @click="cancelAdd('add-eval-type-btn')"
                  />
                </div>
              </v-form>
            </v-card-actions>
            <v-card-text class="pt-0">
              <div class="nannys-list overflow-y-auto">
                <v-data-table
                  id="evaluation-types-table"
                  density="compact"
                  disable-pagination
                  :headers="evaluationTypeHeaders"
                  hide-default-footer
                  :items="evaluationTypes"
                  :items-per-page="-1"
                  item-key="name"
                  must-sort
                  :sort-by="sortBy.evaluationTypes"
                  @update:sort-by="onSortEvaluationTypes"
                >
                  <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: _sortBy}">
                    <SortableTableHeader
                      :id="'eval-'"
                      :columns="columns"
                      :is-sorted="isSorted"
                      :on-sort="toggleSort"
                      :sort-desc="get(_sortBy, 'order') === 'desc'"
                      :sort-icon="getSortIcon"
                    />
                  </template>
                  <template #item.name="{item}">
                    <div class="d-flex justify-space-between">
                      <span>{{ item.name }}</span>
                      <v-btn
                        :id="`delete-eval-type-${item.id}-btn`"
                        class="font-weight-bold text-capitalize px-2 py-0"
                        color="primary"
                        :disabled="disableControls"
                        height="unset"
                        min-width="unset"
                        text="Delete"
                        variant="text"
                        @click.stop="() => listStore.confirmDeleteEvaluationType(item)"
                      />
                    </div>
                  </template>
                </v-data-table>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" lg="6">
          <v-card
            class="mr-4"
            min-width="fit-content"
          >
            <v-card-title
              id="manually-added-instructors-title"
              tabindex="-1"
            >
              Manually Added Instructors
            </v-card-title>
            <v-card-actions>
              <v-btn
                v-if="!isAddingInstructor"
                id="add-instructor-btn"
                class="font-weight-bold text-capitalize pl-2 my-1"
                color="primary"
                :disabled="disableControls"
                :prepend-icon="mdiPlusThick"
                text="Add new instructor"
                variant="text"
                @click="onClickAddInstructor"
              />
              <v-form
                v-if="isAddingInstructor"
                class="ml-8 w-100"
                @submit.prevent="onSubmitAddInstructor"
              >
                <label for="input-instructor-uid" class="form-label">
                  UID
                </label>
                <v-text-field
                  id="input-instructor-uid"
                  v-model="newInstructor.uid"
                  class="mt-1"
                  color="primary"
                  density="compact"
                  :disabled="isSaving"
                  hide-details="auto"
                  maxlength="12"
                  required
                  :rules="rules.numeric"
                  variant="outlined"
                  width="160"
                />
                <div class="mt-2">
                  <label for="input-instructor-csid" class="form-label">
                    CSID
                  </label>
                  <v-text-field
                    id="input-instructor-csid"
                    v-model="newInstructor.csid"
                    class="mt-1"
                    color="primary"
                    density="compact"
                    :disabled="isSaving"
                    hide-details="auto"
                    maxlength="24"
                    variant="outlined"
                    :rules="rules.csid"
                    width="240"
                  />
                </div>
                <div class="mt-2">
                  <label for="input-instructor-first-name" class="form-label">
                    First name
                  </label>
                  <v-text-field
                    id="input-instructor-first-name"
                    v-model="newInstructor.firstName"
                    class="mt-1"
                    color="primary"
                    density="compact"
                    :disabled="isSaving"
                    hide-details="auto"
                    variant="outlined"
                    width="240"
                  />
                </div>
                <div class="mt-2">
                  <label for="input-instructor-last-name" class="form-label">
                    Last name
                  </label>
                  <v-text-field
                    id="input-instructor-last-name"
                    v-model="newInstructor.lastName"
                    class="mt-1"
                    color="primary"
                    density="compact"
                    :disabled="isSaving"
                    hide-details="auto"
                    required
                    variant="outlined"
                    width="240"
                  />
                </div>
                <div class="mt-2">
                  <label for="input-instructor-last-name" class="form-label">
                    Email
                  </label>
                  <v-text-field
                    id="input-instructor-email"
                    v-model="newInstructor.emailAddress"
                    class="mt-1"
                    color="primary"
                    density="compact"
                    :disabled="isSaving"
                    hide-details="auto"
                    required
                    :rules="rules.email"
                    variant="outlined"
                    width="360"
                  />
                </div>
                <div class="mt-3">
                  <ProgressButton
                    id="save-instructor-btn"
                    :action="onSubmitAddInstructor"
                    class="mr-2"
                    :disabled="!isValid(newInstructor.uid, rules.numeric) || !isValid(newInstructor.csid, rules.csid) || !trim(newInstructor.lastName) || !isValid(newInstructor.emailAddress, rules.email) || isSaving"
                    :in-progress="isSaving"
                    :text="isSaving ? 'Saving' : 'Save'"
                  />
                  <v-btn
                    id="cancel-save-instructor-btn"
                    class="text-capitalize ml-1"
                    :disabled="isSaving"
                    text="Cancel"
                    variant="outlined"
                    @click="cancelAdd('add-instructor-btn')"
                  />
                </div>
              </v-form>
            </v-card-actions>
            <v-card-text>
              <div class="nannys-list overflow-y-auto">
                <v-data-table
                  id="instructors-table"
                  :cell-props="{
                    class: 'font-size-12 pl-0 pr-1 vertical-baseline'
                  }"
                  density="compact"
                  :headers="instructorHeaders"
                  hide-default-footer
                  :items="instructors"
                  :items-per-page="-1"
                  :sort-by="sortBy.instructors"
                  @update:sort-by="onSortInstructors"
                >
                  <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: _sortBy}">
                    <SortableTableHeader
                      :id="'instructor-'"
                      :columns="columns"
                      :is-sorted="isSorted"
                      :on-sort="toggleSort"
                      :sort-desc="_sortBy.order === 'desc'"
                      :sort-icon="getSortIcon"
                    />
                  </template>
                  <template #item.delete="{ item }">
                    <v-btn
                      :id="`delete-instructor-${item.uid}-btn`"
                      aria-label="Delete"
                      class="font-weight-bold text-capitalize"
                      color="error"
                      :disabled="disableControls"
                      :icon="mdiTrashCan"
                      title="Delete"
                      variant="text"
                      @click.stop="() => listStore.confirmDeleteInstructor(item)"
                    />
                  </template>
                  <template #no-data>
                    <div class="text-muted my-5">
                      No manually added instructors
                    </div>
                  </template>
                </v-data-table>
              </div>
            </v-card-text>
          </v-card>
          <v-card class="mr-4 mt-6 pa-3">
            <v-card-title>Service Announcement</v-card-title>
            <EditServiceAnnouncement />
          </v-card>
          <v-card class="mr-4 mt-6 pa-3">
            <v-card-title>Automatically Publish</v-card-title>
            <v-card-text class="pt-0">
              <span v-if="config.scheduleLochRefresh">
                When enabled, publication will run daily at
                {{ `${String(config.scheduleLochRefresh.hour).padStart(2, '0')}:${String(config.scheduleLochRefresh.minute).padStart(2, '0')}` }}
                local time, immediately before loch refresh.
              </span>
              <span v-if="!config.scheduleLochRefresh">
                Nightly loch refresh must be scheduled in app configs to enable auto-publish.
              </span>
              <v-switch
                id="auto-publish-enabled"
                v-model="autoPublishEnabled"
                :aria-describedby="undefined"
                :aria-label="`Auto-publish is ${autoPublishEnabled ? 'enabled' : 'disabled'}`"
                class="mt-3 mx-3"
                color="success"
                density="compact"
                :disabled="!config.scheduleLochRefresh"
                hide-details
                :label="autoPublishEnabled ? 'Enabled' : 'Disabled'"
                @change="toggleAutoPublishEnabled(autoPublishEnabled)"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <ConfirmDialog
      :confirm-button-label="isDeleting ? 'Deleting' : 'Delete'"
      :disabled="disableControls"
      :is-open="isConfirming"
      :is-saving="isDeleting"
      :on-click-cancel="cancelDelete"
      :on-click-confirm="confirmDelete"
      :text="`Are you sure you want to delete ${get(listStore.itemToDelete, 'name')}?`"
      :title="`Delete ${get(listStore.itemToDelete, 'description')}?`"
    />
  </div>
</template>

<script setup>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement'
import PageHeader from '@/components/util/PageHeader'
import ProgressButton from '@/components/util/ProgressButton.vue'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {get, find, size, trim} from 'lodash'
import {getAutoPublishStatus, setAutoPublishStatus} from '@/api/config'
import {mdiPlusThick, mdiTrashCan} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useTheme} from 'vuetify'
import {useListManagementStore} from '@/stores/list-management-session'

const contextStore = useContextStore()
const listStore = useListManagementStore()

const autoPublishEnabled = ref(undefined)
const config = contextStore.config
const {
  departmentForms,
  disableControls,
  evaluationTypes,
  instructors,
  isAddingDepartmentForm,
  isAddingEvaluationType,
  isAddingInstructor,
  isConfirming,
  isSaving
} = storeToRefs(listStore)
const departmentFormHeaders = [
  {key: 'name', class: 'pl-3', sortable: true, title: 'Form Name', value: 'name'}
]
const evaluationTypeHeaders = [
  {key: 'name', class: 'pl-3', sortable: true, title: 'Type Name', value: 'name'}
]
const instructorHeaders = [
  {key: 'uid', class: 'pl-0 pr-2', sortable: true, title: 'UID', value: 'uid'},
  {key: 'csid', class: 'pl-0 pr-2', sortable: true, title: 'SID', value: 'csid'},
  {key: 'firstName', class: 'pl-0 pr-2', sortable: true, title: 'First Name', value: 'firstName'},
  {key: 'lastName', class: 'pl-0 pr-2', sortable: true, title: 'Last Name', value: 'lastName'},
  {key: 'email', class: 'pl-0 pr-2', sortable: true, title: 'Email', value: 'email'},
  {key: 'delete', class: 'pl-0 pr-2', sortable: false, title: '', value: 'delete'}
]
const isDeleting = ref(false)
const newInstructor = ref(null)
const newItemName = ref(null)
const rules = {
  csid: [v => !trim(v) || !/[^\d]/.test(v) || 'Number required'],
  email: [
    v => !!v || 'E-mail is required',
    v => /.+@.+\..+/.test(v) || 'Requires a valid email',
  ],
  numeric: [v => !/[^\d]/.test(v) || 'Number required']
}
const sortBy = ref({
  departmentForms: [{key: 'name', order: 'asc'}],
  evaluationTypes: [{key: 'name', order: 'asc'}],
  instructors: [{key: 'uid', order: 'asc'}]
})
const theme = useTheme()

onMounted(() => {
  contextStore.loadingStart()
  resetNewInstructor()
  listStore.init().then(() => {
    contextStore.loadingComplete('List Management')
    putFocusNextTick('page-title')
  })
  getAutoPublishStatus().then(data => {
    autoPublishEnabled.value = data.enabled
  })
})

const afterDelete = deletedItem => {
  listStore.setDisableControls(false)
  alertScreenReader(`Deleted ${deletedItem.description} ${deletedItem.name}.`)
}

const cancelAdd = elementId => {
  newItemName.value = ''
  resetNewInstructor()
  listStore.reset()
  alertScreenReader('Canceled. Nothing saved.')
  putFocusNextTick(elementId)
}

const cancelDelete = () => {
  putFocusNextTick(listStore.itemToDelete.elementId)
  listStore.reset()
  alertScreenReader('Canceled. Nothing deleted.')
}

const confirmDelete = () => {
  isDeleting.value = true
  listStore.setDisableControls(true)
  listStore.onDelete().then(deletedItem => {
    afterDelete(deletedItem)
    isDeleting.value = false
  })
}

const isValid = (value, rules) => rules.every(rule => rule(value) === true)

const onClickAddDepartmentForm = () => {
  listStore.setAddingDepartmentForm().then(() => {
    newItemName.value = ''
    putFocusNextTick('input-dept-form-name')
  })
}

const onClickAddEvaluationType = () => {
  listStore.setAddingEvaluationType().then(() => {
    newItemName.value = ''
    putFocusNextTick('input-eval-type-name')
  })
}

const onClickAddInstructor = () => {
  listStore.setAddingInstructor().then(() => {
    resetNewInstructor()
    putFocusNextTick('input-instructor-uid')
  })
}

const onSortDepartmentForms = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(departmentFormHeaders, {key: key})
  const order = primarySortBy[0].order
  sortBy.value.departmentForms = primarySortBy
  if (header) {
    alertScreenReader(`Sorted department forms by ${header.ariaLabel || header.title}, ${order}ending`)
  }
}
const onSortEvaluationTypes = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(evaluationTypeHeaders, {key: key})
  const order = primarySortBy[0].order
  sortBy.value.evaluationTypes = primarySortBy
  if (header) {
    alertScreenReader(`Sorted evaluation types by ${header.ariaLabel || header.title}, ${order}ending`)
  }
}
const onSortInstructors = primarySortBy => {
  if (size(primarySortBy)) {
    const key = primarySortBy[0].key
    const header = find(instructorHeaders, {key: key})
    const order = primarySortBy[0].order
    sortBy.value.instructors = primarySortBy
    if (header) {
      alertScreenReader(`Sorted instructors by ${header.ariaLabel || header.title}, ${order}ending`)
    }
  } else {
    alertScreenReader('Default sort order restored to instructors.')
  }
}

const onSubmitAddDepartmentForm = () => {
  if (newItemName.value) {
    listStore.addDepartmentForm(newItemName.value).then(() => {
      alertScreenReader(`Created department form ${newItemName.value}.`)
      newItemName.value = ''
      putFocusNextTick('add-dept-form-btn')
    })
  }
}

const onSubmitAddInstructor = () => {
  if (newInstructor.value) {
    listStore.addInstructor(newInstructor.value).then(() => {
      alertScreenReader(`Added instructor with UID ${newInstructor.value.uid}.`)
      resetNewInstructor()
      putFocusNextTick('add-instructor-btn')
    })
  }
}

const onSubmitAddEvaluationType = () => {
  if (newItemName.value) {
    listStore.addEvaluationType(newItemName.value).then(() => {
      alertScreenReader(`Created evaluation type ${newItemName.value}.`)
      newItemName.value = ''
      putFocusNextTick('add-eval-type-btn')
    })
  }
}

const resetNewInstructor = () => {
  newInstructor.value = {
    'csid': null,
    'emailAddress': null,
    'firstName': null,
    'lastName': null,
    'uid': null
  }
}

const toggleAutoPublishEnabled = enabled => {
  setAutoPublishStatus(enabled).then(data => {
    autoPublishEnabled.value = data.enabled
    alertScreenReader(`Auto-publish ${autoPublishEnabled.value ? 'enabled' : 'disabled'}`)
  })
}
</script>

<style scoped>
.nannys-list {
  max-height: 500px;
}
</style>

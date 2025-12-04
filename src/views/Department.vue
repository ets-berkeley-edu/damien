<template>
  <div>
    <PageHeader>
      <div class="align-center d-flex justify-space-between">
        <div v-if="get(department, 'deptName')">
          {{ department.deptName }}
          <span v-if="size(getCatalogListings(department))">({{ getCatalogListings(department).join(', ') }})</span>
          <span v-if="contextStore.selectedTermName" class="mr-2">&mdash;{{ contextStore.selectedTermName }}</span>
        </div>
      </div>
      <template #append>
        <TermSelect :term-ids="get(department, 'enrolledTerms')" />
      </template>
    </PageHeader>
    <div v-if="!contextStore.loading">
      <div v-if="!currentUser.isAdmin && currentUser.departments.length > 1" class="mb-2">
        <v-menu rounded="lg">
          <template #activator="{props: defineProps}">
            <v-btn
              id="change-department-menu"
              :append-icon="mdiChevronDown"
              color="primary"
              text="Change Department"
              variant="flat"
              v-bind="defineProps"
            />
          </template>
          <v-list>
            <template
              v-for="option in sortBy(currentUser.departments, 'name')"
              :key="option.id"
            >
              <v-list-item
                v-if="option.id !== department.id"
                :id="`department-${option.id}-option`"
                @click="() => onChangeDepartment(option.id)"
              >
                <v-list-item-title>{{ option.name }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-list>
        </v-menu>
      </div>
      <v-container class="mx-0 pb-2 pt-1 px-0" fluid>
        <v-row justify="start">
          <v-col cols="12" lg="6">
            <div aria-labelledby="department-contacts-header" class="border-sm pa-3" role="region">
              <v-expansion-panels
                v-model="contactsPanel"
                flat
                @update:model-value="v => toggleCollapseAllContacts(isUndefined(v))"
              >
                <v-expansion-panel class="bg-transparent">
                  <template #default>
                    <div class="d-flex align-center flex-wrap justify-space-between">
                      <h2 id="department-contacts-header" class="ml-2">Department Contacts</h2>
                      <v-expansion-panel-title
                        class="ml-auto px-2 px-sm-6 py-0 w-fit-content"
                        hide-actions
                      >
                        <template #default="{expanded}">
                          <span v-if="!expanded">
                            Expand
                            <v-icon
                              class="rotate-180"
                              :icon="mdiPlusBoxMultipleOutline"
                              aria-hidden="true"
                            />
                          </span>
                          <span v-if="expanded">
                            Collapse All
                            <v-icon
                              class="rotate-180 ml-1"
                              :icon="mdiMinusBoxMultipleOutline"
                              aria-hidden="true"
                            />
                          </span>
                          <span class="sr-only">department contacts</span>
                        </template>
                      </v-expansion-panel-title>
                    </div>
                    <v-expansion-panel-text class="department-contacts">
                      <v-expansion-panels
                        v-model="contactDetailsPanel"
                        flat
                        focusable
                        hover
                        multiple
                        tile
                      >
                        <DepartmentContact
                          v-for="(contact, index) in contacts"
                          :key="contact.id"
                          :contact="contact"
                          :index="index"
                          :is-expanded="includes(contactDetailsPanel, index)"
                        />
                      </v-expansion-panels>
                    </v-expansion-panel-text>
                  </template>
                </v-expansion-panel>
              </v-expansion-panels>
              <div v-if="contextStore.currentUser.isAdmin" class="pt-2">
                <v-btn
                  v-if="!isCreatingNotification"
                  id="open-notification-form-btn"
                  class="department-contacts-btn ml-2 text-capitalize"
                  color="tertiary"
                  :disabled="disableControls || isEmpty(contacts)"
                  text="Send notification"
                  @click="() => isCreatingNotification = true"
                />
                <NotificationForm
                  v-if="isCreatingNotification"
                  :after-send="afterSendNotification"
                  class="bg-surface-light border-sm"
                  :on-cancel="cancelSendNotification"
                  :recipients="[notificationRecipients]"
                />
              </div>
              <div v-if="currentUser.isAdmin" class="pt-3">
                <v-btn
                  v-if="!isAddingContact"
                  id="add-dept-contact-btn"
                  class="department-contacts-btn font-weight-bold ml-2"
                  color="primary"
                  :disabled="disableControls"
                  :prepend-icon="mdiPlusThick"
                  text="Add Contact"
                  variant="text"
                  @click="onClickAddContact"
                />
                <EditDepartmentContact
                  v-if="isAddingContact"
                  :id="`add-department-contact`"
                  :after-save="afterAddContact"
                  :aria-label="pendingDepartmentContactName ? `Edit ${pendingDepartmentContactName}` : undefined"
                  :on-cancel="onCancelAddContact"
                  :role="pendingDepartmentContactName ? 'region' : 'none'"
                  @department-contact-selected="fullName => pendingDepartmentContactName = fullName"
                />
              </div>
            </div>
          </v-col>
          <v-col cols="12" lg="6">
            <div aria-labelledby="notes-title" class="border-sm px-5 py-3" role="region">
              <DepartmentNote />
            </div>
          </v-col>
        </v-row>
      </v-container>
      <div aria-labelledby="evaluations-header" class="border-sm mt-3 position-relative" role="region">
        <h2 id="evaluations-header" class="sr-only">Evaluations</h2>
        <EvaluationTable />
      </div>
    </div>
    <v-dialog v-model="showTheOmenPoster" theme="dark">
      <v-card class="bg-black ma-auto pa-0 overflow-visible">
        <v-toolbar color="secondary" density="compact">
          <v-spacer />
          <v-btn
            id="hide-omen-poster-btn"
            class="font-weight-bold"
            :icon="mdiClose"
            title="Close dialog"
            @click="() => departmentStore.setShowTheOmenPoster(false)"
          />
        </v-toolbar>
        <v-card-text class="text-center px-0 pb-0 pt-2">
          <img
            alt="Movie poster of The Omen"
            class="omen-poster-img"
            src="@/assets/omen_poster.png"
          >
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {filter as _filter, get, includes, isEmpty, isUndefined, size, sortBy} from 'lodash'
import {mdiChevronDown, mdiClose, mdiMinusBoxMultipleOutline, mdiPlusBoxMultipleOutline, mdiPlusThick} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useRoute, useRouter} from 'vue-router'
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import NotificationForm from '@/components/admin/NotificationForm'
import PageHeader from '@/components/util/PageHeader'
import TermSelect from '@/components/util/TermSelect'
import {NUMBER_OF_THE_BEAST, useDepartmentStore} from '@/stores/department/department-edit-session'
import {alertScreenReader, getCatalogListings, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const contactDetailsPanel = ref([])
const contactsPanel = ref(undefined)
const currentUser = contextStore.currentUser
const departmentId = ref(undefined)
const departmentStore = useDepartmentStore()
const isAddingContact = ref(false)
const isCreatingNotification = ref(false)
const pendingDepartmentContactName = ref()
const route = useRoute()
const router = useRouter()
const {contacts, department, disableControls, showTheOmenPoster} = storeToRefs(departmentStore)

const notificationRecipients = computed(() => {
  return {
    deptName: department.value.deptName,
    deptId: department.value.id,
    recipients: _filter(contacts.value, 'canReceiveCommunications')
  }
})

watch(isAddingContact, () => {
  departmentStore.setDisableControls(isAddingContact.value)
})

watch(isCreatingNotification, () => {
  departmentStore.setDisableControls(isCreatingNotification.value)
})

onMounted(() => {
  departmentId.value = get(route, 'params.departmentId')
  refresh()
})

const afterAddContact = contactName => {
  isAddingContact.value = false
  pendingDepartmentContactName.value = undefined
  contactsPanel.value = 0
  alertScreenReader(`Added ${contactName} to department contacts.`)
  putFocusNextTick('add-dept-contact-btn')
}

const afterSendNotification = () => {
  isCreatingNotification.value = false
  contextStore.snackbarOpen('Notification sent.')
  putFocusNextTick('open-notification-form-btn')
}

const cancelSendNotification = () => {
  isCreatingNotification.value = false
  alertScreenReader('Canceled notification.')
  putFocusNextTick('open-notification-form-btn')
}

const onCancelAddContact = () => {
  isAddingContact.value = false
  pendingDepartmentContactName.value = undefined
  alertScreenReader('Canceled. Nothing saved.')
  putFocusNextTick('add-dept-contact-btn')
}

const onChangeDepartment = id => {
  router.push({
    path: `/department/${id}`,
    query: route.query,
    replace: true
  })
}

const onClickAddContact = () => {
  isAddingContact.value = true
  putFocusNextTick('person-lookup-input')
}

const refresh = () => {
  contextStore.loadingStart()
  departmentStore.init(departmentId.value).then(() => {
    departmentStore.setShowTheOmenPoster(route.query.n === NUMBER_OF_THE_BEAST)
    contextStore.loadingComplete()
  })
}

const toggleCollapseAllContacts = isCollapsed => {
  if (isCollapsed) {
    contactDetailsPanel.value = []
  }
}
</script>

<style>
.department-contacts > .v-expansion-panel-text__wrapper {
  padding: 8px;
}
</style>

<style scoped>
.department-contacts-btn {
  width: 10.125rem;
}
.omen-poster-img {
  height: calc(100vh - 100px);
}
</style>

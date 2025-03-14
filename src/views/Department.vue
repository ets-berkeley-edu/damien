<template>
  <div class="page-margins">
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
          <v-col cols="12" md="6">
            <div class="border-sm pa-3">
              <v-expansion-panels
                v-model="contactsPanel"
                flat
                @update:model-value="v => toggleCollapseAllContacts(isUndefined(v))"
              >
                <v-expansion-panel class="bg-transparent">
                  <template #default>
                    <div class="d-flex align-center flex-wrap justify-space-between">
                      <h2 class="ml-2">Department Contacts</h2>
                      <v-expansion-panel-title
                        class="px-2 px-sm-6 py-0 w-fit-content"
                        hide-actions
                      >
                        <template #default="{expanded}">
                          <span v-if="!expanded">
                            Expand
                            <v-icon
                              class="rotate-180"
                              :icon="mdiPlusBoxMultipleOutline"
                            />
                          </span>
                          <span v-if="expanded">
                            Collapse All
                            <v-icon class="rotate-180 ml-1" :icon="mdiMinusBoxMultipleOutline" />
                          </span>
                        </template>
                      </v-expansion-panel-title>
                    </div>
                    <v-expansion-panel-text>
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
                  class="ml-2 text-capitalize"
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
                  class="font-weight-bold ml-2"
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
                  :after-save="afterSaveContact"
                  :on-cancel="onCancelAddContact"
                />
              </div>
            </div>
          </v-col>
          <v-col cols="12" md="6">
            <div class="border-sm px-5 py-3">
              <DepartmentNote />
            </div>
          </v-col>
        </v-row>
      </v-container>
      <div class="border-sm mt-3 position-relative">
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
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import NotificationForm from '@/components/admin/NotificationForm'
import PageHeader from '@/components/util/PageHeader'
import TermSelect from '@/components/util/TermSelect'
import {NUMBER_OF_THE_BEAST, useDepartmentStore} from '@/stores/department/department-edit-session'
import {alertScreenReader, getCatalogListings, putFocusNextTick} from '@/lib/utils'
import {computed, onMounted, ref, watch} from 'vue'
import {filter as _filter, get, includes, isEmpty, isUndefined, size, sortBy} from 'lodash'
import {mdiChevronDown, mdiClose, mdiMinusBoxMultipleOutline, mdiPlusBoxMultipleOutline, mdiPlusThick} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const contactDetailsPanel = ref([])
const contactsPanel = ref(undefined)
const currentUser = contextStore.currentUser
const departmentId = ref(undefined)
const departmentStore = useDepartmentStore()
const isAddingContact = ref(false)
const isCreatingNotification = ref(false)
const route = useRoute()
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

const afterSaveContact = () => {
  isAddingContact.value = false
  contactsPanel.value = 0
  alertScreenReader('Contact saved.')
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
  alertScreenReader('Canceled. Nothing saved.')
  putFocusNextTick('add-dept-contact-btn')
}

const onChangeDepartment = id => {
  departmentId.value = id
  refresh()
}

const onClickAddContact = () => {
  isAddingContact.value = true
  putFocusNextTick('person-lookup-input')
}

const refresh = () => {
  contextStore.loadingStart()
  alertScreenReader(`Loading ${contextStore.selectedTermName}`)
  departmentStore.init(departmentId.value).then(department => {
    departmentStore.setShowTheOmenPoster(route.query.n === NUMBER_OF_THE_BEAST)
    contextStore.loadingComplete(`${department.deptName} ${contextStore.selectedTermName}`)
  })
}

const toggleCollapseAllContacts = isCollapsed => {
  if (isCollapsed) {
    contactDetailsPanel.value = []
  }
}
</script>

<style scoped>
.omen-poster-img {
  height: calc(100vh - 100px);
}
.w-fit-content {
  width: fit-content;
}
</style>

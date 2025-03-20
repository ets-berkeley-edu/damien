<template>
  <v-expansion-panel :id="`department-contact-${contact.id}`" class="panel-width">
    <v-expansion-panel-title :id="`department-contact-${contact.id}-btn`" class="pa-2 rounded-b-0 height-unset">
      <span v-if="isEditing" class="sr-only">Edit</span>
      <div :id="`dept-contact-${contact.id}-name`" class="font-weight-bold">{{ fullName }}</div>
    </v-expansion-panel-title>
    <v-expansion-panel-text
      :aria-labelledby="`department-contact-${contact.id}-btn`"
      class="edit-contact-container"
      role="region"
    >
      <v-container
        v-if="!isEditing"
        :id="`dept-contact-${contact.id}-details`"
        class="pb-0 px-0"
        fluid
      >
        <v-row :id="`dept-contact-${contact.id}-email`">
          <v-col class="px-2 pt-1" cols="12">{{ contact.email }}</v-col>
        </v-row>
        <v-row :id="`dept-contact-${contact.id}-notifications`" class="mt-0">
          <v-col class="text-right px-1" cols="1">
            <v-icon
              :class="contact.canReceiveCommunications ? 'text-success' : 'text-muted'"
              :icon="contact.canReceiveCommunications ? mdiCheckCircle : mdiMinusCircle"
              size="small"
            />
          </v-col>
          <v-col align-self="center" class="font-italic font-size-14 pl-0" cols="11">
            {{ `${contact.canReceiveCommunications ? 'Does' : 'Does not'} receive notifications` }}
          </v-col>
        </v-row>
        <v-row :id="`dept-contact-${contact.id}-permissions`" class="mt-0">
          <v-col class="text-right px-1" cols="1">
            <v-icon
              :class="contact.canViewReports ? 'text-success' : 'text-muted'"
              :icon="contact.canViewReports ? mdiCheckCircle : mdiMinusCircle"
              size="small"
            />
          </v-col>
          <v-col align-self="center" class="font-italic font-size-14 pl-0" cols="11">
            <span v-if="!contact.canViewReports">Does not have access to Blue</span>
            <span v-if="contact.canViewReports">
              {{ `Can view reports ${contact.canViewResponseRates ? 'and response rates ' : ''}in Blue` }}
            </span>
          </v-col>
        </v-row>
        <v-row :id="`dept-contact-${contact.id}-deptForms`" class="mt-0">
          <v-col cols="12">
            <div class="d-flex flex-wrap">
              <div v-for="(form, formIndex) in departmentForms" :key="form.id" class="pb-1 pr-1">
                <v-chip
                  :id="`dept-contact-${contact.id}-form-${formIndex}`"
                  class="font-weight-bold border-sm"
                  color="success"
                  :text="form.name"
                />
              </div>
            </div>
          </v-col>
        </v-row>
        <v-row class="mt-2" no-gutters>
          <v-col class="pl-0" cols="12">
            <v-toolbar
              v-if="currentUser.isAdmin"
              :id="`dept-contact-${contact.id}-actions`"
              class="pl-0"
              color="surface"
              density="compact"
              flat
              height="unset"
              tag="div"
            >
              <v-btn
                :id="`edit-dept-contact-${contact.id}-btn`"
                :aria-label="`Edit ${fullName}`"
                class="font-weight-bold text-capitalize pa-0"
                color="primary"
                density="compact"
                :disabled="disableControls"
                text="Edit"
                variant="text"
                @click="() => isEditing = true"
              />
              <v-divider
                class="mx-1"
                role="presentation"
                thickness="2"
                vertical
              />
              <v-btn
                :id="`delete-dept-contact-${contact.id}-btn`"
                :aria-label="`Delete ${fullName}`"
                class="font-weight-bold text-capitalize pa-0"
                color="primary"
                density="compact"
                :disabled="disableControls"
                text="Delete"
                variant="text"
                @click.stop="() => isConfirming = true"
              />
              <ConfirmDialog
                :is-open="isConfirming"
                :is-saving="isDeleting"
                :on-click-cancel="onCancelDelete"
                :on-click-confirm="onDelete"
                :text="`Are you sure you want to remove ${fullName} as a department contact?`"
                :title="'Delete contact?'"
              />
            </v-toolbar>
          </v-col>
        </v-row>
      </v-container>
      <EditDepartmentContact
        v-if="isEditing"
        :id="`edit-department-contact-${contact.id}`"
        :after-save="afterSave"
        :contact="contact"
        :on-cancel="onCancelEdit"
      />
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import {computed, ref, watch} from 'vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {sortBy} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useDepartmentStore} from '@/stores/department/department-edit-session'
import {mdiCheckCircle, mdiMinusCircle} from '@mdi/js'
import {storeToRefs} from 'pinia'

const props = defineProps({
  contact: {
    required: true,
    type: Object
  },
  index: {
    required: true,
    type: Number
  },
  isExpanded: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()
const departmentStore = useDepartmentStore()
const {disableControls} = storeToRefs(departmentStore)

const currentUser = contextStore.currentUser
const departmentForms = computed(() => sortBy(props.contact.departmentForms, 'name'))
const fullName = computed(() => `${props.contact.firstName} ${props.contact.lastName}`)
const isConfirming = ref(false)
const isDeleting = ref(false)
const isEditing = ref(false)

watch(isConfirming, () => {
  departmentStore.setDisableControls(isConfirming.value)
})

watch(isDeleting, () => {
  departmentStore.setDisableControls(isDeleting.value)
})

watch(isEditing, () => {
  departmentStore.setDisableControls(isEditing.value)
})

watch(() => props.isExpanded, () => {
  if (!props.isExpanded) {
    isEditing.value = false
  }
})

const afterSave = contactName => {
  isEditing.value = false
  alertScreenReader(`Updated contact ${contactName}.`)
  putFocusNextTick(`edit-dept-contact-${props.contact.id}-btn`)
}

const onCancelDelete = () => {
  isConfirming.value = false
  alertScreenReader('Canceled. Nothing deleted.')
  putFocusNextTick(`delete-dept-contact-${props.contact.id}-btn`)
}

const onCancelEdit = () => {
  isEditing.value = false
  alertScreenReader('Canceled. Nothing saved.')
  putFocusNextTick(`edit-dept-contact-${props.contact.id}-btn`)
}

const onDelete = () => {
  alertScreenReader('Deleting contact')
  isDeleting.value = true
  const nameOfDeleted = fullName.value
  departmentStore.deleteContact(props.contact.userId).then(() => {
    isConfirming.value = false
    isDeleting.value = false
    alertScreenReader(`Deleted contact ${nameOfDeleted}.`)
    putFocusNextTick('add-dept-contact-btn')
  })
}
</script>

<style scoped>
.edit-contact-container {
  border-radius: 0 0 4px 4px;
  border: 2px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.panel-width {
  min-width: 320px;
}
</style>

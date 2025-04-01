<template>
  <v-form
    v-model="valid"
    class="py-4"
    :class="{'bg-surface-variant': uid && !contact}"
    lazy-validation
  >
    <div v-if="!contact && !uid">
      <h3 id="add-contact-sub-header" class="form-title">
        Add Contact
      </h3>
      <PersonLookup
        class="my-2"
        :exclude-uids="map(contacts, 'uid')"
        label="Contact"
        label-class="sr-only"
        list-label="Suggested Contacts List"
        :on-key-down-esc="onCancel"
        :on-select-result="onSelectSearchResult"
      />
    </div>
    <div v-if="uid" class="department-contact-form">
      <h3 id="contact-sub-header">
        <span class="sr-only">Contact: </span>{{ fullName }} ({{ uid }})
      </h3>
      <div class="pt-2">
        <label :for="`input-email-${contactId}`" class="form-label">
          Email Address
        </label>
        <v-text-field
          :id="`input-email-${contactId}`"
          v-model="email"
          class="mt-1"
          density="compact"
          :disabled="isSaving"
          variant="outlined"
          required
          :rules="emailRules"
        />
      </div>
      <div class="pt-2">
        <label :for="`checkbox-communications-${contactId}`" class="form-label">
          Communications
        </label>
        <div class="align-center d-flex">
          <v-checkbox
            :id="`checkbox-communications-${contactId}`"
            v-model="canReceiveCommunications"
            :aria-describedby="undefined"
            aria-label="Receive notifications"
            class="checkbox-override rounded-sm"
            color="primary"
            density="comfortable"
            :disabled="isSaving"
            hide-details
            role="checkbox"
            tabindex="0"
          />
          <label class="v-label opacity-100 ml-1 text-wrap" :for="`checkbox-communications-${contactId}`">
            Receive notifications
          </label>
        </div>
      </div>
      <div class="pt-3">
        <label :for="`checkbox-communications-${contactId}`" class="form-label">
          Blue Access
        </label>
        <v-radio-group
          v-model="permissions"
          :aria-describedby="undefined"
          color="primary"
          column
          density="comfortable"
          hide-details
          mandatory
        >
          <v-radio
            :id="`radio-no-blue-${contactId}`"
            :aria-checked="isNil(permissions)"
            :disabled="isSaving"
            label="No access to Blue"
            :value="null"
          />
          <v-radio
            :id="`radio-reports-only-${contactId}`"
            :aria-checked="permissions === 'reports_only'"
            :disabled="isSaving"
            label="View reports"
            value="reports_only"
          />
          <v-radio
            :id="`radio-response-rates-${contactId}`"
            :aria-checked="permissions === 'response_rates'"
            :disabled="isSaving"
            label="View reports and response rates"
            value="response_rates"
          />
        </v-radio-group>
      </div>
      <div class="pt-3">
        <label :for="`select-department-forms-${contactId}`" class="form-label">
          Department Forms
        </label>
        <AccessibleCombobox
          :id-prefix="`select-department-forms-${contactId}`"
          :aria-live="undefined"
          clazz="mt-1"
          :custom-filter="filterDepartmentForms"
          :disabled="isSaving"
          :get-value="() => contactDepartmentForms"
          :item-count="departmentFormsCount - size(contactDepartmentForms)"
          :item-label="item => item.title"
          item-title="name"
          item-value="id"
          :items="availableDepartmentForms"
          label="Department Forms"
          list-label="Choose department forms"
          :set-value="addDepartmentForm"
        >
          <template #selection></template>
        </AccessibleCombobox>
        <div :id="`select-department-forms-${contactId}-desc`" class="py-1">
          <span class="sr-only">
            {{ isEmpty(contactDepartmentForms) ? 'No department forms selected' : `${oxfordJoin(map(contactDepartmentForms, 'name'))} selected` }}
          </span>
          <v-chip
            v-for="item in contactDepartmentForms"
            :id="`selected-deptForm-${item.id}-${contactId}`"
            :key="item.id"
            class="font-weight-bold ma-1"
            closable
            :close-label="`Remove ${item.name} from ${fullName}'s department forms`"
            color="secondary"
            density="compact"
            :disabled="isSaving"
            :text="item.name"
            variant="flat"
            @click:close="() => removeDepartmentForm(item.id)"
          />
        </div>
      </div>
    </div>
    <div class="mt-2">
      <ProgressButton
        :id="`save-dept-contact-${contactId}-btn`"
        :action="onSave"
        class="text-capitalize mr-2 mt-2"
        :disabled="!valid || !uid || isSaving"
        :in-progress="isSaving"
        text="Save"
      />
      <v-btn
        :id="`cancel-dept-contact-${contactId}-btn`"
        class="text-capitalize mt-2"
        :disabled="isSaving"
        text="Cancel"
        variant="outlined"
        @click.prevent="onCancel"
      />
    </div>
  </v-form>
</template>

<script setup>
import AccessibleCombobox from '@/components/util/AccessibleCombobox'
import PersonLookup from '@/components/admin/PersonLookup'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, oxfordJoin, putFocusNextTick} from '@/lib/utils'
import {cloneDeep, differenceBy, find, get, isEmpty, isNil, map, remove, size, some, sortBy, upperCase} from 'lodash'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {getUserDepartmentForms} from '@/api/user'
import {storeToRefs} from 'pinia'
import {useDepartmentStore} from '@/stores/department/department-edit-session'

const props = defineProps({
  afterSave: {
    required: true,
    type: Function
  },
  contact: {
    default: () => {},
    required: false,
    type: Object
  },
  onCancel: {
    required: true,
    type: Function
  }
})

const departmentStore = useDepartmentStore()

const {contacts} = storeToRefs(departmentStore)
const canReceiveCommunications = ref(true)
const csid = ref(undefined)
const contactDepartmentForms = ref([])
const departmentFormsCount = ref(0)
const email = ref(undefined)
const emailRules = [
  v => !!v || 'E-mail is required',
  v => /.+@.+\..+/.test(v) || 'E-mail must be valid'
]
const firstName = ref(undefined)
const isSaving = ref(false)
const lastName = ref(undefined)
const permissions = ref(undefined)
const uid = ref(undefined)
const userId = ref(undefined)
const valid = ref(true)

const availableDepartmentForms = computed(() => {
  return differenceBy(departmentStore.allDepartmentForms, contactDepartmentForms.value, item => item.name)
})
const contactId = computed(() => {
  return get(props.contact, 'uid', 'add-contact')
})
const fullName = computed(() => {
  return firstName.value && lastName.value ? `${firstName.value} ${lastName.value}`.trim() : ''
})

onMounted(() => {
  departmentFormsCount.value = size(departmentStore.allDepartmentForms)
  populateForm(props.contact)
})

onUnmounted(() => {
  departmentStore.setDisableControls(false)
})

const fetchUserDepartmentForms = uid => {
  getUserDepartmentForms(uid).then(data => {
    contactDepartmentForms.value = data
  })
}

const filterDepartmentForms = (value, queryText) => {
  return isEmpty(queryText) || upperCase(value).includes(upperCase(queryText))
}

const addDepartmentForm = departmentForm => {
  if (get(departmentForm, 'id') && some(availableDepartmentForms.value, {id: departmentForm.id})) {
    contactDepartmentForms.value.push(departmentForm)
  }
}

const onSave = () => {
  isSaving.value = true
  alertScreenReader('Saving')
  departmentStore.updateContact({
    canReceiveCommunications: canReceiveCommunications.value,
    canViewReports: permissions.value === 'reports_only',
    canViewResponseRates: permissions.value === 'response_rates',
    csid: csid.value,
    departmentForms: contactDepartmentForms.value,
    email: email.value,
    firstName: firstName.value,
    lastName: lastName.value,
    uid: uid.value,
    userId: userId.value
  }).then(() => {
    props.afterSave(fullName.value)
    isSaving.value = false
  })
}

const onSelectSearchResult = user => {
  populateForm(user)
  putFocusNextTick(`input-email-${contactId.value}`)
}

const populateForm = contact => {
  if (contact) {
    fetchUserDepartmentForms(contact.uid)
    csid.value = contact.csid
    contactDepartmentForms.value = cloneDeep(sortBy(contact.departmentForms, 'name'))
    email.value = contact.email
    firstName.value = contact.firstName
    lastName.value = contact.lastName
    uid.value = contact.uid
    userId.value = contact.userId
    if (contact.canReceiveCommunications !== undefined) {
      canReceiveCommunications.value = contact.canReceiveCommunications
    }
    permissions.value = contact.canViewReports ? (contact.canViewResponseRates ? 'response_rates' : 'reports_only') : null
    putFocusNextTick(`input-email-${contact.uid}`)
  } else {
    csid.value = null
    canReceiveCommunications.value = true
    contactDepartmentForms.value = []
    email.value = null
    firstName.value = null
    lastName.value = null
    permissions.value = null
    uid.value = null
    userId.value = null
    putFocusNextTick('person-lookup-input')
  }
}

const removeDepartmentForm = formId => {
  const form = find(contactDepartmentForms.value, {'id': formId})
  contactDepartmentForms.value = remove(contactDepartmentForms.value, f => f.id !== formId)
  alertScreenReader(`Removed ${form.name} from ${fullName.value} department forms.`)
  putFocusNextTick(`select-department-forms-${contactId.value}`)
}
</script>

<style>
.form-title {
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<style scoped>
.department-contact-form {
  z-index: 10;
}
.checkbox-override {
  min-width: 2.25rem;
}
</style>

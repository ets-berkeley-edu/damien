<template>
  <v-form class="pa-3">
    <div v-if="!contact">
      <label for="input-person-lookup-autocomplete" class="form-label">
        Person Lookup
      </label>
      <PersonLookup class="my-1" :on-select-result="onSelectSearchResult" />
    </div>
    <label :for="`input-first-name-${contactId}`" class="form-label">
      First Name
    </label>
    <v-text-field
      :id="`input-first-name-${contactId}`"
      v-model="firstName"
      class="mt-1"
      dense
      outlined
      required
    ></v-text-field>
    <label :for="`input-last-name-${contactId}`" class="form-label">
      Last Name
    </label>
    <v-text-field
      :id="`input-lase-name-${contactId}`"
      v-model="lastName"
      class="mt-1"
      dense
      outlined
      required
    ></v-text-field>
    <label :for="`input-email-${contactId}`" class="form-label">
      Email Address
    </label>
    <v-text-field
      :id="`input-email-${contactId}`"
      v-model="email"
      class="mt-1"
      dense
      outlined
      required
    ></v-text-field>
    <legend :for="`checkbox-communications-${contactId}`" class="form-label">
      Communications
    </legend>
    <v-checkbox
      :id="`checkbox-communications-${contactId}`"
      v-model="canReceiveCommunications"
      class="mt-1"
      dense
      label="Receive notifications"
    >
    </v-checkbox>
    <legend :for="`checkbox-communications-${contactId}`" class="form-label">
      Blue Access
    </legend>
    <v-radio-group
      v-model="permissions"
      class="mt-1"
      column
      dense
      mandatory
    >
      <v-radio
        :id="`radio-no-blue-${contactId}`"
        value="none"
        class="mb-1"
        color="secondary"
        label="No access to Blue"
      ></v-radio>
      <v-radio
        :id="`radio-reports-only-${contactId}`"
        value="reports only"
        class="mb-1"
        color="secondary"
        label="View reports"
      ></v-radio>
      <v-radio
        :id="`radio-response-rates-${contactId}`"
        value="reports and response rates"
        class="mb-1"
        color="secondary"
        label="View reports and response rates"
      ></v-radio>
    </v-radio-group>
    <v-btn
      :id="`save-dept-contact-${contactId}-btn`"
      class="text-capitalize mr-2"
      color="secondary"
      :disabled="disableControls"
      elevation="2"
      @click="onSave"
    >
      Save
    </v-btn>
    <v-btn
      :id="`cancel-dept-contact-${contactId}-btn`"
      class="text-capitalize ml-1"
      color="secondary"
      :disabled="disableControls"
      elevation="2"
      outlined
      text
      @click="onCancel"
    >
      Cancel
    </v-btn>
  </v-form>
</template>

<script>
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'

export default {
  name: 'EditDepartmentContact',
  mixins: [DepartmentEditSession],
  components: {PersonLookup},
  props: {
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
  },
  data: () => ({
    canReceiveCommunications: false,
    email: undefined,
    firstName: undefined,
    lastName: undefined,
    permissions: undefined,
    userId: undefined
  }),
  computed: {
    contactId() {
      return this.$_.get(this.contact, 'uid', 'add-contact')
    }
  },
  created() {
    this.populateForm(this.contact)
  },
  methods: {
    onSave() {
      this.updateContact({
        'canReceiveCommunications': this.canReceiveCommunications,
        'canViewResponseRates': this.permissions === 'reports and response rates',
        'email': this.email,
        'firstName': this.firstName,
        'lastName': this.lastName,
        'userId': this.userId
      }).then(this.afterSave)
    },
    onSelectSearchResult(user) {
      this.populateForm(user)
    },
    populateForm(contact) {
      if (contact) {
        this.canReceiveCommunications = contact.canReceiveCommunications
        this.canViewResponseRates = contact.canViewResponseRates
        this.email = contact.email
        this.firstName = contact.firstName
        this.lastName = contact.lastName
        this.permissions = contact.canViewResponseRates ? 'reports and response rates' : 'reports only'
        this.userId = contact.id

        this.$putFocusNextTick(`input-first-name-${this.contactId}`)
      } else {
        this.$putFocusNextTick('input-person-lookup-autocomplete')
      }
    }
  }
}
</script>

<style scoped>
.form-label {
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
<template>
  <v-form
    v-model="valid"
    class="pa-3"
    lazy-validation
  >
    <div v-if="!contact">
      <label for="input-person-lookup-autocomplete" class="form-label">
        Person Lookup
      </label>
      <PersonLookup
        class="mt-1 mb-4"
        :exclude-uids="$_.map(contacts, 'uid')"
        :on-select-result="onSelectSearchResult"
      />
    </div>
    <div v-if="fullName" class="mb-4">
      <strong>{{ fullName }}</strong>
    </div>
    <div v-if="uid">
      <label :for="`input-email-${contactId}`" class="form-label">
        Email Address
      </label>
      <v-text-field
        :id="`input-email-${contactId}`"
        v-model="email"
        class="mt-1"
        color="secondary"
        dense
        :disabled="disableControls"
        outlined
        required
        :rules="emailRules"
      ></v-text-field>
      <legend :for="`checkbox-communications-${contactId}`" class="form-label">
        Communications
      </legend>
      <v-checkbox
        :id="`checkbox-communications-${contactId}`"
        v-model="canReceiveCommunications"
        class="mt-1"
        color="secondary"
        dense
        :disabled="disableControls"
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
        :disabled="disableControls"
        mandatory
      >
        <v-radio
          :id="`radio-no-blue-${contactId}`"
          :value="null"
          class="mb-1"
          color="secondary"
          label="No access to Blue"
        ></v-radio>
        <v-radio
          :id="`radio-reports-only-${contactId}`"
          value="reports_only"
          class="mb-1"
          color="secondary"
          label="View reports"
        ></v-radio>
        <v-radio
          :id="`radio-response-rates-${contactId}`"
          value="response_rates"
          class="mb-1"
          color="secondary"
          label="View reports and response rates"
        ></v-radio>
      </v-radio-group>
    </div>
    <v-btn
      :id="`save-dept-contact-${contactId}-btn`"
      class="text-capitalize mr-2"
      color="secondary"
      :disabled="disableControls || !valid || !uid"
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
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'

export default {
  name: 'EditDepartmentContact',
  mixins: [Context, DepartmentEditSession],
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
    canReceiveCommunications: true,
    csid: undefined,
    email: undefined,
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    firstName: undefined,
    lastName: undefined,
    permissions: undefined,
    uid: undefined,
    userId: undefined,
    valid: true
  }),
  computed: {
    contactId() {
      return this.$_.get(this.contact, 'uid', 'add-contact')
    },
    fullName() {
      return this.firstName && this.lastName ? `${this.firstName} ${this.lastName}`.trim() : ''
    }
  },
  created() {
    this.populateForm(this.contact)
    this.alertScreenReader(`${this.contact ? 'Edit' : 'Add'} department contact form is ready`)
  },
  methods: {
    onSave() {
      this.alertScreenReader('Saving')
      this.updateContact({
        'canReceiveCommunications': this.canReceiveCommunications,
        'canViewReports': this.permissions === 'reports_only',
        'canViewResponseRates': this.permissions === 'response_rates',
        'csid': this.csid,
        'email': this.email,
        'firstName': this.firstName,
        'lastName': this.lastName,
        'uid': this.uid,
        'userId': this.userId
      }).then(this.afterSave)
    },
    onSelectSearchResult(user) {
      this.populateForm(user)
    },
    populateForm(contact) {
      if (contact) {
        this.csid = contact.csid
        this.email = contact.email
        this.firstName = contact.firstName
        this.lastName = contact.lastName
        this.uid = contact.uid
        this.userId = contact.userId
        if (contact.canReceiveCommunications !== undefined) {
          this.canReceiveCommunications = contact.canReceiveCommunications
        }
        if (contact.canViewReports) {
          this.permissions = contact.canViewResponseRates ? 'response_rates' : 'reports_only'
        }
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
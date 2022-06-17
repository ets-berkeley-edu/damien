<template>
  <v-form
    v-model="valid"
    class="pa-3"
    lazy-validation
  >
    <div v-if="!contact">
      <h3 class="form-title my-2">
        Add Contact
      </h3>
      <PersonLookup
        class="mt-1 mb-4"
        :exclude-uids="$_.map(contacts, 'uid')"
        :on-select-result="onSelectSearchResult"
      />
    </div>
    <div v-if="uid">
      <label :for="`input-email-${contactId}`" class="form-label">
        Email Address
      </label>
      <v-text-field
        :id="`input-email-${contactId}`"
        v-model="email"
        class="mt-1"
        color="tertiary"
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
        color="tertiary"
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
          color="tertiary"
          label="No access to Blue"
        ></v-radio>
        <v-radio
          :id="`radio-reports-only-${contactId}`"
          value="reports_only"
          class="mb-1"
          color="tertiary"
          label="View reports"
        ></v-radio>
        <v-radio
          :id="`radio-response-rates-${contactId}`"
          value="response_rates"
          class="mb-1"
          color="tertiary"
          label="View reports and response rates"
        ></v-radio>
      </v-radio-group>
      <legend :for="`select-deptForms-${contactId}`" class="form-label">
        Department Forms
      </legend>
      <div :id="`deptForms-${contactId}`">
        <VueSelect
          :id="`select-deptForms-${contactId}`"
          v-model="contactDepartmentForms"
          class="vue-select-override mt-2 mb-4"
          :class="$vuetify.theme.dark ? 'dark' : 'light'"
          :clearable="false"
          :disabled="disableControls"
          label="name"
          multiple
          :options="availableDepartmentForms"
          @option:selected="afterSelectDepartmentForm"
        >
          <template #search="{attributes, events}">
            <input
              :id="`input-deptForms-${contactId}`"
              class="vs__search"
              v-bind="attributes"
              v-on="events"
            />
          </template>
          <template #selected-option-container="{option}">
            <v-chip
              :id="`selected-deptForm-${option.id}-${contactId}`"
              class="px-4 my-1"
              :class="{'disabled': !disableControls}"
              close
              :close-label="`Remove ${option.name} from ${fullName}'s department forms`"
              :disabled="disableControls"
              :ripple="false"
              @click:close="remove(option)"
            >
              {{ option.name }}
            </v-chip>
          </template>
        </VueSelect>
      </div>
    </div>
    <v-btn
      :id="`save-dept-contact-${contactId}-btn`"
      class="text-capitalize mr-2"
      color="secondary"
      :disabled="disableControls || !valid || !uid"
      elevation="2"
      @click.prevent="onSave"
      @keypress.enter.prevent.prevent="onSave"
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
      @click.prevent="onCancel"
      @keypress.enter.prevent.prevent="onCancel"
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
    contactDepartmentForms: undefined,
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
    availableDepartmentForms() {
      return this.$_.differenceBy(this.allDepartmentForms, this.contactDepartmentForms, item => item.name)
    },
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
    afterSelectDepartmentForm(departmentForms) {
      const selected = this.$_.last(departmentForms)
      this.alertScreenReader(`Added ${selected.name}.`)
      this.$putFocusNextTick(`input-deptForms-${this.contactId}`)
    },
    onSave() {
      this.alertScreenReader('Saving')
      this.updateContact({
        'canReceiveCommunications': this.canReceiveCommunications,
        'canViewReports': this.permissions === 'reports_only',
        'canViewResponseRates': this.permissions === 'response_rates',
        'csid': this.csid,
        'departmentForms': this.contactDepartmentForms,
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
        this.contactDepartmentForms = this.$_.cloneDeep(this.$_.sortBy(contact.departmentForms, 'name'))
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
        this.$putFocusNextTick(`input-email-${this.contactId}`)
      } else {
        this.$putFocusNextTick('input-person-lookup-autocomplete')
      }
    },
    remove(departmentForm) {
      const formName = departmentForm.name
      const indexOf = this.$_.findIndex(this.contactDepartmentForms, {'name': formName})
      this.contactDepartmentForms.splice(indexOf, 1)
      this.alertScreenReader(`Removed ${formName} from ${this.fullName} department forms.`)
      this.$putFocusNextTick(`input-deptForms-${this.contactId}`)
    }
  }
}
</script>

<style>
.form-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

}
</style>

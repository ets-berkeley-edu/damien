<template>
  <v-expansion-panel
    :id="`department-contact-${index}`"
    class="text-condensed my-1"
    :class="{'theme--light v-sheet--outlined': isEditing && !this.$vuetify.theme.dark, 'theme--dark v-sheet--outlined': isEditing && this.$vuetify.theme.dark}"
  >
    <v-expansion-panel-header class="py-1 mb-1 rounded-b-0 height-unset">
      <strong :id="`dept-contact-${contact.id}-name`">{{ fullName }}</strong>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <div v-if="!isEditing">
        <div :id="`dept-contact-${contact.id}-email`">{{ contact.email }}</div>
        <div :id="`dept-contact-${contact.id}-notifications`" class="font-italic">
          <v-icon
            class="pb-1"
            :class="contact.canReceiveCommunications ? 'success--text' : 'muted--text'"
            small
          >
            {{ contact.canReceiveCommunications ? 'mdi-check-circle' : 'mdi-minus-circle' }}
          </v-icon>
          {{ `${contact.canReceiveCommunications ? 'Does' : 'Does not'} receive notifications` }}
        </div>
        <div :id="`dept-contact-${contact.id}-permissions`" class="font-italic">
          <v-icon
            class="pb-1"
            :class="contact.canViewReports ? 'success--text' : 'muted--text'"
            small
          >
            {{ contact.canViewReports ? 'mdi-check-circle' : 'mdi-minus-circle' }}
          </v-icon>
          <span v-if="!contact.canViewReports">Does not have access to Blue</span>
          <span v-if="contact.canViewReports">
            {{ `Can view reports ${contact.canViewResponseRates ? 'and response rates ' : ''}in Blue` }}
          </span>
        </div>
        <div :id="`dept-contact-${contact.id}-deptForms`">
          <v-chip
            v-for="(form, formIndex) in contact.departmentForms"
            :id="`dept-contact-${contact.id}-form-${formIndex}`"
            :key="form.id"
            class="px-4 mr-1 mb-1"
            disabled
            :ripple="false"
          >
            {{ form.name }}
          </v-chip>
        </div>
        <v-toolbar
          v-if="$currentUser.isAdmin"
          :id="`dept-contact-${contact.id}-actions`"
          flat
          height="unset"
          tag="div"
        >
          <v-btn
            :id="`edit-dept-contact-${contact.id}-btn`"
            class="text-capitalize pa-0"
            color="tertiary"
            :disabled="disableControls"
            height="unset"
            min-width="unset"
            text
            @click="() => isEditing = true"
          >
            Edit
          </v-btn>
          <v-divider
            class="separator mx-2"
            role="presentation"
            vertical
          ></v-divider>
          <v-btn
            :id="`delete-dept-contact-${contact.id}-btn`"
            class="text-capitalize pa-0"
            color="tertiary"
            :disabled="disableControls"
            height="unset"
            min-width="unset"
            text
            @click="() => isConfirming = true"
          >
            Delete
          </v-btn>
          <ConfirmDialog
            :model="isConfirming"
            :cancel-action="() => isConfirming = false"
            :perform-action="onDelete"
            :text="`Are you sure you want to remove ${fullName}?`"
            :title="'Delete contact?'"
          />
        </v-toolbar>
      </div>
      <EditDepartmentContact
        v-if="isEditing"
        :id="`edit-department-contact-${contact.id}`"
        :after-save="afterSave"
        :contact="contact"
        :on-cancel="onCancelEdit"
      />
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'

export default {
  name: 'DepartmentContact',
  components: {ConfirmDialog, EditDepartmentContact},
  mixins: [Context, DepartmentEditSession],
  props: {
    contact: {
      required: true,
      type: Object
    },
    index: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    isConfirming: false,
    isEditing: false
  }),
  computed: {
    fullName() {
      return `${this.contact.firstName} ${this.contact.lastName}`
    }
  },
  methods: {
    afterSave() {
      this.isEditing = false
      this.alertScreenReader(`Updated contact ${this.fullName}.`)
      this.$putFocusNextTick(`edit-dept-contact-${this.contact.id}-btn`)
    },
    onCancelEdit() {
      this.isEditing = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick(`edit-dept-contact-${this.contact.id}-btn`)
    },
    onDelete() {
      const nameOfDeleted = this.fullName
      this.deleteContact(this.contact.userId).then(() => {
        this.isConfirming = false
        this.alertScreenReader(`Deleted contact ${nameOfDeleted}.`)
        this.$putFocusNextTick('add-dept-contact-btn')
      })
    }
  }
}
</script>

<style scoped>
.v-expansion-panel::before {
   box-shadow: none !important;
}
</style>

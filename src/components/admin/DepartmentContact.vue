<template>
  <v-card
    :id="`department-contact-${index}`"
    class="my-1 pa-2"
    :flat="!isEditing"
    :outlined="isEditing"
  >
    <div v-if="!isEditing" class="text-condensed">
      <strong>{{ contact.firstName }} {{ contact.lastName }}</strong>
      <div>{{ contact.email }}</div>
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
          :class="contact.canViewResponseRates ? 'success--text' : 'muted--text'"
          small
        >
          {{ contact.canViewResponseRates ? 'mdi-check-circle' : 'mdi-minus-circle' }}
        </v-icon>
        {{ `${contact.canViewResponseRates ? 'Can' : 'Cannot'} view response rates` }}
      </div>
      <v-toolbar
        :id="`dept-contact-${contact.id}-actions`"
        flat
        height="unset"
        tag="div"
      >
        <v-btn
          :id="`edit-dept-contact-${contact.id}-btn`"
          class="text-capitalize pa-0"
          color="secondary"
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
          color="secondary"
          :disabled="disableControls"
          height="unset"
          min-width="unset"
          text
          @click="onDelete"
        >
          Delete
        </v-btn>
      </v-toolbar>
    </div>
    <EditDepartmentContact
      v-if="isEditing"
      :id="`edit-department-contact-${contact.id}`"
      :after-save="afterSave"
      :contact="contact"
      :on-cancel="onCancelEdit"
    />
  </v-card>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'

export default {
  name: 'DepartmentContact',
  components: {EditDepartmentContact},
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
    isEditing: false
  }),
  methods: {
    afterSave() {
      this.isEditing = false
      this.alertScreenReader(`Updated department contact ${this.contact.firstName} ${this.contact.lastName}.`)
      this.$putFocusNextTick(`edit-dept-contact-${this.contact.id}-btn`)
    },
    onCancelEdit() {
      this.isEditing = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick(`edit-dept-contact-${this.contact.id}-btn`)
    },
    onDelete() {
      console.log('TODO: delete contact')
    }
  }
}
</script>
<template>
  <v-card class="my-1 pa-2" outlined>
    <div class="pa-3">
      <h3>Send Notification</h3>
      <div v-if="recipients">
        <div class="mt-2 mb-1">Message will be sent to:</div>
        <v-chip
          v-for="(recipient, index) in recipients"
          :key="index"
          class="my-1"
          close
          :disabled="isSending"
          @click:close="removeRecipient(recipient, index)"
        >
          {{ recipientLabel(recipient) }}
        </v-chip>
      </div>
    </div>
    <v-form class="pa-3">
      <label for="input-notification-subject" class="form-label">
        Subject
      </label>
      <v-text-field
        id="input-notification-subject"
        v-model="subject"
        class="my-1"
        color="secondary"
        dense
        :disabled="isSending"
        hide-details="auto"
        outlined
      ></v-text-field>
      <label for="input-notification-message" class="form-label">
        Message
      </label>
      <v-textarea
        id="input-notification-message"
        v-model="message"
        auto-grow
        class="mt-1"
        color="secondary"
        :disabled="isSending"
        flat
        hide-details="auto"
        outlined
      ></v-textarea>
      <div class="pt-3">
        <v-btn
          id="send-notification-btn"
          class="text-capitalize mr-2"
          color="secondary"
          :disabled="disabled"
          elevation="2"
          @click="sendNotification"
        >
          Send
        </v-btn>
        <v-btn
          id="cancel-send-notification-btn"
          class="text-capitalize ml-1"
          color="secondary"
          :disabled="isSending"
          elevation="2"
          outlined
          text
          @click="onCancel"
        >
          Cancel
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script>
import {notifyContacts} from '@/api/departments'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'NotificationForm',
  mixins: [Context, DepartmentEditSession],
  props: {
    afterSend: {
      required: true,
      type: Function
    },
    onCancel: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    message: undefined,
    isSending: false,
    recipients: [],
    subject: undefined
  }),
  computed: {
    disabled() {
      return this.isSending || !this.$_.trim(this.subject) || !this.$_.trim(this.message) || !this.$_.size(this.recipients)
    }
  },
  created() {
    this.recipients = this.$_.clone(this.contacts)
    this.alertScreenReader('Send notification form is ready.')
    this.$putFocusNextTick('input-notification-subject')
  },
  methods: {
    recipientLabel(recipient) {
      return `${recipient.firstName} ${recipient.lastName} (${recipient.email})`
    },
    removeRecipient(recipient, index) {
      const label = this.recipientLabel(recipient)
      this.recipients.splice(index, 1)
      this.alertScreenReader(`Removed ${label} from list of recipients.`)
    },
    sendNotification() {
      this.alertScreenReader('Sending')
      this.isSending = true
      notifyContacts(this.message, this.recipients, this.subject).then(() => {
        this.afterSend()
      })
    }
  }
}
</script>

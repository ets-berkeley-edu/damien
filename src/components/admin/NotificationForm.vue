<template>
  <v-card class="my-1 pa-2" outlined>
    <div class="pa-3">
      <h3>Send Notification</h3>
      <div v-if="selectedRecipients">
        <div class="mt-2 mb-1">Message will be sent to:</div>
        <v-expansion-panels
          class="recipients-container"
          hover
          multiple
          tile
        >
          <v-expansion-panel
            v-for="(department, deptIndex) in selectedRecipients"
            :key="deptIndex"
          >
            <v-expansion-panel-header class="pa-2 dept-expand">
              <h4 :id="`dept-head-${deptIndex}`">{{ department.deptName }}</h4>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-chip
                v-for="(recipient, index) in department.recipients"
                :key="index"
                class="recipient my-1 py-1"
                :ripple="false"
              >
                {{ recipientLabel(recipient) }}
                <v-btn
                  :aria-label="`Remove ${recipientLabel(recipient)} from recipients`"
                  :disabled="isSending"
                  icon
                  small
                  @click.stop="removeRecipient(department, recipient, index)"
                >
                  <v-icon>mdi-close-circle</v-icon>
                </v-btn>
              </v-chip>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
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
        color="tertiary"
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
        color="tertiary"
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
          color="tertiary"
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

export default {
  name: 'NotificationForm',
  mixins: [Context],
  props: {
    afterSend: {
      required: true,
      type: Function
    },
    onCancel: {
      required: true,
      type: Function
    },
    recipients: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    message: undefined,
    isSending: false,
    selectedRecipients: [],
    subject: undefined
  }),
  computed: {
    disabled() {
      return this.isSending || !this.$_.trim(this.subject) || !this.$_.trim(this.message) || !this.$_.size(this.selectedRecipients)
    }
  },
  created() {
    this.selectedRecipients = this.$_.cloneDeep(this.recipients)
    this.alertScreenReader('Send notification form is ready.')
    this.$putFocusNextTick('input-notification-subject')
  },
  methods: {
    recipientLabel(recipient) {
      return `${recipient.firstName} ${recipient.lastName} (${recipient.email})`
    },
    removeRecipient(department, recipient, index) {
      const label = this.recipientLabel(recipient)
      const indexOfDepartment = this.$_.indexOf(this.selectedRecipients, department)
      if (this.$_.size(department.recipients) === 1) {
        this.selectedRecipients.splice(indexOfDepartment, 1)
      } else {
        this.selectedRecipients[indexOfDepartment].recipients.splice(index, 1)
      }
      this.alertScreenReader(`Removed ${label} from list of recipients.`)
      return false
    },
    sendNotification() {
      this.alertScreenReader('Sending')
      this.isSending = true
      notifyContacts(this.message, this.selectedRecipients, this.subject).then(() => {
        this.afterSend()
      })
    }
  }
}
</script>

<style scoped>
.dept-expand {
  min-height: unset !important;
}
.recipient {
  height: fit-content;
  white-space: break-spaces;
}
.recipients-container {
  max-height: 300px;
  overflow-y: auto;
}
</style>

<template>
  <v-card class="my-1 pa-2" outlined>
    <div v-if="isSending">
      <v-progress-circular
        class="spinner"
        :indeterminate="true"
        rotate="5"
        size="64"
        width="4"
        color="secondary"
      ></v-progress-circular>
    </div>
    <v-card-title class="pa-3" :class="isSending ? 'muted--text' : ''">
      <h3
        id="send-notification-section-header"
        tabindex="-1"
      >
        Send Notification
      </h3>
    </v-card-title>
    <v-card-subtitle v-if="selectedRecipients" class="pr-0">
      <div class="mt-2 mb-1">Message will be sent to:</div>
      <v-expansion-panels
        class="recipients-container"
        :disabled="isSending"
        hover
        multiple
        tile
      >
        <v-expansion-panel
          v-for="(department, deptIndex) in selectedRecipients"
          :key="deptIndex"
        >
          <v-expansion-panel-header class="pa-2 height-unset">
            <h4 :id="`dept-head-${deptIndex}`">{{ department.deptName }}</h4>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-chip
              v-for="(recipient, index) in department.recipients"
              :key="index"
              class="recipient my-1 mr-1 py-1"
              :ripple="false"
            >
              {{ recipientLabel(recipient) }}
              <v-btn
                :aria-label="`Remove ${recipientLabel(recipient)} from recipients`"
                :disabled="isSending"
                icon
                small
                @click.stop="removeRecipient(department, recipient, index)"
                @keypress.enter.prevent.stop="removeRecipient(department, recipient, index)"
              >
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </v-chip>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-subtitle>
    <v-divider />
    <v-card-text class="notification-container py-0">
      <v-form
        class="pa-3"
        :class="isSending ? 'muted--text' : ''"
        :disabled="isSending"
      >
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
          @keydown.esc="onCancel"
        />
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
      </v-form>
    </v-card-text>
    <v-card-actions>
      <div class="pt-3">
        <v-btn
          id="send-notification-btn"
          class="text-capitalize mr-2"
          color="secondary"
          :disabled="disabled"
          elevation="2"
          @click="sendNotification"
          @keypress.enter.prevent="sendNotification"
        >
          Send
        </v-btn>
        <v-btn
          id="cancel-send-notification-btn"
          class="text-capitalize ml-1"
          :disabled="isSending"
          elevation="2"
          outlined
          text
          @click="onCancel"
          @keypress.enter.prevent="onCancel"
        >
          Cancel
        </v-btn>
      </div>
    </v-card-actions>
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
    this.$putFocusNextTick('send-notification-section-header')
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
      this.isSending = true
      this.alertScreenReader('Sending')
      notifyContacts(this.message, this.selectedRecipients, this.subject).then(response => {
        if (response) {
          this.afterSend()
        } else {
          this.isSending = false
          this.reportError('Notification failed. Nothing sent.')
        }
      })
    }
  }
}
</script>

<style scoped>
.notification-container {
  min-height: 260px;
}
.recipient {
  height: fit-content;
  white-space: break-spaces;
}
.recipients-container {
  max-height: 180px;
  overflow-y: auto;
}
.spinner {
  bottom: 0;
  height: 2em;
  left: 0;
  margin: auto;
  overflow: visible;
  position: absolute;
  right: 0;
  top: 0;
  width: 2em;
  z-index: 999;
}
</style>

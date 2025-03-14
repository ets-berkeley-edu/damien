<template>
  <v-card
    class="mb-0 modal-content"
    flat
    :min-width="minWidth"
  >
    <v-card-title class="px-4" :class="{'text-muted': isSending}">
      <h3 id="send-notification-header">
        Send Notification
      </h3>
    </v-card-title>
    <v-card-subtitle v-if="selectedRecipients" class="px-4">
      <h4 id="notification-recipients-header" class="font-size-16 mb-2">Message will be sent to:</h4>
      <v-expansion-panels
        id="notification-recipients-container"
        aria-describedby="notification-recipients-header"
        class="recipients-container border-sm"
        hover
        multiple
        tabindex="-1"
        tile
      >
        <v-expansion-panel
          v-for="(department, deptIndex) in selectedRecipients"
          :key="deptIndex"
        >
          <v-expansion-panel-title :id="`notification-recipients-dept-${department.deptId}`" class="border-sm">
            <h5 :id="`dept-head-${deptIndex}`" class="font-size-14">
              {{ department.deptName }} <span class="sr-only">recipients</span>
            </h5>
          </v-expansion-panel-title>
          <v-expansion-panel-text :aria-describedby="`notification-recipients-dept-${department.deptId}`">
            <div v-for="(recipient, index) in department.recipients" :key="index" class="d-flex flex-wrap pt-1">
              <div
                :id="`notification-recipient-${department.deptId}-${recipient.uid}`"
                class="align-center bg-green-accent-1 border-sm d-flex mb-1 pill-height px-2 py-1 rounded-xl"
              >
                <div class="px-2 recipient">
                  {{ recipientLabel(recipient) }}
                </div>
                <v-btn
                  v-if="department.recipients.length > 1"
                  :id="`notification-recipient-remove-${department.deptId}-${recipient.uid}-btn`"
                  :aria-label="`Remove ${recipientLabel(recipient)} from recipients`"
                  color="green-accent-1"
                  density="compact"
                  :disabled="isSending"
                  :icon="mdiCloseCircle"
                  variant="flat"
                  @click.stop="() => removeRecipient(department, recipient, index)"
                />
              </div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-subtitle>
    <v-card-text class="notification-container px-4 py-0">
      <v-form
        class="py-4"
        :class="isSending ? 'text-muted' : ''"
        :disabled="isSending"
      >
        <label for="input-notification-subject" class="form-label">
          Subject
        </label>
        <v-text-field
          id="input-notification-subject"
          v-model="subject"
          class="bg-surface my-1"
          color="primary"
          density="compact"
          :disabled="isSending"
          hide-details="auto"
          variant="outlined"
          @keydown.esc="onCancel"
        />
        <div class="mt-2">
          <label for="input-notification-message" class="form-label">
            Message
          </label>
          <v-textarea
            id="input-notification-message"
            v-model="message"
            auto-grow
            class="bg-surface mt-1"
            color="primary"
            :disabled="isSending"
            hide-details="auto"
            variant="outlined"
          />
        </div>
      </v-form>
    </v-card-text>
    <v-card-actions class="modal-footer px-4">
      <div class="text-right w-100">
        <ProgressButton
          id="send-notification-btn"
          :action="sendNotification"
          class="mr-2"
          :disabled="disabled"
          :in-progress="isSending"
          text="Send"
        />
        <v-btn
          id="cancel-send-notification-btn"
          :disabled="isSending"
          text="Cancel"
          variant="outlined"
          @click="onCancel"
        />
      </div>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {cloneDeep, indexOf, size, trim} from 'lodash'
import {computed, onMounted, ref} from 'vue'
import {mdiCloseCircle} from '@mdi/js'
import {notifyContacts} from '@/api/departments'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  afterSend: {
    required: true,
    type: Function
  },
  minWidth: {
    default: undefined,
    required: false,
    type: [String, Number]
  },
  onCancel: {
    required: true,
    type: Function
  },
  recipients: {
    required: true,
    type: Array
  }
})

const contextStore = useContextStore()

const message = ref(undefined)
const isSending = ref(false)
const selectedRecipients = ref([])
const subject = ref(undefined)

const disabled = computed(() => {
  return isSending.value || !trim(subject.value) || !trim(message.value) || !size(selectedRecipients.value)
})

onMounted(() => {
  selectedRecipients.value = cloneDeep(props.recipients)
  putFocusNextTick('notification-recipients-container')
})

const recipientLabel = recipient => `${recipient.firstName} ${recipient.lastName} (${recipient.email})`

const removeRecipient = (department, recipient, index) => {
  const label = recipientLabel(recipient)
  const indexOfDepartment = indexOf(selectedRecipients.value, department)
  if (size(department.recipients) === 1) {
    selectedRecipients.value.splice(indexOfDepartment, 1)
  } else {
    selectedRecipients.value[indexOfDepartment].recipients.splice(index, 1)
  }
  alertScreenReader(`Removed ${label} from recipients.`)
  return false
}

const sendNotification = () => {
  isSending.value = true
  alertScreenReader('Sending')
  notifyContacts(message.value, selectedRecipients.value, subject.value).then(response => {
    if (response) {
      props.afterSend()
    } else {
      isSending.value = false
      contextStore.snackbarReportError('Notification failed. Nothing sent.')
    }
  })
}
</script>

<style scoped>
.notification-container {
  min-height: 290px;
}
.pill-height {
  min-height: 40px;
}
.recipient {
  white-space: break-spaces;
}
.recipients-container {
  max-height: 180px;
  overflow-y: auto;
}
</style>

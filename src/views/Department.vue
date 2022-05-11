<template>
  <div>
    <div v-if="$_.get(department, 'deptName')" class="d-flex align-center justify-space-between flex-wrap">
      <h1 id="page-title" class="d-flex align-baseline flex-wrap mr-5">
        {{ department.deptName }}&MediumSpace;
        <span v-if="department.catalogListings">
          ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})&MediumSpace;
        </span>
        <span v-if="selectedTerm"> - {{ $_.get(selectedTerm, 'name') }}</span>
      </h1>
      <div class="d-flex align-baseline">
        <div v-if="$currentUser.isAdmin" class="d-flex align-baseline mr-3">
          <label
            id="select-term-label"
            for="select-term"
            class="align-self-baseline text-nowrap pr-3"
          >
            Term:
          </label>
          <select
            id="select-term"
            v-model="selectedTermId"
            class="native-select-override select-term my-2 px-3"
            :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
            :disabled="disableControls || loading"
            @change="onChangeTerm"
          >
            <option
              v-for="term in availableTerms"
              :id="`term-option-${term.id}`"
              :key="term.id"
              :value="term.id"
            >
              {{ term.name }}
            </option>
          </select>
        </div>
        <div v-if="!loading && false === $_.get(department, 'evaluationTerm.isLocked')">
          <span class="sr-only">Unlocked</span>
          <v-icon>
            mdi-lock-open-variant-outline
          </v-icon>
        </div>
        <div v-if="!loading && true === $_.get(department, 'evaluationTerm.isLocked')">
          <span class="sr-only">Locked</span>
          <v-icon>
            mdi-lock
          </v-icon>
        </div>
      </div>
    </div>
    <v-container v-if="!loading" class="mx-0 px-0 pb-6" fluid>
      <v-row justify="start">
        <v-col cols="12" md="5">
          <h2 class="pb-1 px-2">Department Contacts</h2>
          <v-btn
            v-if="$currentUser.isAdmin && !isCreatingNotification"
            id="open-notification-form-btn"
            class="ma-2 secondary text-capitalize"
            :disabled="disableControls || $_.isEmpty(contacts)"
            @click="() => isCreatingNotification = true"
          >
            Send notification
          </v-btn>
          <NotificationForm
            v-if="$currentUser.isAdmin && isCreatingNotification"
            :after-send="afterSendNotification"
            :on-cancel="cancelSendNotification"
            :recipients="[notificationRecipients]"
          />
          <v-btn
            class="float-right text-capitalize mt-2 mr-4"
            color="primary--text"
            text
            @click="() => contactsPanel = []"
            @keypress.enter.prevent="() => contactsPanel = []"
          >
            Collapse All
            <v-icon class="flip-horizontally ml-1">mdi-collapse-all-outline</v-icon>
          </v-btn>
          <v-expansion-panels
            v-model="contactsPanel"
            flat
            focusable
            hover
            multiple
          >
            <DepartmentContact
              v-for="(contact, index) in contacts"
              :key="contact.id"
              :contact="contact"
              :index="index"
            />
          </v-expansion-panels>
          <v-btn
            v-if="$currentUser.isAdmin && !isAddingContact"
            id="add-dept-contact-btn"
            class="text-capitalize pl-2 my-1 mx-2"
            color="tertiary"
            text
            @click="() => isAddingContact = true"
            @keypress.enter.prevent="() => isAddingContact = true"
          >
            <v-icon>mdi-plus-thick</v-icon>
            Add Contact
          </v-btn>
          <EditDepartmentContact
            v-if="$currentUser.isAdmin && isAddingContact"
            :id="`add-department-contact`"
            :after-save="afterSaveContact"
            :on-cancel="onCancelAddContact"
          />
        </v-col>
        <v-col cols="12" md="7">
          <DepartmentNote v-if="$currentUser.isAdmin" />
        </v-col>
      </v-row>
    </v-container>
    <v-container v-if="!loading" class="mx-0 px-0 pb-6" fluid>
      <v-card outlined class="elevation-1">
        <EvaluationActions :after-apply="refresh" />
        <EvaluationTable />
      </v-card>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationActions from '@/components/evaluation/EvaluationActions'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import NotificationForm from '@/components/admin/NotificationForm'

export default {
  name: 'Department',
  components: {
    DepartmentContact,
    DepartmentNote,
    EditDepartmentContact,
    EvaluationActions,
    EvaluationTable,
    NotificationForm
  },
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    availableTerms: undefined,
    bulkUpdateOptions: {
      evalDatesEnabled: false,
      midtermFormEnabled: false,
      startDate: null,
    },
    contactsPanel: [],
    courseActions: [
      {'text': 'Mark for review', 'value': 'mark'},
      {'text': 'Mark as confirmed', 'value': 'confirm'},
      {'text': 'Unmark', 'value': 'unmark'},
      {'text': 'Duplicate', 'value': 'duplicate'},
      {'text': 'Ignore', 'value': 'ignore'}
    ],
    isAddingContact: false,
    isAddingSection: false,
    isCreatingNotification: false,
    selectedCourseAction: undefined,
    selectedTermId: undefined
  }),
  computed: {
    notificationRecipients() {
      return {
        'deptName': this.department.deptName,
        'deptId': this.department.id,
        'recipients': this.$_.filter(this.contacts, 'canReceiveCommunications')
      }
    }
  },
  created() {
    this.availableTerms = this.$config.availableTerms
    this.selectedTermId = this.$config.currentTermId
    this.$root.$on('update-evaluations-selected', this.updateSelectedEvaluationIds)
    this.refresh()
  },
  methods: {
    afterSaveContact() {
      this.isAddingContact = false
      this.alertScreenReader('Contact saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    afterSendNotification() {
      this.isCreatingNotification = false
      this.snackbarOpen('Notification sent.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    cancelAddSection() {
      this.isAddingSection = false
      this.alertScreenReader('Section lookup canceled.')
      this.$putFocusNextTick('add-course-section-btn')
    },
    cancelSendNotification() {
      this.isCreatingNotification = false
      this.alertScreenReader('Notification canceled.')
    },
    onCancelAddContact() {
      this.isAddingContact = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    onChangeTerm(event) {
      const term = this.$_.find(this.availableTerms, ['id', event.target.value])
      this.alertScreenReader(`Loading ${this.$_.get(term, 'name', 'term')}`)
      this.refresh()
      this.$putFocusNextTick('select-term')
    },
    refresh(screenreaderAlert) {
      this.$loading()
      const departmentId = this.$_.get(this.$route, 'params.departmentId')
      const termId = this.selectedTermId
      this.init({departmentId, termId}).then(department => {
        this.$ready(`${department.deptName} ${this.$_.get(this.selectedTerm, 'name')}`, screenreaderAlert)
      })
    }
  }
}
</script>

<style scoped>
.select-term {
  max-width: 200px;
}
</style>
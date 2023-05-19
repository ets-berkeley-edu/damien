<template>
  <div class="pt-2">
    <div class="align-center d-flex flex-wrap justify-space-between">
      <div>
        <h1
          v-if="$_.get(department, 'deptName')"
          id="page-title"
          :style="{color: titleHexColor}"
          tabindex="-1"
        >
          <div class="d-flex flex-wrap">
            <div>
              <span>
                {{ department.deptName }}&MediumSpace;
                <span v-if="$_.size(getCatalogListings(department))">
                  ({{ getCatalogListings(department).join(', ') }})&MediumSpace;
                </span>
              </span>
              <span v-if="selectedTermName" class="mr-2">&mdash;&nbsp;</span>
            </div>
            <div v-if="selectedTermName">
              {{ selectedTermName }}
            </div>
          </div>
        </h1>
      </div>
      <div class="text-nowrap">
        <TermSelect :after-select="refresh" :term-ids="$_.get(department, 'enrolledTerms')" />
      </div>
    </div>
    <v-container v-if="!loading" class="mx-0 px-0 pb-2" fluid>
      <v-row justify="start">
        <v-col cols="12" md="5">
          <div class="contacts-container">
            <v-expansion-panels v-model="contactsPanel" disable-icon-rotate flat>
              <v-expansion-panel class="panel-override">
                <template #default>
                  <div class="align-center d-flex flex-wrap justify-space-between">
                    <h2 class="pb-1 px-2">Department Contacts</h2>
                    <div class="align-center d-flex height-unset justify-space-between">
                      <v-expansion-panel-header
                        class="w-fit-content ml-auto mr-3"
                        hide-actions
                        text
                        @click="collapseAllContacts"
                      >
                        <template #default="{open}">
                          <span v-if="!open">
                            Expand
                            <v-icon class="rotate-180 ml-1">mdi-plus-box-multiple-outline</v-icon>
                          </span>
                          <span v-if="open">
                            Collapse All
                            <v-icon class="rotate-180 ml-1">mdi-minus-box-multiple-outline</v-icon>
                          </span>
                        </template>
                      </v-expansion-panel-header>
                    </div>
                  </div>
                  <v-expansion-panel-content class="panel-content-override">
                    <v-expansion-panels
                      v-model="contactDetailsPanel"
                      flat
                      focusable
                      hover
                      multiple
                      tile
                    >
                      <DepartmentContact
                        v-for="(contact, index) in contacts"
                        :key="contact.id"
                        :contact="contact"
                        :index="index"
                        :is-expanded="$_.includes(contactDetailsPanel, index)"
                      />
                    </v-expansion-panels>
                  </v-expansion-panel-content>
                  <div v-if="$currentUser.isAdmin" class="pl-4">
                    <v-btn
                      v-if="!isCreatingNotification"
                      id="open-notification-form-btn"
                      class="ma-2 secondary text-capitalize"
                      :disabled="disableControls || $_.isEmpty(contacts)"
                      @click="() => isCreatingNotification = true"
                    >
                      Send notification
                    </v-btn>
                    <NotificationForm
                      v-if="isCreatingNotification"
                      :after-send="afterSendNotification"
                      :on-cancel="cancelSendNotification"
                      :recipients="[notificationRecipients]"
                    />
                  </div>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
            <div v-if="$currentUser.isAdmin" class="pl-4">
              <v-btn
                v-if="!isAddingContact"
                id="add-dept-contact-btn"
                class="text-capitalize pl-2 my-1 mx-2"
                color="tertiary"
                text
                @click="() => isAddingContact = true"
              >
                <v-icon>mdi-plus-thick</v-icon>
                Add Contact
              </v-btn>
              <EditDepartmentContact
                v-if="isAddingContact"
                :id="`add-department-contact`"
                :after-save="afterSaveContact"
                :on-cancel="onCancelAddContact"
              />
            </div>
          </div>
        </v-col>
        <v-col cols="12" md="7">
          <DepartmentNote />
        </v-col>
      </v-row>
    </v-container>
    <v-container v-if="!loading" class="mx-0 px-0 pb-6" fluid>
      <v-card outlined class="elevation-1">
        <EvaluationTable />
      </v-card>
    </v-container>
    <v-overlay :value="showTheOmenPoster" z-index="300">
      <v-card>
        <v-toolbar dark color="secondary" dense>
          <v-icon
            class="font-weight-bold pb-1 pl-0"
            @click="() => setShowTheOmenPoster(false)"
          >
            mdi-close
          </v-icon>
        </v-toolbar>
        <v-card-text class="text-center py-2">
          <img
            alt="Movie poster of The Omen"
            class="omen-poster-img"
            src="@/assets/omen_poster.png"
          />
        </v-card-text>
      </v-card>
    </v-overlay>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import NotificationForm from '@/components/admin/NotificationForm'
import TermSelect from '@/components/util/TermSelect'
import Util from '@/mixins/Util.vue'

export default {
  name: 'Department',
  components: {
    DepartmentContact,
    DepartmentNote,
    EditDepartmentContact,
    EvaluationTable,
    NotificationForm,
    TermSelect
  },
  mixins: [Context, DepartmentEditSession, Util],
  data: () => ({
    contactDetailsPanel: [],
    contactsPanel: undefined,
    isAddingContact: false,
    isCreatingNotification: false
  }),
  computed: {
    notificationRecipients() {
      return {
        deptName: this.department.deptName,
        deptId: this.department.id,
        recipients: this.$_.filter(this.contacts, 'canReceiveCommunications')
      }
    }
  },
  created() {
    this.setShowTheOmenPoster(this.$route.query.n === this.NUMBER_OF_THE_BEAST)
    this.$putFocusNextTick('page-title')
  },
  methods: {
    afterSaveContact() {
      this.isAddingContact = false
      this.contactsPanel = 0
      this.alertScreenReader('Contact saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    afterSendNotification() {
      this.isCreatingNotification = false
      this.snackbarOpen('Notification sent.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    cancelSendNotification() {
      this.isCreatingNotification = false
      this.alertScreenReader('Notification canceled.')
      this.scrollToTop(1000)
      this.$putFocusNextTick('open-notification-form-btn')
    },
    collapseAllContacts() {
      if (this.contactsPanel === 0) {
        this.contactDetailsPanel = []
      }
    },
    onCancelAddContact() {
      this.isAddingContact = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    refresh() {
      this.$loading()
      this.alertScreenReader(`Loading ${this.selectedTermName}`)
      const departmentId = this.$_.get(this.$route, 'params.departmentId')
      this.init(departmentId).then(department => {
        this.$ready(`${department.deptName} ${this.selectedTermName}`)
      })
    }
  }
}
</script>

<style scoped>
.contacts-container {
  max-width: 500px;
}
.omen-poster-img {
  height: 90vh;
}
.w-fit-content {
  width: fit-content;
}
</style>

<style>
.panel-content-override>.v-expansion-panel-content__wrap {
  padding: 0 !important;
}
.panel-override {
  background-color: unset !important;
}
</style>

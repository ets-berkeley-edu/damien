<template>
  <div class="pt-2">
    <div class="d-flex">
      <h1
        id="page-title"
        :style="{color: titleHexColor}"
        tabindex="-1"
      >
        List Management
      </h1>
      <v-spacer class="d-flex justify-center"></v-spacer>
      <v-banner
        v-if="$config.isVueAppDebugMode && $config.easterEggMonastery && $vuetify.theme.dark"
        shaped
        single-line
        class="pr-4 my-auto"
      >
        <a :href="$config.easterEggNannysRoom" target="_blank">The Nanny's Room</a>
      </v-banner>
    </div>
    <v-container class="px-0 mx-0" fluid>
      <v-row>
        <v-col cols="12" md="6" lg="3">
          <v-card
            class="mr-4"
            elevation="2"
            height="100%"
            min-width="fit-content"
          >
            <v-card-title
              id="department-forms-card-title"
              class="pb-0"
              tabindex="-1"
            >
              Department Forms
            </v-card-title>
            <v-btn
              v-if="!isAddingDepartmentForm"
              id="add-dept-form-btn"
              class="text-capitalize pl-3 mb-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddDepartmentForm"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new department form
            </v-btn>
            <v-form v-if="isAddingDepartmentForm" class="px-4 pb-4" @submit.prevent="onSubmitAddDepartmentForm">
              <label :for="'input-dept-form-name'" class="form-label">
                Form name
              </label>
              <v-text-field
                :id="'input-dept-form-name'"
                v-model="newItemName"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                required
                @keydown.esc="cancelAdd('add-dept-form-btn')"
              />
              <v-btn
                :id="'save-dept-form-btn'"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newItemName || isSaving"
                elevation="2"
                @click="onSubmitAddDepartmentForm"
              >
                Save
              </v-btn>
              <v-btn
                :id="'cancel-save-dept-form-btn'"
                class="text-capitalize ml-1"
                :disabled="isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-dept-form-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <div class="nannys-list overflow-y-auto">
              <v-data-table
                id="dept-forms-table"
                dense
                disable-pagination
                :headers="[{class: 'pl-3', text: 'Form Name', value: 'name'}]"
                hide-default-footer
                hide-default-header
                :items="departmentForms"
                item-key="name"
                :sort-by.sync="sortBy.departmentForms"
                :sort-desc.sync="sortDesc.departmentForms"
              >
                <template #header="{props: {headers}}">
                  <SortableTableHeader :id="'form-'" :headers="headers" :on-sort="sortDepartmentForms" />
                </template>
                <template #item.name="{item}">
                  <div class="d-flex justify-space-between">
                    <span>{{ item.name }}</span>
                    <v-btn
                      :id="`delete-dept-form-${item.id}-btn`"
                      class="text-capitalize px-2 py-0"
                      color="tertiary"
                      :disabled="disableControls"
                      height="unset"
                      min-width="unset"
                      text
                      @click.stop="() => confirmDeleteDepartmentForm(item)"
                    >
                      Delete
                    </v-btn>
                  </div>
                </template>
              </v-data-table>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" md="6" lg="3">
          <v-card
            class="mr-4"
            elevation="2"
            height="100%"
            min-width="fit-content"
          >
            <v-card-title
              id="evaluation-types-card-title"
              class="pb-0"
              tabindex="-1"
            >
              Evaluation Types
            </v-card-title>
            <v-btn
              v-if="!isAddingEvaluationType"
              id="add-eval-type-btn"
              class="text-capitalize pl-3 mb-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddEvaluationType"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new evaluation type
            </v-btn>
            <v-form v-if="isAddingEvaluationType" class="px-4 pb-4" @submit.prevent="onSubmitAddEvaluationType">
              <label :for="'input-eval-type-name'" class="form-label">
                Type name
              </label>
              <v-text-field
                :id="'input-eval-type-name'"
                v-model="newItemName"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                required
                @keydown.esc="cancelAdd('add-eval-type-btn')"
              />
              <v-btn
                :id="'save-eval-type-btn'"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newItemName || isSaving"
                elevation="2"
                @click="onSubmitAddEvaluationType"
              >
                Save
              </v-btn>
              <v-btn
                :id="'cancel-save-eval-type-btn'"
                class="text-capitalize ml-1"
                :disabled="isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-eval-type-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <div class="nannys-list overflow-y-auto">
              <v-data-table
                id="evaluation-types-table"
                dense
                disable-pagination
                :headers="[{class: 'pl-3', text: 'Type Name', value: 'name'}]"
                hide-default-footer
                hide-default-header
                :items="evaluationTypes"
                item-key="name"
                :sort-by.sync="sortBy.evaluationTypes"
                :sort-desc.sync="sortDesc.evaluationTypes"
              >
                <template #header="{props: {headers}}">
                  <SortableTableHeader :id="'eval-'" :headers="headers" :on-sort="sortEvaluationTypes" />
                </template>
                <template #item.name="{item}">
                  <div class="d-flex justify-space-between">
                    <span>{{ item.name }}</span>
                    <v-btn
                      :id="`delete-eval-type-${item.id}-btn`"
                      class="text-capitalize px-2 py-0"
                      color="tertiary"
                      :disabled="disableControls"
                      height="unset"
                      min-width="unset"
                      text
                      @click.stop="() => confirmDeleteEvaluationType(item)"
                    >
                      Delete
                    </v-btn>
                  </div>
                </template>
              </v-data-table>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" lg="6">
          <v-card
            class="mr-4"
            elevation="2"
            min-width="fit-content"
          >
            <v-card-title
              id="manually-added-instructors-title"
              class="pb-0"
              tabindex="-1"
            >
              Manually Added Instructors
            </v-card-title>
            <v-btn
              v-if="!isAddingInstructor"
              id="add-instructor-btn"
              class="text-capitalize pl-2 my-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddInstructor"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new instructor
            </v-btn>
            <v-form
              v-if="isAddingInstructor"
              class="px-4 pb-4"
              @submit.prevent="onSubmitAddInstructor"
            >
              <label for="input-instructor-uid" class="form-label">
                UID
              </label>
              <v-text-field
                id="input-instructor-uid"
                v-model="newInstructor.uid"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                required
                :rules="rules.numeric"
              />
              <label for="input-instructor-csid" class="form-label">
                CSID
              </label>
              <v-text-field
                id="input-instructor-csid"
                v-model="newInstructor.csid"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                :rules="rules.numeric"
              />
              <label for="input-instructor-first-name" class="form-label">
                First name
              </label>
              <v-text-field
                id="input-instructor-first-name"
                v-model="newInstructor.firstName"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
              />
              <label for="input-instructor-last-name" class="form-label">
                Last name
              </label>
              <v-text-field
                id="input-instructor-last-name"
                v-model="newInstructor.lastName"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                required
              />
              <label for="input-instructor-last-name" class="form-label">
                Email
              </label>
              <v-text-field
                id="input-instructor-email"
                v-model="newInstructor.emailAddress"
                class="mt-1"
                color="tertiary"
                dense
                :disabled="isSaving"
                outlined
                required
                :rules="rules.email"
              />
              <v-btn
                id="save-instructor-btn"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newInstructor.uid || !newInstructor.lastName || !newInstructor.emailAddress || isSaving"
                elevation="2"
                @click="onSubmitAddInstructor"
              >
                Save
              </v-btn>
              <v-btn
                id="cancel-save-instructor-btn"
                class="text-capitalize ml-1"
                :disabled="!instructorValid || isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-instructor-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <div class="nannys-list overflow-y-auto">
              <v-data-table
                id="instructors-table"
                dense
                disable-pagination
                :headers="instructorHeaders"
                hide-default-footer
                hide-default-header
                :items="instructors"
                :sort-by.sync="sortBy.instructors"
                :sort-desc.sync="sortDesc.instructors"
              >
                <template #header="{props: {headers}}">
                  <SortableTableHeader :id="'instructor-'" :headers="headers" :on-sort="sortInstructors" />
                </template>
                <template #item.delete="{ item }">
                  <v-btn
                    :id="`delete-instructor-${item.uid}-btn`"
                    class="text-capitalize px-2 py-0"
                    color="tertiary"
                    :disabled="disableControls"
                    height="unset"
                    min-width="unset"
                    text
                    @click.stop="() => confirmDeleteInstructor(item)"
                  >
                    Delete
                  </v-btn>
                </template>
                <template #no-data>
                  <div class="muted--text my-5">
                    No manually added instructors
                  </div>
                </template>
              </v-data-table>
            </div>
          </v-card>
          <v-card elevation="2" class="mr-4 mt-4">
            <v-card-title>Service Announcement</v-card-title>
            <EditServiceAnnouncement />
          </v-card>
          <v-card elevation="2" class="mr-4 mt-4">
            <v-card-title>Automatically Publish</v-card-title>
            <v-card-text>
              <span v-if="$config.scheduleLochRefresh">
                When enabled, publication will run daily at
                {{ `${String($config.scheduleLochRefresh.hour).padStart(2, '0')}:${String($config.scheduleLochRefresh.minute).padStart(2, '0')}` }}
                local time, immediately before loch refresh.
              </span>
              <span v-if="!$config.scheduleLochRefresh">
                Nightly loch refresh must be scheduled in app configs to enable auto-publish.
              </span>
              <v-switch
                id="auto-publish-enabled"
                v-model="autoPublishEnabled"
                :aria-label="`Auto-publish is ${autoPublishEnabled ? 'enabled' : 'disabled'}`"
                color="success"
                density="compact"
                :disabled="!$config.scheduleLochRefresh"
                hide-details
                :label="autoPublishEnabled ? 'Enabled' : 'Disabled'"
                @change="toggleAutoPublishEnabled(autoPublishEnabled)"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <ConfirmDialog
      v-if="isConfirming"
      :disabled="disableControls"
      :on-click-cancel="cancelDelete"
      :on-click-confirm="confirmDelete"
      :text="`Are you sure you want to delete ${$_.get(itemToDelete, 'name')}?`"
      :title="`Delete ${$_.get(itemToDelete, 'description')}?`"
    />
  </div>
</template>

<script>
import { getAutoPublishStatus, setAutoPublishStatus } from '@/api/config'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement'
import ListManagementSession from '@/mixins/ListManagementSession'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import Util from '@/mixins/Util'

export default {
  name: 'NannysRoom',
  components: {ConfirmDialog, EditServiceAnnouncement, SortableTableHeader},
  mixins: [Context, ListManagementSession, Util],
  data: () => ({
    autoPublishEnabled: undefined,
    instructorValid: true,
    rules: {
      email: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ],
      numeric: [v => !/[^\d]/.test(v) || 'Invalid number.']
    },
    instructorHeaders: [
      {class: 'pl-3', text: 'UID', value: 'uid'},
      {class: 'pl-3', text: 'SID', value: 'csid'},
      {class: 'pl-3', text: 'First Name', value: 'firstName'},
      {class: 'pl-3', text: 'Last Name', value: 'lastName'},
      {class: 'pl-3', text: 'Email', value: 'email'},
      {class: 'pl-3', text: '', value: 'delete', sortable: false}
    ],
    newInstructor: null,
    newItemName: null,
    sortBy: {
      departmentForms: null,
      evaluationTypes: null,
      instructors: null
    },
    sortDesc: {
      departmentForms: null,
      evaluationTypes: null,
      instructors: null
    }
  }),
  created() {
    this.resetNewInstructor()
    this.init().then(() => {
      this.$ready('List Management')
      this.$putFocusNextTick('page-title')
    })
    getAutoPublishStatus().then(data => {
      this.autoPublishEnabled = data.enabled
    })
  },
  methods: {
    afterDelete(deletedItem) {
      this.setDisableControls(false)
      this.alertScreenReader(`Deleted ${deletedItem.description} ${deletedItem.name}.`)
    },
    cancelAdd(elementId) {
      this.newItemName = ''
      this.resetNewInstructor()
      this.reset()
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick(elementId)
    },
    cancelDelete() {
      this.$putFocusNextTick(this.itemToDelete.elementId)
      this.reset()
      this.alertScreenReader('Canceled. Nothing deleted.')
    },
    confirmDelete() {
      this.setDisableControls(true)
      this.onDelete().then(this.afterDelete)
    },
    onClickAddDepartmentForm() {
      this.setAddingDepartmentForm().then(() => {
        this.newItemName = ''
        this.$putFocusNextTick('input-dept-form-name')
      })
    },
    onClickAddEvaluationType() {
      this.setAddingEvaluationType().then(() => {
        this.newItemName = ''
        this.$putFocusNextTick('input-eval-type-name')
      })
    },
    onClickAddInstructor() {
      this.setAddingInstructor().then(() => {
        this.resetNewInstructor()
        this.$putFocusNextTick('input-instructor-uid')
      })
    },
    onSubmitAddDepartmentForm() {
      if (this.newItemName) {
        this.addDepartmentForm(this.newItemName).then(() => {
          this.alertScreenReader(`Created department form ${this.newItemName}.`)
          this.newItemName = ''
          this.$putFocusNextTick('add-dept-form-btn')
        })
      }
    },
    onSubmitAddInstructor() {
      if (this.newInstructor) {
        this.addInstructor(this.newInstructor).then(() => {
          this.alertScreenReader(`Added instructor with UID ${this.newInstructor.uid}.`)
          this.resetNewInstructor()
          this.$putFocusNextTick('add-instructor-btn')
        })
      }
    },
    onSubmitAddEvaluationType() {
      if (this.newItemName) {
        this.addEvaluationType(this.newItemName).then(() => {
          this.alertScreenReader(`Created evaluation type ${this.newItemName}.`)
          this.newItemName = ''
          this.$putFocusNextTick('add-eval-type-btn')
        })
      }
    },
    resetNewInstructor() {
      this.newInstructor = {
        'csid': null,
        'emailAddress': null,
        'firstName': null,
        'lastName': null,
        'uid': null
      }
    },
    sortDepartmentForms(sortBy, sortDesc) {
      this.sortBy.departmentForms = sortBy
      this.sortDesc.departmentForms = sortDesc
    },
    sortEvaluationTypes(sortBy, sortDesc) {
      this.sortBy.evaluationTypes = sortBy
      this.sortDesc.evaluationTypes = sortDesc
    },
    sortInstructors(sortBy, sortDesc) {
      this.sortBy.instructors = sortBy
      this.sortDesc.instructors = sortDesc
    },
    toggleAutoPublishEnabled(enabled) {
      setAutoPublishStatus(enabled).then(data => {
        this.autoPublishEnabled = data.enabled
        this.alertScreenReader(`Auto-publish ${this.autoPublishEnabled ? 'enabled' : 'disabled'}`)
      })
    }
  }
}
</script>

<style scoped>
.nannys-list {
  max-height: 500px;
}
</style>

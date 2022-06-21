<template>
  <div class="pt-2">
    <div class="pb-2 d-flex">
      <h1 id="page-title">List Management</h1>
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
        <v-col cols="12" md="3">
          <v-card elevation="2" class="mr-4">
            <v-card-title>Department Forms</v-card-title>
            <v-btn
              v-if="!isAddingDepartmentForm"
              id="add-dept-form-btn"
              class="text-capitalize pl-2 mt-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddDepartmentForm"
              @keyup.enter="onClickAddDepartmentForm"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new department form
            </v-btn>
            <v-form v-if="isAddingDepartmentForm" class="px-4" @submit.prevent="onSubmitAddDepartmentForm">
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
              ></v-text-field>
              <v-btn
                :id="'save-dept-form-btn'"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newItemName || isSaving"
                elevation="2"
                @click="onSubmitAddDepartmentForm"
                @keyup.enter="onSubmitAddDepartmentForm"
              >
                Save
              </v-btn>
              <v-btn
                :id="'cancel-save-dept-form-btn'"
                class="text-capitalize ml-1"
                color="tertiary"
                :disabled="isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-dept-form-btn')"
                @keyup.enter="cancelAdd('add-dept-form-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <v-data-table
              id="dept-forms-table"
              dense
              disable-pagination
              :headers="[{text: 'Form Name', value: 'name'}]"
              hide-default-footer
              :items="departmentForms"
              item-key="name"
            >
              <template #item.name="{item}">
                <div class="d-flex justify-space-between">
                  <span>{{ item.name }}</span>
                  <v-btn
                    :id="`delete-dept-form-${item.id}-btn`"
                    class="text-capitalize pa-0"
                    color="tertiary"
                    :disabled="disableControls"
                    height="unset"
                    min-width="unset"
                    text
                    @click="() => confirmDeleteDepartmentForm(item)"
                    @keyup.enter="() => confirmDeleteDepartmentForm(item)"
                  >
                    Delete
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card elevation="2" class="mr-4">
            <v-card-title>Evaluation Types</v-card-title>
            <v-btn
              v-if="!isAddingEvaluationType"
              id="add-eval-type-btn"
              class="text-capitalize pl-2 mt-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddEvaluationType"
              @keyup.enter="onClickAddEvaluationType"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new evaluation type
            </v-btn>
            <v-form v-if="isAddingEvaluationType" class="px-4" @submit.prevent="onSubmitAddEvaluationType">
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
              ></v-text-field>
              <v-btn
                :id="'save-eval-type-btn'"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newItemName || isSaving"
                elevation="2"
                @click="onSubmitAddEvaluationType"
                @keyup.enter="onSubmitAddEvaluationType"
              >
                Save
              </v-btn>
              <v-btn
                :id="'cancel-save-eval-type-btn'"
                class="text-capitalize ml-1"
                color="tertiary"
                :disabled="isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-eval-type-btn')"
                @keyup.enter="cancelAdd('add-eval-type-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <v-data-table
              id="evaluation-types-table"
              dense
              disable-pagination
              :headers="[{text: 'Type Name', value: 'name'}]"
              hide-default-footer
              :items="evaluationTypes"
              item-key="name"
            >
              <template #item.name="{item}">
                <div class="d-flex justify-space-between">
                  <span>{{ item.name }}</span>
                  <v-btn
                    :id="`delete-eval-type-${item.id}-btn`"
                    class="text-capitalize pa-0"
                    color="tertiary"
                    :disabled="disableControls"
                    height="unset"
                    min-width="unset"
                    text
                    @click="() => confirmDeleteEvaluationType(item)"
                    @keyup.enter="() => confirmDeleteEvaluationType(item)"
                  >
                    Delete
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card elevation="2" class="mr-4">
            <v-card-title>Manually Added Instructors</v-card-title>
            <v-btn
              v-if="!isAddingInstructor"
              id="add-instructor-btn"
              class="text-capitalize pl-2 mt-1"
              color="tertiary"
              :disabled="disableControls"
              text
              @click="onClickAddInstructor"
              @keyup.enter="onClickAddInstructor"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new instructor
            </v-btn>
            <v-form
              v-if="isAddingInstructor"
              class="px-4"
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
              ></v-text-field>
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
              ></v-text-field>
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
              ></v-text-field>
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
              ></v-text-field>
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
              ></v-text-field>
              <v-btn
                id="save-instructor-btn"
                class="text-capitalize mr-2"
                color="secondary"
                :disabled="!newInstructor.uid || !newInstructor.lastName || !newInstructor.emailAddress || isSaving"
                elevation="2"
                @click="onSubmitAddInstructor"
                @keyup.enter="onSubmitAddInstructor"
              >
                Save
              </v-btn>
              <v-btn
                id="cancel-save-instructor-btn"
                class="text-capitalize ml-1"
                color="tertiary"
                :disabled="!instructorValid || isSaving"
                elevation="2"
                outlined
                text
                @click="cancelAdd('add-instructor-btn')"
                @keyup.enter="cancelAdd('add-instructor-btn')"
              >
                Cancel
              </v-btn>
            </v-form>
            <v-data-table
              id="instructors-table"
              dense
              disable-pagination
              :headers="instructorHeaders"
              hide-default-footer
              :items="instructors"
            >
              <template #item.delete="{ item }">
                <v-btn
                  :id="`delete-instructor-${item.uid}-btn`"
                  class="text-capitalize pa-0"
                  color="secondary"
                  :disabled="disableControls"
                  text
                  @click="() => confirmDeleteInstructor(item)"
                  @keyup.enter="() => confirmDeleteInstructor(item)"
                >
                  Delete
                </v-btn>
              </template>
            </v-data-table>
          </v-card>
          <v-card elevation="2" class="mr-4 mt-4">
            <v-card-title>Service Announcement</v-card-title>
            <EditServiceAnnouncement />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <ConfirmDialog
      :cancel-action="cancelDelete"
      :confirming="isConfirming"
      :perform-action="() => onDelete().then(afterDelete)"
      :text="`Are you sure you want to delete ${$_.get(itemToDelete, 'name')}?`"
      :title="`Delete ${$_.get(itemToDelete, 'description')}?`"
    />
  </div>
</template>

<script>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement'
import ListManagementSession from '@/mixins/ListManagementSession'

export default {
  name: 'NannysRoom',
  components: {ConfirmDialog, EditServiceAnnouncement},
  mixins: [Context, ListManagementSession],
  data: () => ({
    instructorValid: true,
    rules: {
      email: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ],
      numeric: [v => !/[^\d]/.test(v) || 'Invalid number.']
    },
    instructorHeaders: [
      {text: 'UID', value: 'uid'},
      {text: 'SID', value: 'csid'},
      {text: 'First Name', value: 'firstName'},
      {text: 'Last Name', value: 'lastName'},
      {text: 'Email', value: 'email'},
      {text: '', value: 'delete', sortable: false}
    ],
    newInstructor: null,
    newItemName: null
  }),
  created() {
    this.resetNewInstructor()
    this.init().then(() => {
      this.$ready('List Management')
    })
  },
  methods: {
    afterDelete(deletedItem) {
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
    }
  }
}
</script>
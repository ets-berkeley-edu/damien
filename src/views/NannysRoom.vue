<template>
  <div>
    <div class="pb-2 d-flex">
      <h1>List Management</h1>
      <v-spacer class="d-flex justify-center"></v-spacer>
      <v-banner
        v-if="$config.easterEggMonastery && $vuetify.theme.dark"
        shaped
        single-line
        class="pr-4 my-auto"
      >
        <a :href="$config.easterEggNannysRoom" target="_blank">The Nanny's Room</a>
      </v-banner>
    </div>
    <v-container class="px-0 mx-0">
      <v-row>
        <v-col>
          <v-card elevation="2" class="mr-4">
            <v-card-title>Department Forms</v-card-title>
            <v-btn
              v-if="!isAddingDepartmentForm"
              id="add-dept-form-btn"
              class="text-capitalize pl-2 mt-1"
              color="secondary"
              :disabled="disableControls"
              text
              @click="onClickAddDepartmentForm"
              @keyup.enter="onClickAddDepartmentForm"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new department form
            </v-btn>
            <v-form v-if="isAddingDepartmentForm" @submit.prevent="onSubmitAddDepartmentForm">
              <label :for="'input-dept-form-name'" class="form-label">
                Form name
              </label>
              <v-text-field
                :id="'input-dept-form-name'"
                v-model="newItemName"
                class="mt-1"
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
                color="secondary"
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
                    color="secondary"
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
        <v-col>
          <v-card elevation="2" class="mr-4">
            <v-card-title>Evaluation Types</v-card-title>
            <v-btn
              v-if="!isAddingEvaluationType"
              id="add-eval-type-btn"
              class="text-capitalize pl-2 mt-1"
              color="secondary"
              :disabled="disableControls"
              text
              @click="onClickAddEvaluationType"
              @keyup.enter="onClickAddDepartmentForm"
            >
              <v-icon>mdi-plus-thick</v-icon>
              Add new evaluation type
            </v-btn>
            <v-form v-if="isAddingEvaluationType" @submit.prevent="onSubmitAddEvaluationType">
              <label :for="'input-eval-type-name'" class="form-label">
                Type name
              </label>
              <v-text-field
                :id="'input-eval-type-name'"
                v-model="newItemName"
                class="mt-1"
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
                color="secondary"
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
                    color="secondary"
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
      </v-row>
    </v-container>
    <ConfirmDialog
      :model="isConfirming"
      :cancel-action="cancelDelete"
      :perform-action="() => onDelete().then(afterDelete)"
      :text="`Are you sure you want to delete ${$_.get(itemToDelete, 'name')}?`"
      :title="`Delete ${$_.get(itemToDelete, 'description')}?`"
    />
  </div>
</template>

<script>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import ListManagementSession from '@/mixins/ListManagementSession'

export default {
  name: 'NannysRoom',
  components: {ConfirmDialog},
  mixins: [Context, ListManagementSession],
  data: () => ({
    newItemName: ''
  }),
  created() {
    this.init().then(() => {
      this.$ready('List management')
    })
  },
  methods: {
    afterDelete(deletedItem) {
      this.alertScreenReader(`Deleted ${deletedItem.description} ${deletedItem.name}.`)
    },
    cancelAdd(elementId) {
      this.newItemName = ''
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
    onSubmitAddDepartmentForm() {
      if (this.newItemName) {
        this.addDepartmentForm(this.newItemName).then(() => {
          this.alertScreenReader(`Created department form ${this.newItemName}.`)
          this.newItemName = ''
          this.$putFocusNextTick('add-dept-form-btn')
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
    }
  }
}
</script>
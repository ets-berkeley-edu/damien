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
            <v-data-table
              id="department-forms-table"
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
                    height="unset"
                    min-width="unset"
                    text
                    @click="() => confirmDelete(item, 'department form', deleteDepartmentForm)"
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
                    height="unset"
                    min-width="unset"
                    text
                    @click="() => confirmDelete(item, 'evaluation type', deleteEvaluationType)"
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
      :perform-action="onDelete || $_.noop"
      :text="`Are you sure you want to delete ${$_.get(itemToDelete, 'name')}?`"
      :title="`Delete ${$_.get(itemToDelete, 'description')}?`"
    />
  </div>
</template>

<script>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import {deleteDepartmentForm, getDepartmentForms} from '@/api/departmentForms'
import {deleteEvaluationType, getEvaluationTypes} from '@/api/evaluationTypes'

export default {
  name: 'NannysRoom',
  components: {ConfirmDialog},
  mixins: [Context],
  data: () => ({
    departmentForms: [],
    evaluationTypes: [],
    isConfirming: false,
    itemToDelete: undefined,
    onDelete: undefined
  }),
  created() {
    Promise.all([getDepartmentForms(), getEvaluationTypes()]).then(data => {
      this.departmentForms = data[0]
      this.evaluationTypes = data[1]
      this.$ready('List management')
    })
  },
  methods: {
    cancelDelete() {
      this.alertScreenReader('Canceled. Nothing deleted.')
      this.reset()
    },
    confirmDelete(item, description, onDelete) {
      this.itemToDelete = {
        ...item,
        description: description
      }
      this.onDelete = onDelete
      this.isConfirming = true
    },
    deleteDepartmentForm() {
      deleteDepartmentForm(this.itemToDelete.name).then(() => {
        this.alertScreenReader(`Deleted department form ${this.itemToDelete.name}.`)
        this.reset()
        getDepartmentForms().then(data => {
          this.departmentForms = data
        })
      })
    },
    deleteEvaluationType() {
      deleteEvaluationType(this.itemToDelete.name).then(() => {
        this.alertScreenReader(`Deleted evaluation type ${this.itemToDelete.name}.`)
        this.reset()
        getEvaluationTypes().then(data => {
          this.evaluationTypes = data
        })
      })
    },
    reset() {
      this.onDelete = null
      this.isConfirming = false
      this.itemToDelete = null
    }
  }
}
</script>
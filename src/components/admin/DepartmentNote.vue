<template>
  <div>
    <h2
      id="notes-title"
      class="pb-1 px-2"
      tabindex="-1"
    >
      Notes
    </h2>
    <v-card
      class="my-1 pa-2"
      :flat="!isEditing"
      :outlined="isEditing"
    >
      <div
        v-if="item && !isEditing"
        id="dept-note"
        class="text-condensed pb-2 pl-4"
      >
        <pre class="body-2 text-condensed text-prewrap">{{ item }} </pre>
      </div>
      <v-form v-if="isEditing" class="pa-3">
        <v-textarea
          id="dept-note-textarea"
          v-model="item"
          auto-grow
          color="tertiary"
          :disabled="disableControls || !isEditable"
          flat
          hide-details="auto"
          outlined
          @keydown.esc="onCancelSave"
        />
      </v-form>
      <v-toolbar
        v-if="!isEditing"
        id="dept-note-actions"
        flat
        height="unset"
        tag="div"
      >
        <v-btn
          id="edit-dept-note-btn"
          class="text-capitalize pa-0"
          color="tertiary"
          :disabled="disableControls || !isEditable"
          dark
          height="unset"
          min-width="unset"
          text
          @click="onEdit"
        >
          {{ item ? 'Edit ' : 'Create ' }}<span class="sr-only">Note</span>
        </v-btn>
        <v-divider
          v-if="item"
          class="separator mx-2"
          role="presentation"
          vertical
        ></v-divider>
        <v-btn
          v-if="item"
          id="delete-dept-note-btn"
          class="text-capitalize pa-0"
          color="tertiary"
          :disabled="disableControls || !isEditable"
          height="unset"
          min-width="unset"
          text
          @click.stop="() => isConfirming = true"
        >
          Delete <span class="sr-only">Note</span>
        </v-btn>
        <ConfirmDialog
          v-if="isConfirming"
          :button-context="'Delete Note'"
          :disabled="disableControls"
          :on-click-cancel="onCancelDelete"
          :on-click-confirm="onDelete"
          :text="`Are you sure you want to delete the ${selectedTermName || ''} note?`"
          :title="'Delete note?'"
        />
      </v-toolbar>
      <div v-if="isEditing" class="pa-2">
        <v-btn
          id="save-dept-note-btn"
          class="text-capitalize mr-2"
          color="secondary"
          :disabled="disableControls || !isEditable"
          elevation="2"
          @click="onSave"
        >
          Save Note
        </v-btn>
        <v-btn
          id="cancel-dept-note-btn"
          class="text-capitalize ml-1"
          :disabled="disableControls || !isEditable"
          elevation="2"
          outlined
          text
          @click="onCancelSave"
        >
          Cancel <span class="sr-only">{{ item ? 'Edit' : 'Create' }} Note</span>
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script>
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'DepartmentNote',
  mixins: [Context, DepartmentEditSession],
  components: {ConfirmDialog},
  data: () => ({
    isConfirming: false,
    isEditable: false,
    isEditing: false,
    item: undefined
  }),
  created() {
    this.reset()
  },
  methods: {
    onCancelDelete() {
      this.alertScreenReader('Canceled. Nothing deleted.')
      this.$putFocusNextTick('delete-dept-note-btn')
      this.reset()
    },
    onCancelSave() {
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('edit-dept-note-btn')
      this.reset()
    },
    onDelete() {
      this.updateNote({note: null, termId: this.selectedTermId}).then(() => {
        this.alertScreenReader('Note deleted.')
        this.$putFocusNextTick('notes-title')
        this.reset()
      })
    },
    onEdit() {
      this.isEditing = true
      this.$putFocusNextTick('dept-note-textarea')
    },
    onSave() {
      this.updateNote({note: this.item, termId: this.selectedTermId}).then(() => {
        this.alertScreenReader('Note saved.')
        this.$putFocusNextTick('edit-dept-note-btn')
        this.reset()
      })
    },
    reset() {
      this.isConfirming = false
      this.isEditable = this.selectedTermId === this.$config.currentTermId
      this.isEditing = false
      this.item = this.note
    }
  }
}
</script>

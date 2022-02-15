<template>
  <div>
    <div class="pl-3">
      <h2 class="pb-1">Notes</h2>
      <div
        v-if="item && !isEditing"
        id="dept-note"
        class="text-condensed pt-3"
      >
        {{ item }}
      </div>
    </div>
    <v-textarea
      v-if="isEditing"
      id="dept-note-textarea"
      v-model="item"
      auto-grow
      :disabled="disableControls"
      hide-details="auto"
      solo
    ></v-textarea>
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
        color="secondary"
        :disabled="disableControls"
        dark
        height="unset"
        min-width="unset"
        text
        @click="isEditing = true"
      >
        Edit
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
        color="secondary"
        :disabled="disableControls"
        height="unset"
        min-width="unset"
        text
        @click="onDelete"
      >
        Delete
      </v-btn>
    </v-toolbar>
    <div v-if="isEditing" class="pt-3">
      <v-btn
        id="save-dept-note-btn"
        class="text-capitalize mr-2"
        color="secondary"
        :disabled="disableControls"
        @click="onSave"
      >
        Save Note
      </v-btn>
      <v-btn
        id="cancel-dept-note-btn"
        class="text-capitalize ml-1"
        color="secondary"
        :disabled="disableControls"
        text
        @click="onCancel"
      >
        Cancel
      </v-btn>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'DepartmentNote',
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    isEditing: false,
    item: undefined
  }),
  created() {
    this.reset()
  },
  methods: {
    onCancel() {
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('edit-dept-note-btn')
      this.reset()
    },
    onDelete() {
      // TODO: add confirmation step
      this.update().then(this.reset)
    },
    onSave() {
      this.update(this.item).then(() => {
        this.alertScreenReader('Note saved.')
        this.$putFocusNextTick('edit-dept-note-btn')
        this.reset()
      })
    },
    reset() {
      this.isEditing = false
      this.item = this.note
    }
  }
}
</script>
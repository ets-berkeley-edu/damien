<template>
  <div>
    <div class="pl-3">
      <h2 class="pb-1">Notes</h2>
      <div
        v-if="item && !isEditing"
        id="dept-note"
        class="pt-3"
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
    <div v-if="!isEditing" class="pt-3">
      <v-btn
        id="edit-dept-note-btn"
        class="text-capitalize mr-2"
        color="secondary"
        :disabled="disableControls"
        dark
        text
        @click="isEditing = true"
      >
        Edit
      </v-btn>
      <span v-if="item">|
        <v-btn
          id="delete-dept-note-btn"
          class="text-capitalize ml-1"
          color="secondary"
          :disabled="disableControls"
          text
          @click="onDelete"
        >
          Delete
        </v-btn>
      </span>
    </div>
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
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'DepartmentNote',
  mixins: [DepartmentEditSession],
  data: () => ({
    isEditing: false,
    item: undefined
  }),
  created() {
    this.reset()
  },
  methods: {
    onCancel() {
      this.reset()
    },
    onDelete() {
      this.update().then(this.reset)
    },
    onSave() {
      this.update(this.item).then(this.reset)
    },
    reset() {
      this.isEditing = false
      this.item = this.note
    }
  }
}
</script>
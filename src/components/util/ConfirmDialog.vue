<template>
  <v-dialog
    v-model="model"
    width="500"
    @click:outside="cancelAction"
    @keydown.esc="cancelAction"
  >
    <v-card>
      <v-card-title id="confirm-dialog-title" tabindex="-1">{{ title }}</v-card-title>
      <v-card-text class="pt-3">{{ text }}</v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <div class="d-flex pa-2">
          <div class="mr-2">
            <v-btn
              id="confirm-dialog-btn"
              class="text-capitalize"
              color="primary"
              @click="performAction"
            >
              Confirm <span class="sr-only">{{ buttonContext }}</span>
            </v-btn>
          </div>
          <div>
            <v-btn
              id="cancel-dialog-btn"
              class="text-capitalize"
              @click="cancelAction"
            >
              Cancel <span class="sr-only">{{ buttonContext }}</span>
            </v-btn>
          </div>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  props: {
    buttonContext: {
      default: '',
      required: false,
      type: String
    },
    cancelAction: {
      required: true,
      type: Function
    },
    confirming: {
      required: true,
      type: Boolean
    },
    performAction: {
      required: true,
      type: Function
    },
    text: {
      required: true,
      type: String
    },
    title: {
      required: true,
      type: String
    }
  },
  data: () => ({
    model: false
  }),
  watch: {
    confirming(isConfirming) {
      this.model = isConfirming
    }
  }
}
</script>

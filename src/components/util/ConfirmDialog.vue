<template>
  <v-dialog
    v-model="model"
    width="500"
    @click:outside="cancel"
    @keydown.esc="cancel"
  >
    <v-card>
      <v-card-title id="confirm-dialog-title" tabindex="-1">
        <div class="align-center d-flex">
          <div v-if="icon" class="pb-1 pr-2">
            <v-icon aria-label="Error icon" color="error">{{ icon }}</v-icon>
          </div>
          <div>
            {{ title }}
          </div>
        </div>
      </v-card-title>
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
              :disabled="disabled"
              @click="onClickConfirm"
            >
              {{ confirmButtonLabel }} <span class="sr-only">{{ buttonContext }}</span>
            </v-btn>
          </div>
          <div>
            <v-btn
              id="cancel-dialog-btn"
              class="text-capitalize"
              :disabled="disabled"
              @click="cancel"
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
    confirmButtonLabel: {
      default: 'Confirm',
      required: false,
      type: String
    },
    disabled: {
      required: false,
      type: Boolean
    },
    icon: {
      default: undefined,
      required: false,
      type: String
    },
    onClickCancel: {
      required: true,
      type: Function
    },
    onClickConfirm: {
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
  created() {
    this.model = true
    this.$putFocusNextTick('confirm-dialog-title')
  },
  methods: {
    cancel() {
      this.model = false
      this.onClickCancel()
    },
    confirm() {
      this.model = false
      this.onClickConfirm()
    }
  }
}
</script>

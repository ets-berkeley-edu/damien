<template>
  <v-dialog
    v-model="model"
    content-class="overflow-scroll"
    @click:outside="cancel"
    @keydown.esc="cancel"
  >
    <v-card class="modal-content" width="500">
      <v-card-title id="confirm-dialog-title">
        <div class="align-center d-flex pt-3 px-2">
          <div v-if="icon" class="pb-1 pr-2">
            <v-icon aria-label="Error icon" color="error">{{ icon }}</v-icon>
          </div>
          <h3>
            {{ title }}
          </h3>
        </div>
      </v-card-title>
      <v-card-text v-if="!html" class="pt-3">{{ text }}</v-card-text>
      <v-card-text v-if="html" class="pt-3" v-html="html"></v-card-text>
      <v-card-actions>
        <div class="align-center d-flex pb-3 pr-4">
          <ProgressButton
            v-if="!hideConfirm"
            id="confirm-dialog-btn"
            :action="onClickConfirm"
            class="mr-2"
            :disabled="disabled || isSaving"
            :in-progress="isSaving"
          >
            {{ confirmButtonLabel }} <span class="sr-only">{{ buttonContext }}</span>
          </ProgressButton>
          <v-btn
            id="cancel-dialog-btn"
            :disabled="disabled || isSaving"
            variant="outlined"
            @click="cancel"
          >
            Cancel <span class="sr-only">{{ buttonContext }}</span>
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import {putFocusNextTick} from '@/lib/utils'
import {onMounted, ref} from 'vue'

const props = defineProps({
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
  hideConfirm: {
    required: false,
    type: Boolean
  },
  html: {
    default: null,
    required: false,
    type: String
  },
  icon: {
    default: undefined,
    required: false,
    type: String
  },
  isSaving: {
    required: false,
    type: Boolean
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
})

const model = ref(true)

onMounted(() => putFocusNextTick('confirm-dialog-btn'))

const cancel = () => {
  model.value = false
  props.onClickCancel()
}
</script>

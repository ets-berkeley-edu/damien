<template>
  <ModalDialog
    id-prefix="confirm"
    :is-open="isOpen"
    :on-click-outside="onClickCancel"
  >
    <template #title>
      <div class="align-center d-flex px-2">
        <div v-if="icon" class="pb-1 pr-2">
          <v-icon alt="Error" color="error">{{ icon }}</v-icon>
        </div>
        <h3>
          {{ title }}
        </h3>
      </div>
    </template>
    <template #text>
      <span v-if="!html">{{ text }}</span>
      <span v-if="html" v-html="html"></span>
    </template>
    <template #actions>
      <div class="align-center d-flex">
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
          @click="onClickCancel"
        >
          Cancel <span class="sr-only">{{ buttonContext }}</span>
        </v-btn>
      </div>
    </template>
  </ModalDialog>
</template>

<script setup>
import ModalDialog from '@/components/util/ModalDialog'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {onMounted} from 'vue'

defineProps({
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
  isOpen: {
    required: false,
    type: Boolean
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
    default: '',
    required: false,
    type: String
  },
  title: {
    required: true,
    type: String
  }
})

onMounted(() => putFocusNextTick('confirm-dialog-btn'))
</script>

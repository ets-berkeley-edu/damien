<template>
  <v-dialog
    :model-value="isOpen"
    :aria-describedby="`${idPrefix}-dialog-text`"
    :aria-hidden="ariaHidden"
    :aria-labelledby="`${idPrefix}-dialog-title`"
    :fullscreen="display.xs.value"
    :persistent="persistent"
    :role="role"
    @click:outside="onClickOutside"
    @keydown.esc="onClickOutside"
    @after-enter="onOpened"
    @after-leave="onClosed"
  >
    <slot>
      <v-card
        class="modal-content"
        elevation="0"
        :max-width="maxWidth || width"
        :min-width="minWidth || width"
        :width="width"
      >
        <v-card-title v-if="slots.title" :id="`${idPrefix}-dialog-title`">
          <slot name="title" />
        </v-card-title>
        <v-card-text v-if="slots.text" :id="`${idPrefix}-dialog-text`" :class="textClass">
          <slot name="text" />
        </v-card-text>
        <v-divider v-if="slots.actions" />
        <v-card-actions v-if="slots.actions" class="d-flex justify-end px-6 py-4">
          <slot name="actions" />
        </v-card-actions>
      </v-card>
    </slot>
  </v-dialog>
</template>

<script setup>
import {nextTick, ref, useSlots} from 'vue'
import {useDisplay} from 'vuetify'
import {useContextStore} from '@/stores/context'

defineProps({
  idPrefix: {
    required: true,
    type: String
  },
  isOpen: {
    required: true,
    type: Boolean
  },
  maxWidth: {
    default: '100%',
    required: false,
    type: [Number, String]
  },
  minWidth: {
    default: '50%',
    required: false,
    type: [Number, String]
  },
  onClickOutside: {
    default: () => {},
    required: false,
    type: Function
  },
  persistent: {
    required: false,
    type: Boolean
  },
  role: {
    default: 'alertdialog',
    required: false,
    type: String
  },
  textClass: {
    default: '',
    required: false,
    type: String
  },
  width: {
    default: '31.25rem',
    required: false,
    type: [Number, String]
  }
})

const ariaHidden = ref(true)
const contextStore = useContextStore()
const display = useDisplay()
const slots = useSlots()

const onClosed = () => {
  contextStore.setIsModalOpen(false)
  nextTick(() => {
    ariaHidden.value = true
  })
}

const onOpened = () => {
  ariaHidden.value = false
  contextStore.setIsModalOpen(true)
}
</script>

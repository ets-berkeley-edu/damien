<template>
  <div class="ma-0 px-4 pb-4">
    <v-textarea
      id="service-announcement-textarea"
      v-model="text"
      aria-label="Enter service announcement for users to read"
      color="primary"
      :disabled="isSaving"
      rows="3"
      max-rows="5"
      hide-details="auto"
      solo
      variant="outlined"
    />
    <v-checkbox
      id="service-announcement-published"
      v-model="isPublished"
      :aria-describedby="undefined"
      :disabled="isSaving"
      hide-details
      label="Publish"
    />
    <ProgressButton
      id="service-announcement-save"
      :action="save"
      :disabled="!trim(text) || isSaving"
      :in-progress="isSaving"
      :text="isSaving ? 'Saving' : 'Save'"
    />
  </div>
</template>

<script setup>
import {getServiceAnnouncement, updateServiceAnnouncement} from '@/api/config'
import {onMounted, ref} from 'vue'
import {trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import ProgressButton from '@/components/util/ProgressButton.vue'

const contextStore = useContextStore()
const isPublished = ref(undefined)
const isSaving = ref(false)
const text = ref(undefined)

onMounted(() => {
  getServiceAnnouncement().then(data => {
    contextStore.setServiceAnnouncement(data)
    text.value = data.text
    isPublished.value = data.isLive
  })
})

const save = () => {
  isSaving.value = true
  updateServiceAnnouncement(text.value, isPublished.value).then(data => {
    text.value = data.text
    isPublished.value = data.isLive
    isSaving.value = false
  })
}
</script>

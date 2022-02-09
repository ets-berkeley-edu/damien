<template>
  <div class="pb-4">
    <h2>Department Contacts</h2>
    <v-card
      v-for="(contact, index) in items"
      :id="`department-contact-${index}`"
      :key="contact.id"
      class="py-3"
      flat
    >
      <strong>{{ contact.name }}</strong>
      <div>{{ contact.email }}</div>
      <div class="font-italic">
        <v-icon
          class="pb-1"
          :class="contact.canReceiveCommunications ? 'success--text' : 'muted--text'"
          small
        >
          {{ contact.canReceiveCommunications ? 'mdi-check-circle' : 'mdi-minus-circle' }}
        </v-icon>
        {{ `${contact.canReceiveCommunications ? 'Does' : 'Does not'} receive notifications` }}
      </div>
      <div class="font-italic">
        <v-icon
          class="pb-1"
          :class="contact.canViewResponseRates ? 'success--text' : 'muted--text'"
          small
        >
          {{ contact.canViewResponseRates ? 'mdi-check-circle' : 'mdi-minus-circle' }}
        </v-icon>
        {{ `${contact.canViewResponseRates ? 'Can' : 'Cannot'} view response rates` }}
      </div>
    </v-card>
  </div>
</template>

<script>
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'DepartmentContacts',
  mixins: [DepartmentEditSession],
  data: () => ({
    items: undefined
  }),

  created() {
    const items = []
    this.$_.each(this.contacts, c => {
      items.push({
        id: c.id,
        name: `${c.firstName} ${c.lastName}`,
        email: c.email,
        canReceiveCommunications: c.canReceiveCommunications,
        canViewResponseRates: c.canViewResponseRates
      })
    })
    this.items = items
  }
}
</script>
<template>
  <div>
    <div class="pb-2">
      <h1 id="page-title">Evaluation Status Dashboard - Spring 2022</h1>
    </div>
    <v-row>
      <v-col>
        <v-btn
          id="publish-btn"
          class="my-4"
          color="primary"
          :disabled="isExporting"
          @click="publish"
          @keypress.enter.prevent="publish"
        >
          <span v-if="!isExporting">Publish</span>
          <v-progress-circular
            v-if="isExporting"
            :indeterminate="true"
            color="white"
            rotate="5"
            size="20"
            width="3"
          ></v-progress-circular>
        </v-btn>
      </v-col>
      <v-col>
        <h2>Term Exports</h2>
        <ul id="term-exports-list">
          <li v-for="e in exports" :key="e.createdAt">
            <a :href="`${$config.apiBaseUrl}/api/export/${encodeURIComponent(e.s3Path)}`">{{ e.createdAt | moment('M/DD/YYYY HH:mm:SS') }}</a>
          </li>
        </ul>
      </v-col>
    </v-row>
    <v-card outlined class="elevation-1">
      <v-data-table
        id="department-table"
        disable-pagination
        :headers="headers"
        :header-props="{'every-item': true, 'some-items': true}"
        hide-default-footer
        :items="departments"
        show-select
      >
        <template #header.data-table-select>
          <div class="d-flex flex-row notify-all">
            <v-simple-checkbox
              id="checkbox-select-dept-all"
              :indeterminate="someDepartmentsSelected"
              :ripple="false"
              :value="allDepartmentsSelected"
              @input="toggleSelectAll"
            ></v-simple-checkbox>
            <div class="d-flex align-center">Send notification</div>
            <v-btn
              v-if="!isCreatingNotification"
              id="open-notification-form-btn"
              class="ma-2 secondary text-capitalize"
              color="secondary"
              :disabled="$_.isEmpty(selectedDepartmentIds)"
              small
              @click="() => isCreatingNotification = true"
              @keypress.enter.prevent="() => isCreatingNotification = true"
            >
              Apply
            </v-btn>
          </div>
        </template>
        <template #body="{items}">
          <tbody>
            <template v-for="(department, index) in items">
              <tr :id="`department-${index}`" :key="department.name">
                <td>
                  <v-simple-checkbox
                    :id="`checkbox-select-dept-${$_.kebabCase(department.deptName)}`"
                    :ripple="false"
                    :value="isSelected(department)"
                    @input="toggleSelect(department)"
                  ></v-simple-checkbox>
                </td>
                <td class="department-name">
                  <router-link :id="`link-to-dept-${$_.kebabCase(department.deptName)}`" :to="`/department/${department.id}`">
                    {{ department.deptName }}
                    ({{ $_.compact($_.keys(department.catalogListings)).join(', ') }})
                  </router-link>
                </td>
                <td class="department-lastUpdated">
                  {{ department.updatedAt | moment('MMM D, YYYY h:mma') }}
                </td>
                <td class="department-errors">
                  <span class="font-italic muted--text">TODO</span>
                </td>
                <td class="department-confirmed">
                  <span class="font-italic muted--text">TODO</span>
                </td>
                <td class="department-note">
                  {{ $_.get(department, `notes.${$config.currentTermId}.note`) }}
                </td>
              </tr>
            </template>
          </tbody>
        </template>
      </v-data-table>
    </v-card>
    <v-dialog v-model="isCreatingNotification" width="600">
      <NotificationForm
        v-if="isCreatingNotification"
        :after-send="afterSendNotification"
        :on-cancel="cancelSendNotification"
        :recipients="notificationRecipients"
      />
    </v-dialog>
  </div>
</template>

<script>
import {getDepartmentsEnrolled} from '@/api/departments'
import {exportEvaluations, getExports} from '@/api/evaluations'
import Context from '@/mixins/Context.vue'
import NotificationForm from '@/components/admin/NotificationForm'

export default {
  name: 'StatusBoard',
  components: {NotificationForm},
  mixins: [Context],
  data: () => ({
    departments: [],
    exports: [],
    headers: [
      {class: 'pt-12 pb-3', text: 'Department', value: 'deptName'},
      {class: 'pt-12 pb-3', text: 'Last Updated', value: 'updatedAt'},
      {class: 'pt-12 pb-3', text: 'Errors', value: 'errors'},
      {class: 'pt-12 pb-3', text: 'Confirmed', value: 'confirmed'},
      {class: 'pt-12 pb-3', text: 'Notes', value: 'notes'},
    ],
    isCreatingNotification: false,
    isExporting: false,
    selectedDepartmentIds: []
  }),
  computed: {
    allDepartmentsSelected() {
      return !!(this.$_.size(this.selectedDepartmentIds) && this.$_.size(this.selectedDepartmentIds) === this.$_.size(this.departments))
    },
    notificationRecipients() {
      let recipients = []
      this.$_.each(this.departments, d => {
        if (this.isSelected(d)) {
          const departmentRecipients = this.$_.filter(d.contacts, 'canReceiveCommunications')
          if (departmentRecipients.length) {
            recipients.push({
              'deptId': d.id,
              'deptName': d.deptName,
              'recipients': this.$_.filter(d.contacts, 'canReceiveCommunications')
            })
          }
        }
      })
      return recipients
    },
    someDepartmentsSelected() {
      return !!(this.$_.size(this.selectedDepartmentIds) && this.$_.size(this.selectedDepartmentIds) < this.$_.size(this.departments))
    }
  },
  created() {
    this.$loading()
    getDepartmentsEnrolled().then(data => {
      this.departments = data
      this.$ready('Status Board')
    })
    getExports().then(data => {
      this.exports = data
    })
  },
  methods: {
    afterSendNotification() {
      this.selectedDepartmentIds = []
      this.isCreatingNotification = false
      this.alertScreenReader('Notification sent.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    cancelSendNotification() {
      this.isCreatingNotification = false
      this.alertScreenReader('Notification canceled.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    isSelected(department) {
      return this.$_.includes(this.selectedDepartmentIds, department.id)
    },
    publish() {
      this.isExporting = true
      this.alertScreenReader('Publishing.')
      exportEvaluations().then(data => {
        this.exports.unshift(data)
        this.isExporting = false
        this.alertScreenReader('Publication complete.')
      })
    },
    toggleSelect(department) {
      const index = this.$_.indexOf(this.selectedDepartmentIds, department.id)
      if (index === -1) {
        this.selectedDepartmentIds.push(department.id)
      } else {
        this.selectedDepartmentIds.splice(index, 1)
      }
    },
    toggleSelectAll() {
      if (this.allDepartmentsSelected) {
        this.selectedDepartmentIds = []
      } else {
        this.selectedDepartmentIds = this.$_.map(this.departments, 'id')
      }
    }
  }
}
</script>

<style scoped>
.department-confirmed {
  width: 10%;
}
.department-errors {
  width: 10%;
}
.department-lastUpdated {
  width: 20%;
}
.department-name {
  width: 25%;
}
.department-note {
  width: 35%;
}
.notify-all {
  position: absolute;
  top: 0;
}
</style>

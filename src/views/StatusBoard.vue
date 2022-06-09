<template>
  <div class="pt-2">
    <v-row class="pb-2" no-gutters>
      <v-col cols="12" md="9" class="d-flex align-baseline">
        <h1 id="page-title">Evaluation Status Dashboard - {{ selectedTermName }}</h1>
      </v-col>
      <v-col cols="12" md="3" class="d-flex align-center justify-end flex-wrap">
        <div v-if="$currentUser.isAdmin" class="d-flex align-baseline mr-3">
          <label
            id="select-term-label"
            for="select-term"
            class="align-self-baseline text-nowrap pr-3"
          >
            Term:
          </label>
          <select
            id="select-term"
            v-model="selectedTermId"
            class="native-select-override select-term my-2 px-3"
            :class="this.$vuetify.theme.dark ? 'dark' : 'light'"
            :disabled="loading"
            @change="onChangeTerm"
          >
            <option
              v-for="term in availableTerms"
              :id="`term-option-${term.id}`"
              :key="term.id"
              :value="term.id"
            >
              {{ term.name }}
            </option>
          </select>
        </div>
        <div class="d-flex ml-4">
          <label for="toggle-term-locked" class="text-nowrap pr-4 py-2">
            {{ `${isCurrentTermLocked ? 'Unlock' : 'Lock'} current term` }}
          </label>
          <v-switch
            id="toggle-term-locked"
            v-model="isCurrentTermLocked"
            class="my-auto"
            color="tertiary"
            dense
            hide-details
            inset
            @change="toggleCurrentTermLocked"
          />
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="auto" class="d-flex mr-auto">
        <v-btn
          id="publish-btn"
          class="align-self-end my-4"
          color="primary"
          :disabled="isExporting || loading"
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
      <v-col cols="auto" class="pr-8 mb-2">
        <h2>Term Exports</h2>
        <ul id="term-exports-list" class="pl-2">
          <li v-for="(e, index) in exports" :key="index">
            <a
              :id="`term-export-${index}`"
              download
              :href="`${$config.apiBaseUrl}/api/export/${encodeURIComponent(e.s3Path)}`"
            >
              <v-icon
                aria-hidden="false"
                aria-label="download"
                class="pr-2"
                color="anchor"
                role="img"
                small
              >
                mdi-tray-arrow-down
              </v-icon>
              {{ e.createdAt | moment('M/DD/YYYY HH:mm:SS') }}
              <span class="sr-only">term export</span>
            </a>
          </li>
        </ul>
      </v-col>
    </v-row>
    <v-card outlined class="elevation-1">
      <v-data-table
        id="department-table"
        disable-pagination
        :disable-sort="loading"
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
              :disabled="loading"
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
                <td :id="`last-updated-dept-${department.id}`" class="department-lastUpdated">
                  {{ department.updatedAt | moment('MMM D, YYYY h:mma') }}
                </td>
                <td class="department-errors">
                  <v-chip
                    v-if="department.totalInError"
                    :id="`errors-count-dept-${department.id}`"
                    class="error error--text error-count"
                    outlined
                    small
                  >
                    {{ department.totalInError }} <span class="sr-only">errors</span>
                  </v-chip>
                  <v-icon
                    v-if="!department.totalInError"
                    aria-hidden="false"
                    aria-label="no errors"
                    class="success--text"
                    role="img"
                  >
                    mdi-check-circle
                  </v-icon>
                </td>
                <td class="department-confirmed">
                  <v-icon
                    v-if="department.totalConfirmed > 0 && department.totalConfirmed === department.totalEvaluations"
                    aria-hidden="false"
                    aria-label="all confirmed"
                    class="success--text"
                    role="img"
                  >
                    mdi-check-circle
                  </v-icon>
                  <span v-if="department.totalConfirmed === 0 || department.totalConfirmed < department.totalEvaluations">
                    <span aria-hidden="true">{{ department.totalConfirmed }} / {{ department.totalEvaluations }}</span>
                    <span class="sr-only">{{ department.totalConfirmed }} of {{ department.totalEvaluations }} confirmed</span>
                  </span>
                </td>
                <td class="department-note">
                  {{ $_.get(department, `notes.${selectedTermId}.note`) }}
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
import {getEvaluationTerm, lockEvaluationTerm, unlockEvaluationTerm} from '@/api/evaluationTerms'
import Context from '@/mixins/Context.vue'
import NotificationForm from '@/components/admin/NotificationForm'

export default {
  name: 'StatusBoard',
  components: {NotificationForm},
  mixins: [Context],
  data: () => ({
    availableTerms: [],
    selectedTermId: null,
    selectedTermName: null,
    departments: [],
    exports: [],
    headers: [],
    isCreatingNotification: false,
    isExporting: false,
    isCurrentTermLocked: false,
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
    this.selectedTermId = this.$config.currentTermId
    this.selectedTermName = this.$config.currentTermName
    this.availableTerms = this.$config.availableTerms
    this.headers = [
      {class: 'text-nowrap pt-12 pb-3', text: 'Department', value: 'deptName'},
      {class: 'text-nowrap pt-12 pb-3', text: 'Last Updated', value: 'updatedAt'},
      {class: 'text-nowrap pt-12 pb-3', text: 'Errors', value: 'totalInError'},
      {class: 'text-nowrap pt-12 pb-3', text: 'Confirmed', value: 'totalConfirmed'},
      {
        class: 'text-nowrap pt-12 pb-3',
        sort: (a, b) => {
          const deptANote = this.$_.get(a, `${this.selectedTermId}.note`)
          const deptBNote = this.$_.get(b, `${this.selectedTermId}.note`)
          // Nulls last
          return deptANote && deptBNote ? deptANote.localeCompare(deptBNote) : !deptANote - !deptBNote
        },
        text: 'Notes',
        value: 'notes'
      },
    ]
    getDepartmentsEnrolled(false, false, true).then(data => {
      this.departments = data
      this.$ready('Status Board')
    })
    getExports().then(data => {
      this.exports = data
    })
    getEvaluationTerm(this.selectedTermId).then(data => {
      this.isCurrentTermLocked = data.isLocked === true
    })
  },
  methods: {
    afterSendNotification() {
      this.selectedDepartmentIds = []
      this.isCreatingNotification = false
      this.alertScreenReader('Notification sent.')
      this.$putFocusNextTick('open-notification-form-btn')
    },
    toggleCurrentTermLocked() {
      if (this.isCurrentTermLocked) {
        lockEvaluationTerm(this.selectedTermId).then(() => {
          this.alertScreenReader(`Locked ${this.selectedTermName}`)
        })
      } else {
        unlockEvaluationTerm(this.selectedTermId).then(() => {
          this.alertScreenReader(`Unlocked ${this.selectedTermName}`)
        })
      }
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
    },
    onChangeTerm(event) {
      const term = this.$_.find(this.availableTerms, ['id', event.target.value])
      this.selectedTermId = term.id
      this.selectedTermName = term.name
      this.alertScreenReader(`Loading ${this.$_.get(term, 'name', 'term')}`)
      this.$putFocusNextTick('select-term')
    },
  }
}
</script>

<style scoped>
.department-confirmed {
  min-width: 120px;
  width: 10%;
}
.department-errors {
  min-width: 100px;
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
.error-count {
  border-width: 2px;
  font-weight: bold;
  padding: 0 7px;
}
.notify-all {
  position: absolute;
  top: 0;
}
.select-term {
  max-width: 200px;
}
</style>

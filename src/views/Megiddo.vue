<template>
  <div class="pt-2">
    <v-row no-gutters>
      <v-col cols="9" class="d-flex align-center">
        <h1 id="page-title" :style="{color: titleHexColor}">
          Publish<span v-if="selectedTermName"> - {{ selectedTermName }}</span>
        </h1>
      </v-col>
      <v-col cols="3">
        <TermSelect :after-select="refresh" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="auto" class="mr-auto">
        <div v-if="$_.size(confirmed)">
          Rows confirmed for publication:
          <ul id="confirmed-list" class="pl-4">
            <li v-for="(department, index) in confirmed" :key="index">
              {{ department.deptName }} ({{ department.count }})
            </li>
          </ul>
        </div>
        <div v-if="$_.size(blockers)">
          <v-icon color="error">
            mdi-alert-circle
          </v-icon>
          Publication is blocked by errors in departments:
          <ul id="blocker-list" class="pl-4">
            <li v-for="(count, deptName) in blockers" :key="deptName">
              {{ deptName }} ({{ count }})
            </li>
          </ul>
        </div>
        <v-btn
          id="publish-btn"
          class="publish-btn align-self-end my-4 mr-2"
          color="secondary"
          :disabled="isExporting || loading || !!$_.size(blockers)"
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
        <v-slide-x-reverse-transition>
          <span v-if="isExporting" class="mx-2">Publishing in progress.</span>
        </v-slide-x-reverse-transition>
        <v-btn
          id="status-btn"
          class="mx-2"
          color="secondary"
          :disabled="isUpdatingStatus || !isExporting || loading"
          fab
          x-small
          @click="onUpdateStatus"
          @keypress.enter.prevent="onUpdateStatus"
        >
          <v-icon>mdi-refresh</v-icon>
          <span class="sr-only">Refresh</span>
        </v-btn>
      </v-col>
      <v-col cols="auto" class="pr-4 mb-2">
        <v-expansion-panels
          v-model="exportsPanel"
          class="term-exports"
          :disabled="loading"
          flat
        >
          <v-expansion-panel class="panel-override">
            <v-expansion-panel-header id="term-exports-btn" class="term-exports-btn">
              <h2>Term Exports</h2>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <div v-if="$_.isEmpty(termExports)" id="term-exports-no-data">There are no {{ selectedTermName }} exports.</div>
              <ul v-if="!$_.isEmpty(termExports)" id="term-exports-list" class="pl-2">
                <li v-for="(e, index) in termExports" :key="index">
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
                    {{ e.createdAt | moment(dateFormat) }}
                    <span class="sr-only">term export</span>
                  </a>
                </li>
              </ul>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-card v-if="!loading" outlined class="elevation-1">
      <EvaluationTable :readonly="true" />
    </v-card>
  </div>
</template>

<script>
import {exportEvaluations, getConfirmed, getExportStatus, getExports, getValidation} from '@/api/evaluations'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import TermSelect from '@/components/util/TermSelect'
import Util from '@/mixins/Util'

export default {
  name: 'Megiddo',
  components: {
    EvaluationTable,
    TermSelect
  },
  mixins: [Context, DepartmentEditSession, Util],
  data: () => ({
    blockers: {},
    confirmed: [],
    dateFormat: 'M/DD/YYYY HH:mm:SS',
    exportsPanel: undefined,
    isExporting: false,
    isUpdatingStatus: false,
    termExports: []
  }),
  created() {
    this.updateStatus()
  },
  methods: {
    onUpdateStatus() {
      this.isUpdatingStatus = true
      this.updateStatus()
      this.$putFocusNextTick('status-btn')
    },
    publish() {
      this.isExporting = true
      this.alertScreenReader('Publishing.')
      exportEvaluations(this.selectedTermId).then(() => {
        this.snackbarOpen('Publication has started and will run in the background.')
        this.$putFocusNextTick('publish-btn')
      })
    },
    refresh() {
      this.$loading()
      this.alertScreenReader(`Loading ${this.selectedTermName}`)
      Promise.all([getValidation(this.selectedTermId), getConfirmed(this.selectedTermId), getExports(this.selectedTermId)]).then(responses => {
        this.setEvaluations(this.$_.sortBy(responses[0], 'sortableCourseName'))
        this.confirmed = responses[1]
        this.termExports = responses[2]
        this.$ready(`Publish ${this.selectedTermName || ''}`)
      })
    },
    updateStatus() {
      getExportStatus().then(response => {
        this.isExporting = false
        if (this.$_.isEmpty(response)) {
          return false
        }
        const lastUpdate = this.$moment(response.updatedAt)
        const now = this.$moment()
        if (now.diff(lastUpdate, 'hours') < 1) {
          this.showStatus(response)
        }
      }).finally(() => {
        this.$nextTick(() => {
          this.isUpdatingStatus = false
        })
      })
    },
    showStatus(termExport) {
      const exportLabel = this.$moment(termExport.createdAt).format(this.dateFormat)
      const term = this.$_.find(this.$config.availableTerms, {'id': termExport.termId})
      if (termExport.status === 'success') {
        this.snackbarOpen(
          `Success! Publication of ${term.name} term export <b>${exportLabel || ''}</b> is complete.`,
          'success'
        )
      } else if (termExport.status === 'error') {
        this.reportError(`Error: Publication of ${term.name} term export <b>${exportLabel || ''}</b> failed.`)
      } else {
        this.isExporting = true
      }
    }
  }
}
</script>

<style scoped>
.publish-btn {
  width: 8rem;
}
.term-exports {
  width: 325px;
}
.term-exports-btn {
  width: 225px;
}
</style>

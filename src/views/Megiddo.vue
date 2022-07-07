<template>
  <div class="pt-2">
    <v-row class="pb-2" no-gutters>
      <v-col cols="12" md="9" class="d-flex align-baseline">
        <h1 id="page-title">
          Publish<span v-if="selectedTermName"> - {{ selectedTermName }}</span>
        </h1>
      </v-col>
      <v-col cols="12" md="3">
        <TermSelect :after-select="refresh" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="auto" class="mr-auto">
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
          class="align-self-end my-4"
          color="primary"
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
                    {{ e.createdAt | moment('M/DD/YYYY HH:mm:SS') }}
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
import {exportEvaluations, getExports, getValidation} from '@/api/evaluations'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import TermSelect from '@/components/util/TermSelect'

export default {
  name: 'Megiddo',
  components: {
    EvaluationTable,
    TermSelect
  },
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    blockers: {},
    exportsPanel: undefined,
    isExporting: false,
    termExports: []
  }),
  methods: {
    publish() {
      this.isExporting = true
      this.alertScreenReader('Publishing.')
      exportEvaluations().then(data => {
        this.termExports.unshift(data)
        this.isExporting = false
        this.alertScreenReader('Publication complete.')
      })
    },
    refresh() {
      this.$loading()
      this.alertScreenReader(`Loading ${this.selectedTermName}`)
      Promise.all([getValidation(), getExports(this.selectedTermId)]).then(responses => {
        this.setEvaluations(this.$_.sortBy(responses[0], 'sortableCourseNumber'))
        this.termExports = responses[1]
        this.$ready(`Publish ${this.selectedTermName || ''}`)
      })
    }
  }
}
</script>

<style scoped>
.term-exports {
  width: 325px;
}
.term-exports-btn {
  width: 225px;
}
</style>

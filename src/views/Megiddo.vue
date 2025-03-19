<template>
  <div class="page-margins">
    <PageHeader>
      Publish<span v-if="contextStore.selectedTermName"> &mdash;&nbsp;{{ contextStore.selectedTermName }}</span>
      <template #append>
        <TermSelect />
      </template>
    </PageHeader>
    <v-container v-if="!contextStore.loading" class="pa-0" fluid>
      <v-row>
        <v-col cols="12" md="6">
          <div v-if="size(confirmed)" class="pb-3 pt-2">
            <h2 class="align-with-term-exports">Confirmed for publication</h2>
            <ul id="confirmed-list" class="pl-4">
              <li v-for="(department, index) in confirmed" :key="index">
                {{ department.deptName }} <span class="text-muted">({{ department.count }})</span>
              </li>
            </ul>
          </div>
          <div id="blockers" aria-live="assertive" role="alert">
            <v-alert
              v-if="size(blockers)"
              class="my-3 alert-blockers"
              density="compact"
              :icon="mdiAlertCircle"
              :role="undefined"
              title="Publication is blocked by errors in departments:"
              type="error"
              variant="tonal"
            >
              <ul id="blocker-list" class="pl-4">
                <li v-for="(count, deptName) in blockers" :key="deptName">
                  {{ deptName }} ({{ count }})
                </li>
              </ul>
            </v-alert>
          </div>
          <ProgressButton
            id="publish-btn"
            :action="publish"
            aria-describedby="blockers"
            color="secondary"
            :disabled="isExporting || !isEmpty(blockers) || isEmpty(confirmed)"
            :in-progress="isExporting"
            size="large"
            :text="isExporting ? 'Publishing...' : 'Publish'"
          />
          <v-btn
            id="status-btn"
            aria-label="Refresh"
            class="mx-2"
            color="secondary"
            :disabled="isUpdatingStatus || !isExporting"
            fab
            :icon="mdiRefresh"
            size="small"
            @click="onUpdateStatus"
          />
        </v-col>
        <v-col>
          <v-expansion-panels
            v-model="exportsPanel"
            class="term-exports mr-15"
            flat
            tile
          >
            <v-expansion-panel class="border-sm">
              <v-expansion-panel-title id="term-exports-btn" class="term-exports-btn text-no-wrap">
                <h2>Term Exports</h2>
              </v-expansion-panel-title>
              <v-expansion-panel-text v-if="isEmpty(termExports)" class="border-t-sm pt-3">
                <div id="term-exports-no-data">
                  There are no {{ contextStore.selectedTermName }} exports.
                </div>
              </v-expansion-panel-text>
              <v-expansion-panel-text v-if="!isEmpty(termExports)">
                <ul id="term-exports-list" class="pl-2">
                  <li v-for="(e, index) in termExports" :key="index">
                    <a
                      :id="`term-export-${index}`"
                      download
                      :href="`${contextStore.config.apiBaseUrl}/api/export/${encodeURIComponent(e.s3Path)}`"
                    >
                      <v-icon
                        aria-hidden="false"
                        aria-label="download"
                        class="pr-2"
                        color="anchor"
                        :icon="mdiTrayArrowDown"
                        role="presentation"
                        size="small"
                      />
                      {{ toLocaleFromISO(e.createdAt, dateFormat) }}
                      <span class="sr-only">term export</span>
                    </a>
                  </li>
                </ul>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
      <div class="pt-6">
        <h2 class="mb-1">Outstanding errors</h2>
        <EvaluationTable :readonly="true" />
      </div>
    </v-container>
  </div>
</template>

<script setup>
import EvaluationTable from '@/components/evaluation/EvaluationTable'
import PageHeader from '@/components/util/PageHeader'
import ProgressButton from '@/components/util/ProgressButton.vue'
import TermSelect from '@/components/util/TermSelect'
import {DateTime} from 'luxon'
import {alertScreenReader, putFocusNextTick, toLocaleFromISO} from '@/lib/utils'
import {exportEvaluations, getConfirmed, getExportStatus, getExports, getValidation} from '@/api/evaluations'
import {filter, find, groupBy, isEmpty, mapValues, size, sortBy} from 'lodash'
import {mdiAlertCircle, mdiRefresh, mdiTrayArrowDown} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useDepartmentStore} from '@/stores/department/department-edit-session'

const contextStore = useContextStore()
const departmentStore = useDepartmentStore()
const blockers = ref({})
const confirmed = ref([])
const dateFormat = DateTime.DATETIME_SHORT_WITH_SECONDS
const exportsPanel = ref(undefined)
const isExporting = ref(false)
const isUpdatingStatus = ref(false)
const termExports = ref([])

onMounted(() => refresh())

const onUpdateStatus = () => {
  updateStatus().then(() => putFocusNextTick('status-btn', {scroll: false}))
}

const publish = () => {
  isExporting.value = true
  alertScreenReader('Publishing.')
  exportEvaluations(contextStore.selectedTermId).then(() => {
    contextStore.snackbarOpen('Publication has started and will run in the background.')
    putFocusNextTick('publish-btn', {scroll: false})
  })
}

const refresh = () => {
  contextStore.loadingStart(`Loading ${contextStore.selectedTermName}`)
  Promise.all([
    getValidation(contextStore.selectedTermId),
    getConfirmed(contextStore.selectedTermId),
    getExports(contextStore.selectedTermId),
    updateStatus()
  ]).then(responses => {
    departmentStore.setEvaluations(sortBy(responses[0], 'sortableCourseName'))
    const blockerEvals = filter(responses[0], {'valid': false, 'status': 'confirmed'})
    blockers.value = mapValues(groupBy(blockerEvals, e => e.department.name), 'length')
    confirmed.value = responses[1]
    termExports.value = responses[2]
    contextStore.loadingComplete(`Publish ${contextStore.selectedTermName || ''}`)
  })
}

const updateStatus = async () => {
  isUpdatingStatus.value = true
  try {
    const response = await getExportStatus()
    if (!isEmpty(response)) {
      const lastUpdate = DateTime.fromISO(response.updatedAt)
      if (DateTime.now().diff(lastUpdate, ['hours']).as('hours') < 1) {
        showStatus(response)
      }
    }
  } finally {
    nextTick(() => {
      isUpdatingStatus.value = false
    })
  }
}

const showStatus = termExport => {
  const exportLabel = toLocaleFromISO(termExport.createdAt, dateFormat)
  const term = find(contextStore.config.availableTerms, {'id': termExport.termId})
  contextStore.snackbarHide()
  nextTick(() => {
    if (termExport.status === 'success') {
      isExporting.value = false
      contextStore.snackbarOpen(
        `Success! Publication of ${term.name} term export <b>${exportLabel || ''}</b> is complete.`,
        'success'
      )
    } else if (termExport.status === 'error') {
      isExporting.value = false
      contextStore.snackbarReportError(`Error: Publication of ${term.name} term export <b>${exportLabel || ''}</b> failed.`)
    } else if (termExport.status === 'started') {
      contextStore.snackbarOpen('Publication in progress.')
    }
  })
}
</script>

<style scoped>
:deep(.alert-blockers.v-theme--dark .v-alert__underlay) {
  opacity: 0.08 !important;
}
.align-with-term-exports {
  margin-top: 2px;
}
.term-exports {
  min-width: 325px;
}
.term-exports-btn {
  min-width: 225px;
}
</style>

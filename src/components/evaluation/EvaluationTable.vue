<template>
  <v-container
    v-if="evaluations.length"
    class="pa-0"
    max-width="100%"
    @resize="setStickySearchPosition"
  >
    <div
      class="bg-surface-variant elevation-2 py-2 sticky"
      role="search"
    >
      <div class="align-center d-flex flex-wrap px-4 pt-2" :class="{'pb-2': readonly}">
        <v-text-field
          id="evaluation-search-input"
          v-model="searchFilter"
          :aria-describedby="undefined"
          aria-label="Filter evaluations table by search terms."
          class="bg-surface mr-3"
          clearable
          color="primary"
          density="comfortable"
          hide-details
          label="Filter courses"
          max-width="600px"
          type="search"
        />
        <AddCourseSection
          v-if="!readonly"
          id="add-course-section"
          :allow-edits="allowEdits"
        />
      </div>
      <div class="align-center d-flex flex-wrap justify-space-between px-4">
        <div v-if="!readonly && allowEdits" class="d-flex pt-2">
          <v-checkbox
            id="select-all-evals-checkbox"
            :aria-describedby="undefined"
            class="select-all-evals my-auto mr-3"
            color="primary"
            density="compact"
            :disabled="!searchFilterResults.length || disableControls"
            :false-value="!someEvaluationsSelected && !allEvaluationsSelected"
            hide-details
            :indeterminate="someEvaluationsSelected"
            :input-value="someEvaluationsSelected || allEvaluationsSelected"
            :model-value="allEvaluationsSelected"
            :ripple="false"
            @update:model-value="toggleSelectAll"
          >
            <template #label>
              <span class="text-no-wrap my-auto pl-1">
                {{ someEvaluationsSelected || allEvaluationsSelected ? 'Unselect' : 'Select' }} all
              </span>
            </template>
          </v-checkbox>
          <div class="evaluation-actions">
            <EvaluationActions v-if="!readonly" :reset="() => duplicatingEvaluationId = null" />
          </div>
        </div>
        <div class="align-center d-flex flex-wrap pt-2">
          <div class="mr-2">Show statuses:</div>
          <v-btn-toggle
            v-model="selectedFilterTypes"
            aria-controls="evaluation-table"
            borderless
            class="status-filter d-flex flex-wrap"
            color="tertiary"
            density="compact"
            flat
            multiple
            rounded
          >
            <v-btn
              v-for="status in keys(filterTypes)"
              :id="`evaluations-filter-${status}`"
              :key="status"
              :active="filterTypes[status].enabled"
              :aria-pressed="filterTypes[status].enabled"
              :disabled="disableControls"
              color="tertiary"
              class="mb-1 mr-1 rounded-pill text-uppercase"
              height="30"
              size="small"
              :value="status"
              :width="filterTypes[status].width"
            >
              <div class="align-center d-flex justify-space-between">
                <v-icon
                  v-if="filterTypes[status].enabled"
                  color="success"
                  :icon="filterTypes[status].enabled ? mdiCheckCircle : mdiPlusCircle"
                  left
                />
                <div class="pl-1">
                  <span class="sr-only">{{ filterTypes[status].enabled ? 'Hide' : 'Show' }} evaluations of marked with</span>
                  {{ filterTypes[status].label }}
                </div>
                <div :class="filterTypes[status].enabled ? 'text-white' : 'text-grey darken-2'">
                  <v-chip
                    class="ml-2 px-1"
                    :class="{'font-weight-bold': filterTypes[status].enabled}"
                    size="small"
                  >
                    {{ filterTypeCounts(status) }}<span class="sr-only"> evaluations</span>
                  </v-chip>
                </div>
              </div>
            </v-btn>
          </v-btn-toggle>
        </div>
      </div>
    </div>
    <div
      id="evaluation-table-search-results-desc"
      aria-atomic="true"
      aria-live="polite"
      class="sr-only"
    >
      <span v-if="searchFilter">{{ pluralize('evaluation', size(searchFilterResults.value)) }} displayed.</span>
    </div>
    <v-data-table
      id="evaluation-table"
      v-model:sort-by="sortBy"
      class="v-table-hidden-row-override v-table-overflow-override pt-3"
      :custom-filter="customFilter"
      density="compact"
      :headers="evaluationHeaders"
      hide-default-footer
      :items="visibleEvaluations"
      items-per-page="-1"
      :loading="contextStore.loading"
      must-sort
      :search="searchFilter"
      :sort-by="sortBy"
      @update:current-items="onChangeSearchFilter"
      @update:sort-by="onUpdateSortBy"
    >
      <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: _sortBy}">
        <SortableTableHeader
          :columns="columns"
          :is-sorted="isSorted"
          :on-sort="toggleSort"
          :sort-desc="get(_sortBy, 'order') === 'desc'"
          :sort-icon="getSortIcon"
        />
      </template>
      <template #body="{items}">
        <transition-group v-if="size(items)" name="evaluation-row">
          <template v-for="(evaluation, rowIndex) in items" :key="evaluation.id">
            <tr
              :id="rowId(evaluation, rowIndex)"
              class="evaluation-row"
              :class="{
                'bg-evaluation-active text-tertiary': isRowActive(evaluation) && !isEditing(evaluation),
                'bg-evaluation-done': !isRowActive(evaluation) && !isEditing(evaluation) && evaluation.status === 'confirmed',
                'bg-evaluation-ignore text-muted': !isRowActive(evaluation) && !isEditing(evaluation) && evaluation.status === 'ignore',
                'bg-tertiary text-white border-bottom-none': evaluation.id === editRowId,
                'bg-evaluation-to-do': !isRowActive(evaluation) && !isEditing(evaluation) && evaluation.status === 'review',
                'bg-evaluation-xlisting': !isRowActive(evaluation) && !isEditing(evaluation) && !evaluation.status && (evaluation.crossListedWith || evaluation.roomSharedWith),
                'text-primary': isRowSelected(evaluation) && !isRowActive(evaluation) && !isEditing(evaluation)
              }"
              @mouseenter="onMouseenterRow(evaluation)"
              @mouseleave="onMouseleaveRow(evaluation)"
            >
              <td v-if="readonly" :id="`evaluation-${rowIndex}-department`" class="align-middle py-1 pl-2">
                <router-link :to="`/department/${get(evaluation.department, 'id')}`" class="font-weight-bold">
                  {{ get(evaluation.department, 'name') }}
                </router-link>
              </td>
              <td
                v-if="!readonly && allowEdits && !(allowEdits && isEditing(evaluation))"
                :id="`evaluation-${rowIndex}-select`"
                class="align-middle pl-1 pr-5"
              >
                <v-checkbox
                  v-if="!isEditing(evaluation)"
                  :id="`evaluation-${rowIndex}-checkbox`"
                  :key="`checkbox-${rowIndex}`"
                  :aria-describedby="undefined"
                  :aria-description="`${describeRow(evaluation)}`"
                  :aria-label="`Evaluation ${rowIndex + 1} of ${size(items)}`"
                  class="d-flex justify-center"
                  :color="`${isRowActive(evaluation) ? 'tertiary' : 'primary'}`"
                  :disabled="editRowId === evaluation.id || disableControls"
                  hide-details
                  :model-value="evaluation.isSelected"
                  :ripple="false"
                  @update:model-value="() => departmentStore.toggleSelectEvaluation(evaluation)"
                />
              </td>
              <td
                :id="`evaluation-${rowIndex}-status`"
                class="pl-1 pr-3"
                :class="{
                  'align-middle': !isEditing(evaluation),
                  'pr-1': isRowActive(evaluation)
                }"
                :colspan="allowEdits && isEditing(evaluation) ? 2 : 1"
              >
                <v-chip
                  v-if="isStatusVisible(evaluation)"
                  :key="`status-${rowIndex}`"
                  class="mx-auto px-1 status-label text-caption"
                  :class="{
                    'bg-evaluation-done-label': evaluation.status === 'confirmed',
                    'bg-evaluation-ignore-label': evaluation.status === 'ignore',
                    'bg-evaluation-to-do-label': evaluation.status === 'review',
                    'sr-only': hoverId === evaluation.id && allowEdits && !readonly
                  }"
                >
                  {{ displayStatus(evaluation) }}
                </v-chip>
                <div
                  v-if="allowEdits && !isEditing(evaluation) && (!readonly || !evaluation.status)"
                  class="pill-invisible mx-auto"
                >
                  <v-menu
                    :key="`menu-${rowIndex}`"
                    scroll-strategy="none"
                    z-index="0"
                    @update:model-value="isOpen => onToggleEditMenu(isOpen, evaluation)"
                  >
                    <template #activator="{props: menuProps}">
                      <v-btn
                        :id="`evaluation-menu-btn-${evaluation.id}`"
                        :append-icon="mdiChevronDown"
                        class="mx-auto px-1 text-uppercase evaluation-row-btn"
                        :class="{
                          'sr-only': !isRowActive(evaluation),
                          'focus-btn': evaluation.id === focusedEditButtonEvaluationId
                        }"
                        color="tertiary"
                        :disabled="!allowEdits || disableControls"
                        max-width="150"
                        min-width="54"
                        text="Edit"
                        variant="text"
                        width="100%"
                        v-bind="menuProps"
                        @blur="() => focusedEditButtonEvaluationId = null"
                        @focus="() => focusedEditButtonEvaluationId = evaluation.id"
                      />
                    </template>
                    <v-list
                      :id="`evaluation-menu-list-${evaluation.id}`"
                      class="border-sm py-0"
                      rounded="sm"
                    >
                      <v-list-item
                        :id="`option-edit-evaluation-${evaluation.id}`"
                        base-color="secondary"
                        density="compact"
                        @click="() => onEditEvaluation(evaluation)"
                      >
                        <v-list-item-title>Edit</v-list-item-title>
                      </v-list-item>
                      <v-list-item
                        :id="`option-duplicate-evaluation-${evaluation.id}`"
                        base-color="secondary"
                        density="compact"
                        @click="() => duplicatingEvaluationId = evaluation.id"
                      >
                        <v-list-item-title>Duplicate</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </div>
                <div v-if="allowEdits && isEditing(evaluation)" class="pl-2 pt-2 select-evaluation-status">
                  <label for="select-evaluation-status">
                    Status
                  </label>
                  <select
                    id="select-evaluation-status"
                    v-model="selectedEvaluationStatus"
                    class="d-block mx-auto v-theme--light w-99"
                    :disabled="isSaving"
                    autocomplete="off"
                  >
                    <option
                      v-if="!selectedEvaluationStatus"
                      selected
                      :value="selectedEvaluationStatus"
                    >
                      Select...
                    </option>
                    <option
                      v-for="s in EVALUATION_STATUSES"
                      :key="s.text"
                      :selected="selectedEvaluationStatus === s.value"
                      :value="s.value"
                    >
                      {{ s.text }}
                    </option>
                  </select>
                </div>
              </td>
              <td
                :id="`evaluation-${rowIndex}-lastUpdated`"
                class="px-1"
                :class="{
                  'font-weight-bold pt-7': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                {{ toFormatFromJsDate(evaluation.lastUpdated, 'LL/dd/yyyy') }}
              </td>
              <td
                :id="`evaluation-${rowIndex}-courseNumber`"
                class="px-1 td-courseNumber"
                :class="{
                  'font-weight-bold pt-7': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                {{ evaluation.courseNumber }}
                <div v-if="evaluation.crossListedWith" class="xlisting-note">
                  (Cross-listed with {{ evaluation.crossListedWith.length > 1 ? 'sections' : 'section' }}
                  {{ evaluation.crossListedWith.join(', ') }})
                </div>
                <div v-if="evaluation.roomSharedWith" class="xlisting-note">
                  (Room shared with {{ evaluation.roomSharedWith.length > 1 ? 'sections' : 'section' }}
                  {{ evaluation.roomSharedWith.join(', ') }})
                </div>
              </td>
              <td
                class="px-1 td-courseName"
                :class="{
                  'font-weight-bold pt-7': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                <label :id="`evaluation-${rowIndex}-courseName`" :for="isEditing(evaluation) ? undefined : `evaluation-${rowIndex}-checkbox`">
                  {{ evaluation.subjectArea }}
                  {{ evaluation.catalogId }}
                  {{ evaluation.instructionFormat }}
                  {{ evaluation.sectionNumber }}
                </label>
                <div :id="`evaluation-${rowIndex}-courseTitle`">
                  {{ evaluation.courseTitle }}
                </div>
              </td>
              <td
                :id="`evaluation-${rowIndex}-instructor`"
                class="px-1 td-instructor"
                :class="{
                  'font-weight-bold pt-7': isEditing(evaluation) && evaluation.instructor,
                  'font-weight-bold pt-2': isEditing(evaluation) && !evaluation.instructor,
                  'align-middle': !isEditing(evaluation)
                }"
              >
                <div v-if="evaluation.instructor">
                  {{ evaluation.instructor.firstName }}
                  {{ evaluation.instructor.lastName }}
                  ({{ evaluation.instructor.uid }})
                </div>
                <div v-if="evaluation.instructor">
                  {{ evaluation.instructor.emailAddress }}
                </div>
                <EvaluationError
                  v-if="!evaluation.instructor && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                  :id="`error-msg-evaluation-instructor-${rowIndex}`"
                  :hover="isRowActive(evaluation)"
                  message="Instructor required"
                />
                <div v-if="!evaluation.instructor && isEditing(evaluation) && allowEdits" class="position-relative">
                  <PersonLookup
                    class="font-weight-regular instructor-lookup"
                    clearable
                    color="black"
                    :disabled="isSaving"
                    input-class="text-no-wrap overflow-hidden"
                    :instructor-lookup="true"
                    label="Instructor"
                    list-label="Suggested Instructors List"
                    :on-select-result="selectInstructor"
                  />
                  <div v-if="pendingInstructor" class="pt-1">
                    <div>
                      {{ pendingInstructor.firstName }} {{ pendingInstructor.lastName }} ({{ pendingInstructor.uid }})
                    </div>
                    <div>
                      {{ pendingInstructor.emailAddress }}
                    </div>
                  </div>
                </div>
              </td>
              <td
                :id="`evaluation-${rowIndex}-departmentForm`"
                class="px-1"
                :class="{
                  'pt-2': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                <div v-if="evaluation.departmentForm && !isEditing(evaluation)">
                  {{ evaluation.departmentForm.name }}
                  <EvaluationError
                    v-for="(conflict, index) in evaluation.conflicts.departmentForm"
                    :id="`error-msg-evaluation-department-form-conflict-${rowIndex}-${index}`"
                    :key="index"
                    :hover="isRowActive(evaluation)"
                    :message="`Conflicts with value ${conflict.value} from ${conflict.department} department`"
                  />
                </div>
                <EvaluationError
                  v-if="!evaluation.departmentForm && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                  :id="`error-msg-evaluation-department-form-${rowIndex}`"
                  :hover="isRowActive(evaluation)"
                  message="Department form required"
                />
                <EvaluationError
                  v-if="evaluation.departmentForm && evaluation.departmentForm.deletedAt"
                  :id="`error-msg-evaluation-department-form-${rowIndex}`"
                  :hover="isRowActive(evaluation)"
                  message="Department form has been deleted"
                />
                <div v-if="allowEdits && isEditing(evaluation)">
                  <label id="select-department-form-label" for="select-department-form">
                    Department Form
                  </label>
                  <select
                    id="select-department-form"
                    v-model="selectedDepartmentForm"
                    class="v-theme--light"
                    :disabled="isSaving"
                    autocomplete="off"
                  >
                    <option v-for="df in departmentForms" :key="df.id" :value="df.id">{{ df.name }}</option>
                  </select>
                </div>
              </td>
              <td
                :id="`evaluation-${rowIndex}-evaluationType`"
                class="px-1"
                :class="{
                  'pt-2': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                <div v-if="evaluation.evaluationType && !isEditing(evaluation)">
                  {{ evaluation.evaluationType.name }}
                  <EvaluationError
                    v-for="(conflict, index) in evaluation.conflicts.evaluationType"
                    :id="`error-msg-evaluation-type-conflict-${rowIndex}-${index}`"
                    :key="index"
                    :hover="isRowActive(evaluation)"
                    :message="`Conflicts with value ${conflict.value} from ${conflict.department} department`"
                  />
                </div>
                <EvaluationError
                  v-if="!evaluation.evaluationType && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                  :id="`error-msg-evaluation-type-${rowIndex}`"
                  :hover="isRowActive(evaluation)"
                  message="Evaluation type required"
                />
                <EvaluationError
                  v-if="evaluation.evaluationType && evaluation.evaluationType.deletedAt"
                  :id="`error-msg-evaluation-department-form-${rowIndex}`"
                  :hover="isRowActive(evaluation)"
                  message="Evaluation type has been deleted"
                />
                <div v-if="allowEdits && isEditing(evaluation)">
                  <label id="select-evaluation-type-label" for="select-evaluation-type">
                    Evaluation Type
                  </label>
                  <select
                    id="select-evaluation-type"
                    v-model="selectedEvaluationType"
                    class="v-theme--light"
                    :disabled="isSaving"
                    autocomplete="off"
                  >
                    <option
                      v-if="!selectedEvaluationType"
                      selected
                      :value="selectedEvaluationType"
                    >
                      Select...
                    </option>
                    <option
                      v-for="et in evaluationTypes"
                      :key="et.id"
                      :selected="selectedEvaluationType === et.id"
                      :value="et.id"
                    >
                      {{ et.name }}
                    </option>
                  </select>
                </div>
              </td>
              <td
                :id="`evaluation-${rowIndex}-period`"
                class="px-1"
                :class="{
                  'pt-2': isEditing(evaluation),
                  'align-middle': !isEditing(evaluation)
                }"
              >
                <div v-if="evaluation.startDate && !isEditing(evaluation)">
                  <div>
                    {{ toFormatFromJsDate(evaluation.startDate, 'LL/dd/yyyy') }} -
                    {{ toFormatFromJsDate(evaluation.endDate, 'LL/dd/yyyy') }}
                  </div>
                  <div>{{ evaluation.modular ? 2 : 3 }} weeks</div>
                  <EvaluationError
                    v-for="(conflict, index) in evaluation.conflicts.evaluationPeriod"
                    :id="`error-msg-evaluation-period-conflict-${index}`"
                    :key="index"
                    :hover="isRowActive(evaluation)"
                    :message="`Conflicts with period starting
                    ${toLocaleFromISO(conflict.value, 'LL/dd/yyyy')}
                    from ${conflict.department} department`"
                  />
                </div>
                <div v-if="allowEdits && isEditing(evaluation)" class="evaluation-period-edit">
                  <label for="evaluation-start-date-input">
                    Start date
                  </label>
                  <AccessibleDateInput
                    aria-label="Start Date"
                    :container-id="`evaluation-${rowIndex}-period`"
                    :disabled="isSaving"
                    :get-value="() => selectedStartDate"
                    id-prefix="evaluation-start-date"
                    :min-date="minStartDate(evaluation)"
                    :max-date="evaluation.maxStartDate"
                    :placement="rowIndex > 3 ? 'top' : 'bottom'"
                    :set-value="selectedDate => selectedStartDate = selectedDate"
                  />
                  <EvaluationError
                    v-if="!selectedStartDate"
                    id="error-msg-evaluation-start-date"
                    color="white"
                    message="Required"
                  />
                </div>
              </td>
            </tr>
            <tr v-if="isEditing(evaluation)" :key="`${evaluation.id}-edit`" class="bg-tertiary text-white border-top-none">
              <td />
              <td :colspan="size(evaluationHeaders) - 1" class="pb-1 px-3">
                <div class="d-flex justify-end">
                  <ConfirmDialog
                    confirm-button-label="Confirm anyway"
                    :hide-confirm="!currentUser.isAdmin"
                    :html="get(markAsDoneWarning, 'message')"
                    :icon="mdiAlertCircle"
                    :is-open="!!markAsDoneWarning"
                    :on-click-cancel="() => markAsDoneWarning = undefined"
                    :on-click-confirm="onOverrideMarkAsDoneWarning"
                    text=""
                    title="Warning"
                  />
                  <ProgressButton
                    id="save-evaluation-edit-btn"
                    :action="() => validateAndSave(evaluation)"
                    class="ma-2 evaluation-form-btn"
                    color="primary"
                    :disabled="!rowValid || isSaving"
                    :in-progress="isSaving"
                    :text="isSaving ? 'Saving...' : 'Save'"
                  />
                  <v-btn
                    id="cancel-evaluation-edit-btn"
                    class="evaluation-form-btn evaluation-form-btn-cancel ma-2"
                    :disabled="isSaving"
                    text="Cancel"
                    variant="flat"
                    @click="onCancelEdit(evaluation)"
                  />
                </div>
              </td>
            </tr>
          </template>
        </transition-group>
        <tr v-if="isEmpty(items)">
          <td :colspan="size(evaluationHeaders)">
            <div id="no-courses-found" class="font-size-16 pa-5 text-center text-muted">
              {{ searchFilter ? 'No courses match your filter.' : 'No courses' }}
            </div>
          </td>
        </tr>
      </template>
    </v-data-table>
    <ConfirmDialog
      :is-open="isConfirmingCancelEdit"
      :on-click-cancel="onCancelConfirm"
      :on-click-confirm="onConfirm"
      :text="'You have unsaved changes that will be lost.'"
      :title="'Cancel edit?'"
    />
    <ConfirmDialog
      :is-open="isConfirmingNonSisInstructor"
      :on-click-cancel="onCancelNonSisInstructor"
      :on-click-confirm="onConfirmNonSisInstructor"
      :text="instructorConfirmationText(pendingInstructor)"
      title="Add new instructor?"
    />
    <ModalDialog
      id-prefix="error"
      :is-open="errorDialog"
      persistent
      width="400"
    >
      <template #title><span class="px-2">Error</span></template>
      <template #text>{{ errorDialogText }}</template>
      <template #actions>
        <div class="align-center d-flex">
          <v-btn
            id="error-dialog-ok-btn"
            color="tertiary"
            text="OK"
            variant="flat"
            @click="departmentStore.dismissErrorDialog"
          />
        </div>
      </template>
    </ModalDialog>
  </v-container>
  <v-container v-if="!evaluations.length" class="no-eligible-sections mt-3">
    <v-row>
      <v-col align-self="center">
        <div class="d-flex flex-column text-muted">
          <span>No eligible sections to load.</span>
          <span v-if="!readonly && allowEdits">You may still add a section manually.</span>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="!readonly">
      <v-col align-self="center">
        <AddCourseSection
          id="add-course-section"
          :allow-edits="allowEdits"
          class="d-flex align-baseline justify-center ml-0"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {clone, each, filter, find, get, includes, isEmpty, keys, map, noop, pickBy, pull, size, some} from 'lodash'
import {computed, nextTick, onMounted, provide, ref, watch} from 'vue'
import {mdiAlertCircle, mdiCheckCircle, mdiChevronDown, mdiPlusCircle} from '@mdi/js'
import {storeToRefs} from 'pinia'
import AccessibleDateInput from '@/components/util/AccessibleDateInput'
import AddCourseSection from '@/components/evaluation/AddCourseSection'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import EvaluationActions from '@/components/evaluation/EvaluationActions'
import EvaluationError from '@/components/evaluation/EvaluationError'
import ModalDialog from '@/components/util/ModalDialog'
import PersonLookup from '@/components/admin/PersonLookup'
import ProgressButton from '@/components/util/ProgressButton.vue'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import {addInstructor} from '@/api/instructor'
import {alertScreenReader, oxfordJoin, pluralize, putFocusNextTick, toFormatFromJsDate, toLocaleFromISO} from '@/lib/utils'
import {EVALUATION_STATUSES, useDepartmentStore} from '@/stores/department/department-edit-session'
import {useContextStore} from '@/stores/context'
import {validateMarkAsDone} from '@/stores/department/utils'

const props = defineProps({
  readonly: {
    type: Boolean,
    required: false
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const departmentStore = useDepartmentStore()
const {disableControls, errorDialog, errorDialogText, evaluations, selectedEvaluationIds} = storeToRefs(departmentStore)
const departmentForms = ref([])
const duplicatingEvaluationId = ref(undefined)
const editRowId = ref(undefined)
const evaluationHeaders = ref([])
const evaluationTypes = ref([])
const filterTypes = {
  unmarked: {label: 'None', enabled: true, width: 112},
  review: {label: 'To-Do', enabled: true, width: 114},
  confirmed: {label: 'Done', enabled: true, width: 112},
  ignore: {label: 'Ignore', enabled: false, width: 122}
}
const focusedEditButtonEvaluationId = ref(undefined)
const hoverId = ref(undefined)
const isConfirmingCancelEdit = ref(false)
const isConfirmingNonSisInstructor = ref(false)
const isSaving = ref(false)
const markAsDoneWarning = ref(undefined)
const openMenuEvaluationIds = ref([])
const onOverrideMarkAsDoneWarning = ref(noop)
const pendingEditRowId = ref(undefined)
const pendingInstructor = ref(undefined)
const rules = {
  instructorUid: undefined
}
const searchFilter = ref('')
const searchFilterResults = ref([])
const selectedDepartmentForm = ref(undefined)
const selectedEvaluationStatus = ref(undefined)
const selectedEvaluationType = ref(undefined)
const selectedFilterTypes = ref(keys(pickBy(filterTypes, 'enabled')))
const selectedStartDate = ref(undefined)
const sortBy = ref([{key: 'sortableCourseName', order: 'asc'}])

const allEvaluationsSelected = computed(() => {
  const selectedCount = size(selectedEvaluationIds.value)
  return !!selectedCount && selectedCount === size(evaluations.value)
})
const allowEdits = computed(() => {
  return contextStore.currentUser.isAdmin || !contextStore.isSelectedTermLocked
})
const rowValid = computed(() => {
  const evaluation = find(evaluations.value, ['id', editRowId.value])
  return selectedStartDate.value >= minStartDate(evaluation) && selectedStartDate.value <= evaluation.maxStartDate
})
const someEvaluationsSelected = computed(() => {
  const selectedCount = size(selectedEvaluationIds.value)
  return !!selectedCount && selectedCount < size(evaluations.value)
})
const visibleEvaluations = computed(() => {
  return filter(evaluations.value, isStatusFilterEnabled)
})

provide('duplicatingEvaluationId', duplicatingEvaluationId)

watch(errorDialog, isOpen => {
  if (isOpen) {
    putFocusNextTick('error-dialog-ok-btn')
  }
})

watch(selectedFilterTypes, types => {
  alertScreenReader(`Showing ${types.length ? `evaluations marked ${oxfordJoin(types)}` : 'no evaluations'}`)
  each(keys(filterTypes), type => {
    filterTypes[type].enabled = types.includes(type)
  })
})

const stickySearchPosition = ref('0px')
const setStickySearchPosition = () => {
  stickySearchPosition.value = 64 + document.getElementById('service-announcement').clientHeight + 'px'
}

onMounted(() => {
  evaluationHeaders.value = [
    {key: 'status', class: 'text-no-wrap', headerProps: {justifyItems: 'center', minWidth: '5rem', width: '7%'}, sortable: true, title: 'Status', value: 'status'},
    {key: 'lastUpdated', class: 'text-no-wrap', headerProps: {minWidth: '5.63rem', width: '5%'}, sortable: true, title: 'Last Updated', value: 'lastUpdated'},
    {key: 'courseNumber', class: 'text-no-wrap', headerProps: {minWidth: '2.5rem', width: '5%'}, sortable: true, title: 'Course Number', value: 'sortableCourseNumber'},
    {key: 'courseName', headerProps: {minWidth: '6.25rem', width: '25%'}, sortable: true, title: 'Course Name', value: 'sortableCourseName'},
    {key: 'instructor', headerProps: {minWidth: '5rem', width: '20%'}, sortable: true, title: 'Instructor', value: 'sortableInstructor'},
    {key: 'departmentForm', class: 'text-start', headerProps: {minWidth: '6.25rem', width: '10%'}, sortable: true, title: 'Department Form', value: 'departmentForm.name'},
    {key: 'evaluationType', class: 'text-start', headerProps: {minWidth: '6.25rem', width: '10%'}, sortable: true, title: 'Evaluation Type', value: 'evaluationType.name'},
    {key: 'startDate', class: 'text-no-wrap', headerProps: {minWidth: '6.88', width: '15%'}, sortable: true, title: 'Evaluation Period', value: 'startDate'}
  ]
  if (props.readonly) {
    evaluationHeaders.value.unshift({key: 'departmentId', class: 'pl-1 text-no-wrap', headerProps: {width: '15%'}, sortable: true, title: 'Department', value: 'department.id'})
  } else if (allowEdits.value) {
    evaluationHeaders.value.unshift(
      {key: 'select', ariaLabel: 'Selected', class: 'pl-1 text-no-wrap', headerProps: {justifyItems: 'center', width: '3%'}, sortable: true, title: 'Select', value: 'isSelected'}
    )
  }
  departmentForms.value = [{id: null, name: 'Revert'}].concat(departmentStore.activeDepartmentForms)
  evaluationTypes.value = [{id: null, name: 'Revert'}].concat(contextStore.config.evaluationTypes)

  rules.instructorUid = () => {
    return get(pendingInstructor.value, 'uid') ? true : 'Instructor is required.'
  }

  setStickySearchPosition()
})

const afterEditEvaluation = evaluation => {
  if (pendingInstructor.value && pendingInstructor.value.isSisInstructor === false) {
    addInstructor(pendingInstructor.value)
  }
  editRowId.value = null
  pendingEditRowId.value = null
  pendingInstructor.value = null
  isSaving.value = false
  selectedDepartmentForm.value = null
  selectedEvaluationStatus.value = null
  selectedEvaluationType.value = null
  selectedStartDate.value = null
  focusedEditButtonEvaluationId.value = evaluation.id
  departmentStore.setDisableControls(false)
  putFocusNextTick(`evaluation-menu-btn-${focusedEditButtonEvaluationId.value}`, {scroll: false})
}

const customFilter = (value, search, item) => {
  const itemObject = item.raw
  if (!search) {
    return true
  }
  if (!value || typeof value === 'boolean') {
    return false
  }
  if (value === itemObject.sortableInstructor) {
    value = itemObject.searchableInstructor
  }
  if (value === itemObject.lastUpdated) {
    value = toFormatFromJsDate(itemObject.lastUpdated, 'LL/dd/yyyy')
  }
  if (value === itemObject.sortableCourseName) {
    value = itemObject.searchableCourseName
  }
  if (value === itemObject.sortableCourseNumber) {
    value = itemObject.courseNumber
    if (itemObject.crossListedWith) {
      value += (' ' + itemObject.crossListedWith.join(', '))
    }
    if (itemObject.roomSharedWith) {
      value += (' ' + itemObject.roomSharedWith.join(', '))
    }
  }
  if (value === itemObject.startDate) {
    value = [
      toFormatFromJsDate(itemObject.startDate, 'LL/dd/yyyy'),
      '-',
      toFormatFromJsDate(itemObject.endDate, 'LL/dd/yyyy'),
      (itemObject.modular ? '2' : '3'),
      'weeks'
    ].join(' ')
  }
  if (itemObject.department?.name) {
    value += ' ' + itemObject.department.name
  }
  return value.toString().toLocaleLowerCase().indexOf(search.toLocaleLowerCase()) !== -1
}

const describeRow = e => {
  const courseName = `${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber}`
  const instructor = `instructor ${get(e, 'instructor.firstName', 'blank')} ${get(e, 'instructor.lastName', '')}`
  const departmentForm = `department form ${get(e, 'departmentForm.name') || get(e, 'defaultDepartmentForm.name', 'blank')}`
  const evaluationType = `evaluation type ${get(e, 'evaluationType.name', 'blank')}`
  return `${e.status || ''} evaluation for section ${e.courseNumber}, ${courseName}, ${instructor}, ${departmentForm}, ${evaluationType}`
}

const displayStatus = evaluation => {
  if (evaluation.status === 'review') {
    return 'To-Do'
  } else if (evaluation.status === 'confirmed') {
    return 'Done'
  } else {
    return evaluation.status
  }
}

const filterTypeCounts = type => {
  if (type === 'unmarked') {
    return filter(evaluations.value, e => e.status === null).length
  }
  return filter(evaluations.value, e => e.status === type).length
}

const instructorConfirmationText = instructor => {
  if (instructor) {
    return `
      ${instructor.firstName} ${instructor.lastName} (${instructor.uid})
      is not currently listed in SIS data as an instructor for any courses.`
  }
  return ''
}

const isEditing = evaluation => {
  return editRowId.value === evaluation.id
}

const isRowActive = evaluation => {
  return [focusedEditButtonEvaluationId.value, hoverId.value, ...openMenuEvaluationIds.value].includes(evaluation.id)
}

const isRowSelected = evaluation => {
  return selectedEvaluationIds.value.includes(evaluation.id)
}

const isStatusFilterEnabled = evaluation => {
  const status = evaluation.status || 'unmarked'
  return includes(selectedFilterTypes.value, status)
}

const isStatusVisible = evaluation => {
  return evaluation.status && !isEditing(evaluation) && !isRowActive(evaluation)
}

const minStartDate = evaluation => {
  return new Date(get(evaluation, 'meetingDates.start'))
}

const onCancelConfirm = () => {
  isConfirmingCancelEdit.value = false
  focusedEditButtonEvaluationId.value = clone(pendingEditRowId.value)
  pendingEditRowId.value = null
  putFocusNextTick(`evaluation-menu-btn-${focusedEditButtonEvaluationId.value}`, {scroll: false})
}

const onCancelEdit = evaluation => {
  alertScreenReader('Edit canceled.')
  afterEditEvaluation(evaluation)
}

const onCancelNonSisInstructor = () => {
  isConfirmingNonSisInstructor.value = false
  pendingInstructor.value = null
}

const onChangeSearchFilter = filterResults => {
  if (!contextStore.loading) {
    searchFilterResults.value = map(filterResults, r => r.raw)
    if (size(selectedEvaluationIds.value)) {
      departmentStore.filterSelectedEvaluations(searchFilterResults.value, selectedFilterTypes.value)
    }
    if (!some(searchFilterResults.value, {'id': editRowId.value})) {
      editRowId.value = null
    }
  }
}

const onConfirm = () => {
  const evaluation = find(evaluations.value, ['id', pendingEditRowId.value])
  isConfirmingCancelEdit.value = false
  editRowId.value = null
  onEditEvaluation(evaluation)
}

const onConfirmNonSisInstructor = () => {
  isConfirmingNonSisInstructor.value = false
}

const onEditEvaluation = evaluation => {
  departmentStore.setDisableControls(true)
  pull(openMenuEvaluationIds.value, evaluation.id)
  if (editRowId.value) {
    const editingEvaluation = find(evaluations.value, ['id', editRowId.value])
    isConfirmingCancelEdit.value = editingEvaluation && (
      get(pendingInstructor.value, 'uid') !== get(editingEvaluation, 'instructor.uid')
      || selectedDepartmentForm.value !== get(editingEvaluation, 'departmentForm.id')
      || selectedEvaluationStatus.value !== get(editingEvaluation, 'status')
      || selectedEvaluationType.value !== get(editingEvaluation, 'evaluationType.id')
      || selectedStartDate.value !== editingEvaluation.startDate
    )
  }
  if (isConfirmingCancelEdit.value) {
    pendingEditRowId.value = evaluation.id
  } else {
    editRowId.value = evaluation.id
    pendingInstructor.value = evaluation.instructor
    selectedDepartmentForm.value = get(evaluation, 'departmentForm.id')
    selectedEvaluationStatus.value = get(evaluation, 'status')
    selectedEvaluationType.value = get(evaluation, 'evaluationType.id')
    selectedStartDate.value = evaluation.startDate
    putFocusNextTick(`${props.readonly ? '' : 'select-evaluation-status'}`, {scroll: false})
  }
}

const onMouseenterRow = evaluation => {
  nextTick(() => {
    hoverId.value = evaluation.id
  })
}

const onMouseleaveRow = evaluation => {
  if (!openMenuEvaluationIds.value.includes(evaluation.id)) {
    hoverId.value = null
  }
}

const onToggleEditMenu = (isOpen, evaluation) => {
  if (isOpen) {
    openMenuEvaluationIds.value.push(evaluation.id)
    focusedEditButtonEvaluationId.value = evaluation.id
  } else {
    pull(openMenuEvaluationIds.value, evaluation.id)
  }
}

const onUpdateSortBy = primarySortBy => {
  if (size(primarySortBy)) {
    const key = primarySortBy[0].key
    const header = find(evaluationHeaders.value, {key: key})
    const order = primarySortBy[0].order
    sortBy.value = primarySortBy
    if (header) {
      alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${order}ending`)
    }
  } else {
    alertScreenReader('Default sort order restored.')
  }
}

const rowId = (evaluation, rowIndex) => {
  const deptId = get(evaluation, 'department.id', get(departmentStore, 'department.id', 'None'))
  const instructorUid = get(evaluation, 'instructor.uid', 'None')
  const deptForm = get(evaluation, 'departmentForm.name', get(evaluation, 'defaultDepartmentForm.name', 'None'))
  const evalType = get(evaluation, 'evaluationType.name', 'None')
  return `evaluation-${deptId}-${evaluation.courseNumber}-${instructorUid}-${deptForm}-${evalType}-${rowIndex}`
}

const selectInstructor = instructor => {
  if (instructor) {
    instructor.emailAddress = instructor.email
    if (!instructor.isSisInstructor) {
      isConfirmingNonSisInstructor.value = true
    }
  }
  pendingInstructor.value = instructor
}

const toggleSelectAll = () => {
  if (allEvaluationsSelected.value || someEvaluationsSelected.value) {
    departmentStore.deselectAllEvaluations()
    alertScreenReader('All evaluations unselected')
  } else {
    departmentStore.selectAllEvaluations(searchFilterResults.value, selectedFilterTypes.value)
    alertScreenReader('All evaluations selected')
  }
}

const updateEvaluation = (evaluation, fields) => {
  isSaving.value = true
  alertScreenReader('Saving evaluation row.')
  return new Promise(resolve => {
    const showError = fields.status === 'confirmed' && (!fields.departmentFormId || !fields.evaluationTypeId || !fields.instructorUid)
    if (showError) {
      departmentStore.showErrorDialog('Cannot confirm an evaluation with missing fields.')
      isSaving.value = false
      resolve()
    } else {
      departmentStore.editEvaluation(
        evaluation.id,
        evaluation.courseNumber,
        contextStore.selectedTermId,
        fields
      ).then(response => {
        const conflicts = get(response, '0.conflicts')
        if (conflicts) {
          alertScreenReader(`Changes saved. Conflicting data on field ${Object.keys(conflicts).join(' and ')}`)
        } else {
          alertScreenReader('Changes saved.')
        }
        isSaving.value = false
        afterEditEvaluation(evaluation)
        departmentStore.deselectAllEvaluations()
        resolve()
      }).catch(error => {
        departmentStore.showErrorDialog(get(error, 'response.data.message', 'An unknown error occurred.'))
        isSaving.value = false
        resolve()
      })
    }
  })
}

const validateAndSave = evaluation => {
  markAsDoneWarning.value = null
  const departmentFormId = selectedDepartmentForm.value || get(evaluation, 'defaultDepartmentForm.id') || null
  const status = selectedEvaluationStatus.value === 'none' ? null : selectedEvaluationStatus.value
  const startDate = selectedStartDate.value ? toFormatFromJsDate(selectedStartDate.value, 'y-LL-dd') : null
  const fields = {
    departmentFormId,
    evaluationTypeId: selectedEvaluationType.value,
    instructorUid: get(pendingInstructor.value, 'uid'),
    startDate,
    status
  }
  let warning
  if (status === 'confirmed') {
    // If evaluation end date is in the past then put up a warning dialog.
    const proposedUpdate = {...evaluation, ...fields}
    warning = validateMarkAsDone([proposedUpdate])
  }
  if (warning) {
    markAsDoneWarning.value = {evaluation, fields, message: warning}
    if (currentUser.isAdmin) {
      onOverrideMarkAsDoneWarning.value = () => {
        updateEvaluation(evaluation, fields)
        markAsDoneWarning.value = null
      }
    }
  } else {
    updateEvaluation(evaluation, fields)
  }
}
</script>

<style>
.course-name {
  min-width: 200px;
}
.evaluation-input .v-messages__message {
  color: #fff !important;
}
.evaluation-row-btn .v-btn__append {
  margin-left: 2px !important;
}
.focus-btn::before {
  opacity: 0.24;
}
tr.border-bottom-none td {
  border-bottom: none !important;
}
tr.border-top-none td {
  border-top: none !important;
}
</style>

<style scoped>
.align-middle {
  vertical-align: middle;
}
.evaluation-actions {
  position: relative;
  top: 2px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.bg-evaluation-active a {
  color: rgb(var(--v-theme-anchor-darken-2));
}
.evaluation-form-btn {
  width: 150px;
}
.evaluation-form-btn-cancel {
  color: rgba(var(--v-theme-on-surface),var(--v-high-emphasis-opacity)) !important;
}
.evaluation-row {
  vertical-align: top;
}
.evaluation-row.evaluation-row-enter-to,
.evaluation-row.evaluation-row-leave-from {
  animation: 4s highlightRow;
  animation-delay: 250ms;
  animation-timing-function: cubic-bezier(.05, -.12, .02, .32);
}
.evaluation-row.evaluation-row-enter-from,
.evaluation-row.evaluation-row-leave-to {
  opacity: 0;
  transform: translateX(20%);
}
@media (prefers-reduced-motion) {
  .evaluation-row.evaluation-row-enter-from,
  .evaluation-row.evaluation-row-leave-to {
    transform: none;
  }
}
.evaluation-row.evaluation-row-move,
.evaluation-row.evaluation-row-enter-active,
.evaluation-row.evaluation-row-leave-active {
  transition: opacity 0.5s ease,
    position 0.5s ease,
    transform 0.5s ease;
}
.evaluation-row.evaluation-row-leave-active {
  position: absolute;
}
.instructor-lookup {
  max-width: 300px !important;
  min-width: 5rem !important;
}
.no-eligible-sections {
  font-size: 20px;
  height: fit-content;
}
.pill {
  border: 1px solid #999;
  border-radius: 5px;
  color: #fff;
  font-size: 0.8em;
  font-weight: bold;
  margin: 0;
  padding: 3px 10px;
  text-align: center;
  text-transform: uppercase;
  width: 90px;
}
.pill-invisible {
  border: none;
  padding: 0;
}
.select-all-evals {
  height: 36px;
  margin-left: -3px;
  width: 6.5rem;
}
.select-evaluation-status {
  min-width: 5.5rem;
}
.status-filter {
  height: fit-content !important;
}
.status-label {
  border-radius: 4px;
  display: flex;
  font-weight: 700;
  justify-content: center;
  max-width: 150px;
  min-width: 54px;
  text-transform: uppercase !important;
  width: 100%;
}
.sticky {
  position: sticky;
  top: v-bind(stickySearchPosition);
  z-index: 11;
}
.td-courseNumber {
  word-break: break-word;
}
.td-courseName {
  word-break: break-word;
}
.td-instructor {
  word-break: break-word;
}
.w-99 {
  width: 99%;
}
.xlisting-note {
  font-size: 0.8em;
}
</style>

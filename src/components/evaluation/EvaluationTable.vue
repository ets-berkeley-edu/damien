<template>
  <div v-if="evaluations.length > 0">
    <div
      class="elevation-2 sticky"
      :class="$vuetify.theme.dark ? 'sticky-dark' : 'sticky-light'"
      role="search"
    >
      <div class="align-baseline d-flex flex-wrap px-5 pb-3 pt-1 w-75">
        <v-text-field
          id="evaluation-search-input"
          v-model="searchFilter"
          append-icon="mdi-magnify"
          aria-label="Filter evaluations table by search terms."
          class="evaluation-search-input mr-3"
          color="tertiary"
          hide-details
          label="Find"
          max-width="600px"
          single-line
          type="search"
        />
        <div class="text-left">
          <AddCourseSection
            v-if="!readonly"
            id="add-course-section"
            :evaluations="evaluations"
            :allow-edits="allowEdits"
          />
        </div>
      </div>
      <div class="align-center d-flex flex-wrap justify-space-between px-5 py-3">
        <div v-if="!readonly && allowEdits">
          <div class="d-flex">
            <div>
              <v-checkbox
                id="select-all-evals-checkbox"
                class="select-all-evals align-center mt-0 pt-0"
                color="tertiary"
                :disabled="$_.isEmpty(searchFilterResults)"
                :false-value="!someEvaluationsSelected && !allEvaluationsSelected"
                hide-details
                :indeterminate="someEvaluationsSelected"
                :input-value="someEvaluationsSelected || allEvaluationsSelected"
                :ripple="false"
                :value="allEvaluationsSelected"
                @change="toggleSelectAll"
              >
                <template #label>
                  <span
                    v-if="!(someEvaluationsSelected || allEvaluationsSelected)"
                    class="text-nowrap pl-1 py-2"
                    :class="{'sr-only': someEvaluationsSelected || allEvaluationsSelected}"
                  >
                    {{ someEvaluationsSelected || allEvaluationsSelected ? 'Unselect' : 'Select' }} all
                  </span>
                </template>
              </v-checkbox>
            </div>
            <EvaluationActions v-if="!readonly" />
          </div>
        </div>
        <div class="align-center d-flex flex-wrap">
          <div class="mr-2">Show statuses:</div>
          <v-btn-toggle
            v-model="selectedFilterTypes"
            aria-controls="evaluation-table"
            borderless
            dense
            multiple
            rounded
          >
            <v-btn
              v-for="status in $_.keys(filterTypes)"
              :id="`evaluations-filter-${status}`"
              :key="status"
              :aria-selected="filterTypes[status].enabled"
              class="mr-1 pl-3 rounded-pill"
              :class="{
                'secondary': filterTypes[status].enabled,
                'inactive': !filterTypes[status].enabled
              }"
              small
              text
              :value="status"
            >
              <div class="align-center d-flex justify-space-between">
                <div>
                  <v-icon
                    v-if="filterTypes[status].enabled"
                    :color="filterTypes[status].enabled ? 'green' : 'inactive-contrast'"
                    left
                    small
                  >
                    {{ filterTypes[status].enabled ? 'mdi-check-circle' : 'mdi-plus-circle' }}
                  </v-icon>
                </div>
                <div :class="filterTypes[status].enabled ? 'white--text' : 'grey--text darken-2'">
                  <span class="sr-only">{{ filterTypes[status].enabled ? 'Hide' : 'Show' }} evaluations of marked with</span>
                  {{ filterTypes[status].label }}
                </div>
                <div :class="filterTypes[status].enabled ? 'white--text' : 'grey--text darken-2'">
                  <v-chip
                    class="ml-2 px-1"
                    :class="{'font-weight-bold': filterTypes[status].enabled}"
                    x-small
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
      <span v-if="searchFilter">{{ pluralize('evaluation', $_.size(searchFilterResults)) }} displayed.</span>
    </div>
    <v-data-table
      id="evaluation-table"
      aria-label="Evaluations"
      class="mt-3"
      disable-pagination
      :headers="evaluationHeaders"
      :search="searchFilter"
      :custom-filter="customFilter"
      hide-default-footer
      hide-default-header
      :items="evaluations"
      :loading="loading"
      :sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      @current-items="onChangeSearchFilter"
      @update:sort-by="onSort"
      @update:sort-desc="onSort"
    >
      <template #header="{props: {headers}}">
        <SortableTableHeader :headers="headers" :on-sort="sort" />
      </template>
      <template #body="{items}">
        <TransitionGroup
          class="position-relative"
          name="evaluation-row"
          tag="tbody"
        >
          <template v-for="(evaluation, rowIndex) in items">
            <v-hover v-if="statusFilterEnabled(evaluation)" v-slot="{ hover }" :key="evaluation.id">
              <tr
                class="evaluation-row"
                :class="evaluationClass(evaluation, hover)"
              >
                <td v-if="readonly" :id="`evaluation-${rowIndex}-department`" class="align-middle py-1">
                  <router-link :to="`/department/${$_.get(evaluation.department, 'id')}`">
                    {{ $_.get(evaluation.department, 'name') }}
                  </router-link>
                </td>
                <td v-if="!readonly && allowEdits && !(allowEdits && isEditing(evaluation))" class="align-middle text-center pr-1">
                  <v-checkbox
                    v-if="!isEditing(evaluation)"
                    :id="`evaluation-${rowIndex}-checkbox`"
                    :aria-label="`${evaluation.subjectArea} ${evaluation.catalogId} ${selectedEvaluationIds.includes(evaluation.id) ? '' : 'not '}selected`"
                    class="pr-1"
                    :color="`${hover ? 'primary' : 'tertiary'}`"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
                    :value="selectedEvaluationIds.includes(evaluation.id)"
                    @change="toggleSelectEvaluation(evaluation)"
                  />
                </td>
                <td
                  :id="`evaluation-${rowIndex}-status`"
                  :class="{'align-middle position-relative': !isEditing(evaluation)}"
                  class="px-1"
                  :colspan="allowEdits && isEditing(evaluation) ? 2 : 1"
                >
                  <div
                    v-if="isStatusVisible(evaluation)"
                    class="pill mx-auto"
                    :class="evaluationPillClass(evaluation, hover)"
                  >
                    {{ displayStatus(evaluation) }}
                  </div>
                  <div
                    v-if="allowEdits && !isEditing(evaluation) && (!readonly || !evaluation.status)"
                    class="pill pill-invisible mx-auto"
                  >
                    <v-btn
                      :id="`edit-evaluation-${evaluation.id}-btn`"
                      class="primary-contrast primary--text"
                      :class="{'sr-only': !hover && evaluation.id !== focusedEditButtonEvaluationId, 'focus-btn': evaluation.id === focusedEditButtonEvaluationId}"
                      block
                      :disabled="!allowEdits"
                      :ripple="false"
                      text
                      @click.stop="onEditEvaluation(evaluation)"
                      @blur.native="() => focusedEditButtonEvaluationId = null"
                      @focus.native="() => focusedEditButtonEvaluationId = evaluation.id"
                    >
                      Edit
                    </v-btn>
                  </div>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pl-2 py-2 select-evaluation-status">
                    <label for="select-evaluation-status">
                      Status:
                    </label>
                    <select
                      id="select-evaluation-status"
                      v-model="selectedEvaluationStatus"
                      class="d-block light mx-auto native-select-override"
                      :disabled="saving"
                    >
                      <option
                        v-if="!selectedEvaluationStatus"
                        selected
                        :value="selectedEvaluationStatus"
                      >
                        Select...
                      </option>
                      <option
                        v-for="s in evaluationStatuses"
                        :key="s.text"
                        :selected="selectedEvaluationStatus === s.value"
                        :value="s.value"
                      >
                        {{ s.text }}
                      </option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-lastUpdated`" class="evaluation-last-updated px-1" :class="{'pt-5': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
                  {{ $moment(evaluation.lastUpdated) | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${rowIndex}-courseNumber`" class="evaluation-course-number px-1" :class="{'pt-5': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
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
                <td class="evaluation-course-name px-1" :class="{'pt-3': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
                  <label :id="`evaluation-${rowIndex}-courseName`" :for="`evaluation-${rowIndex}-checkbox`">
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
                  :class="{'pt-5': isEditing(evaluation) && evaluation.instructor, 'align-middle': !isEditing(evaluation)}"
                  class="evaluation-instructor px-1"
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
                    id="error-msg-evaluation-instructor"
                    :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                    message="Instructor required"
                  />
                  <div v-if="!evaluation.instructor && isEditing(evaluation) && allowEdits">
                    <div class="mt-1 py-2">
                      <PersonLookup
                        id="input-instructor-lookup-autocomplete"
                        class="instructor-lookup"
                        :disabled="saving"
                        :instructor-lookup="true"
                        label="Instructor: "
                        :on-select-result="selectInstructor"
                      />
                    </div>
                    <div v-if="pendingInstructor">
                      {{ pendingInstructor.firstName }}
                      {{ pendingInstructor.lastName }}
                      ({{ pendingInstructor.uid }})
                    </div>
                    <div v-if="pendingInstructor">
                      {{ pendingInstructor.emailAddress }}
                    </div>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-departmentForm`" class="evaluation-department-form px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <div v-if="evaluation.departmentForm && !isEditing(evaluation)">
                    {{ evaluation.departmentForm.name }}
                    <EvaluationError
                      v-for="(conflict, index) in evaluation.conflicts.departmentForm"
                      :id="`error-msg-evaluation-department-form-conflict-${index}`"
                      :key="index"
                      :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                      :message="`Conflicts with value ${conflict.value} from ${conflict.department} department`"
                    />
                  </div>
                  <EvaluationError
                    v-if="!evaluation.departmentForm && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    id="error-msg-evaluation-department-form"
                    :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                    message="Department form required"
                  />
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 py-2">
                    <label id="select-department-form-label" for="select-department-form">
                      Department Form:
                    </label>
                    <select
                      id="select-department-form"
                      v-model="selectedDepartmentForm"
                      class="native-select-override light"
                      :disabled="saving"
                    >
                      <option v-for="df in departmentForms" :key="df.id" :value="df.id">{{ df.name }}</option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-evaluationType`" class="evaluation-type px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <div v-if="evaluation.evaluationType && !isEditing(evaluation)">
                    {{ evaluation.evaluationType.name }}
                    <EvaluationError
                      v-for="(conflict, index) in evaluation.conflicts.evaluationType"
                      :id="`error-msg-evaluation-type-conflict-${index}`"
                      :key="index"
                      :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                      :message="`Conflicts with value ${conflict.value} from ${conflict.department} department`"
                    />
                  </div>
                  <EvaluationError
                    v-if="!evaluation.evaluationType && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    id="error-msg-evaluation-type"
                    :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                    message="Evaluation type required"
                  />
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 py-2">
                    <label id="select-evaluation-type-label" for="select-evaluation-type">
                      Evaluation Type:
                    </label>
                    <select
                      id="select-evaluation-type"
                      v-model="selectedEvaluationType"
                      class="native-select-override light"
                      :disabled="saving"
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
                <td :id="`evaluation-${rowIndex}-period`" class="evaluation-period px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <span v-if="evaluation.startDate && !isEditing(evaluation)">
                    <div>{{ evaluation.startDate | moment('MM/DD/YY') }} - {{ evaluation.endDate | moment('MM/DD/YY') }}</div>
                    <div>{{ evaluation.modular ? 2 : 3 }} weeks</div>
                    <EvaluationError
                      v-for="(conflict, index) in evaluation.conflicts.evaluationPeriod"
                      :id="`error-msg-evaluation-period-conflict-${index}`"
                      :key="index"
                      :hover="hover || focusedEditButtonEvaluationId === evaluation.id"
                      :message="`Conflicts with period starting
                      ${$moment(conflict.value).format('MM/DD/YY')}
                      from ${conflict.department} department`"
                    />
                  </span>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 py-2">
                    <div class="d-flex align-center">
                      <label id="input-evaluation-start-date-label" for="input-evaluation-start-date">
                        Start date:
                      </label>
                    </div>
                    <c-date-picker
                      v-model="selectedStartDate"
                      :min-date="minStartDate(evaluation)"
                      :max-date="evaluation.maxStartDate"
                      :popover="{positionFixed: true}"
                      title-position="left"
                    >
                      <template #default="{ inputValue, inputEvents }">
                        <input
                          id="input-evaluation-start-date"
                          class="datepicker-input input-override light mt-0"
                          :class="{'disabled': saving}"
                          :disabled="saving"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                        <EvaluationError
                          v-if="!selectedStartDate"
                          id="error-msg-evaluation-start-date"
                          color="white"
                          message="Required"
                        />
                      </template>
                    </c-date-picker>
                  </div>
                </td>
              </tr>
            </v-hover>
            <tr v-if="isEditing(evaluation)" :key="`${evaluation.id}-edit`" class="secondary white--text border-top-none">
              <td></td>
              <td colspan="8" class="pb-2 px-2">
                <div class="d-flex justify-end">
                  <ConfirmDialog
                    v-if="markAsDoneWarning"
                    confirm-button-label="Proceed"
                    :disabled="disableControls"
                    :on-click-cancel="() => markAsDoneWarning = undefined"
                    :on-click-confirm="onProceedMarkAsDone"
                    :text="markAsDoneWarning.message"
                    icon="mdi-alert-circle"
                    title="Warning"
                  />
                  <v-btn
                    id="save-evaluation-edit-btn"
                    class="ma-2 evaluation-form-btn"
                    color="primary"
                    width="150px"
                    :disabled="disableControls || !rowValid || saving"
                    @click.prevent="validateAndSave(evaluation)"
                    @keypress.enter.prevent="validateAndSave(evaluation)"
                  >
                    <span v-if="!saving">Save</span>
                    <v-progress-circular
                      v-if="saving"
                      :indeterminate="true"
                      color="white"
                      rotate="5"
                      size="20"
                      width="3"
                    ></v-progress-circular>
                  </v-btn>
                  <v-btn
                    id="cancel-evaluation-edit-btn"
                    class="ma-2 evaluation-form-btn"
                    :disabled="saving"
                    width="150px"
                    @click="onCancelEdit(evaluation)"
                    @keypress.enter.prevent="onCancelEdit(evaluation)"
                  >
                    Cancel
                  </v-btn>
                </div>
              </td>
            </tr>
          </template>
        </TransitionGroup>
      </template>
    </v-data-table>
    <ConfirmDialog
      v-if="isConfirmingCancelEdit"
      :disabled="disableControls"
      :on-click-cancel="onCancelConfirm"
      :on-click-confirm="onConfirm"
      :text="'You have unsaved changes that will be lost.'"
      :title="'Cancel edit?'"
    />
    <ConfirmDialog
      v-if="isConfirmingNonSisInstructor"
      :disabled="disableControls"
      :on-click-cancel="onCancelNonSisInstructor"
      :on-click-confirm="onConfirmNonSisInstructor"
      :text="instructorConfirmationText(pendingInstructor)"
      title="Add new instructor?"
    />
    <v-dialog
      id="error-dialog"
      v-model="errorDialog"
      width="400"
      role="alertdialog"
      aria-labelledby="error-dialog-title"
      aria-describedby="error-dialog-text"
    >
      <v-card>
        <v-card-title id="error-dialog-title" tabindex="-1">Error</v-card-title>
        <v-card-text id="error-dialog-text" class="pt-3">{{ errorDialogText }}</v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <div class="d-flex pa-2">
            <div class="mr-2">
              <v-btn
                id="error-dialog-ok-btn"
                color="primary"
                @click="dismissErrorDialog"
                @keypress.enter.prevent="dismissErrorDialog"
              >
                OK
              </v-btn>
            </div>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
  <v-container v-else class="no-eligible-sections py-8">
    <v-row>
      <v-col align="center">
        <div class="d-flex flex-column muted--text">
          <span>No eligible sections to load.</span>
          <span v-if="!readonly && allowEdits">You may still add a section manually.</span>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="!readonly">
      <v-col align="center">
        <AddCourseSection
          id="add-course-section"
          :evaluations="evaluations"
          :allow-edits="allowEdits"
          class="d-flex align-baseline justify-center ml-0"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import {addInstructor} from '@/api/instructor'
import AddCourseSection from '@/components/evaluation/AddCourseSection'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationActions from '@/components/evaluation/EvaluationActions'
import EvaluationError from '@/components/evaluation/EvaluationError'
import PersonLookup from '@/components/admin/PersonLookup'
import SortableTableHeader from '@/components/util/SortableTableHeader'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationTable',
  mixins: [Context, DepartmentEditSession, Util],
  components: {
    AddCourseSection,
    ConfirmDialog,
    EvaluationActions,
    EvaluationError,
    PersonLookup,
    SortableTableHeader
  },
  props: {
    readonly: {
      type: Boolean,
      required: false
    }
  },
  data: () => ({
    departmentForms: [],
    editRowId: null,
    evaluationTypes: [],
    filterTypes: {
      unmarked: {label: 'None', enabled: true},
      review: {label: 'To-Do', enabled: true},
      confirmed: {label: 'Done', enabled: true},
      ignore: {label: 'Ignore', enabled: false}
    },
    focusedEditButtonEvaluationId: null,
    evaluationHeaders: [
      {class: 'text-center text-nowrap', text: 'Status', value: 'status', width: '115px'},
      {class: 'text-start text-nowrap', text: 'Last Updated', value: 'lastUpdated', width: '5%'},
      {class: 'text-start text-nowrap', text: 'Course Number', value: 'sortableCourseNumber', width: '5%'},
      {class: 'text-start course-name', text: 'Course Name', value: 'sortableCourseName', width: '20%'},
      {class: 'text-start text-nowrap', text: 'Instructor', value: 'sortableInstructor', width: '20%'},
      {class: 'text-start', text: 'Department Form', value: 'departmentForm.name', width: '20%'},
      {class: 'text-start', text: 'Evaluation Type', value: 'evaluationType.name', width: '20%'},
      {class: 'text-start text-nowrap', text: 'Evaluation Period', value: 'startDate', width: '10%'}
    ],
    isConfirmingCancelEdit: false,
    isConfirmingNonSisInstructor: false,
    markAsDoneWarning: undefined,
    pendingEditRowId: null,
    pendingInstructor: null,
    rules: {
      instructorUid: null
    },
    saving: false,
    searchFilter: '',
    searchFilterResults: [],
    selectedDepartmentForm: null,
    selectedEvaluationStatus: null,
    selectedEvaluationType: null,
    selectedStartDate: null,
    sortBy: null,
    sortDesc: false
  }),
  computed: {
    allEvaluationsSelected() {
      return !!(this.$_.size(this.selectedEvaluationIds) && this.$_.size(this.selectedEvaluationIds) === this.$_.size(this.evaluations))
    },
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
    rowValid() {
      const evaluation = this.$_.find(this.evaluations, ['id', this.editRowId])
      return this.selectedStartDate >= this.minStartDate(evaluation) && this.selectedStartDate <= evaluation.maxStartDate
    },
    selectedFilterTypes: {
      get: function() {
        return this.$_.keys(this.$_.pickBy(this.filterTypes, 'enabled'))
      },
      set: function(types) {
        this.alertScreenReader(`Showing ${types.length ? `evaluations marked ${this.oxfordJoin(types)}` : 'no evaluations'}`)
        this.$_.each(this.$_.keys(this.filterTypes), type => {
          this.filterTypes[type].enabled = types.includes(type)
        })
      }
    },
    someEvaluationsSelected() {
      return !!(this.$_.size(this.selectedEvaluationIds) && this.$_.size(this.selectedEvaluationIds) < this.$_.size(this.evaluations))
    }
  },
  methods: {
    afterEditEvaluation(evaluation) {
      if (this.pendingInstructor && this.pendingInstructor.isSisInstructor === false) {
        addInstructor(this.pendingInstructor)
      }
      this.editRowId = null
      this.pendingEditRowId = null
      this.pendingInstructor = null
      this.saving = false
      this.selectedDepartmentForm = null
      this.selectedEvaluationStatus = null
      this.selectedEvaluationType = null
      this.selectedStartDate = null
      this.focusedEditButtonEvaluationId = evaluation.id
      this.$putFocusNextTick(`edit-evaluation-${this.focusedEditButtonEvaluationId}-btn`)
    },
    afterSelectDepartmentForm(selected) {
      this.alertScreenReader(`${selected.name} department form selected.`)
      this.$putFocusNextTick('input-department-form')
    },
    customFilter(value, search, item) {
      if (!search) {
        return true
      }
      if (!value || typeof value === 'boolean') {
        return false
      }
      if (value === item.sortableInstructor) {
        value = item.searchableInstructor
      }
      if (value === item.lastUpdated) {
        value = this.$moment(item.lastUpdated).format('MM/DD/YYYY')
      }
      if (value === item.sortableCourseName) {
        value = item.searchableCourseName
      }
      if (value === item.sortableCourseNumber) {
        value = item.courseNumber
        if (item.crossListedWith) {
          value += (' ' + item.crossListedWith.join(', '))
        }
        if (item.roomSharedWith) {
          value += (' ' + item.roomSharedWith.join(', '))
        }
      }
      if (value === item.startDate) {
        value = [
          this.$moment(item.startDate).format('MM/DD/YY'),
          '-',
          this.$moment(item.endDate).format('MM/DD/YY'),
          (item.modular ? '2' : '3'),
          'weeks'
        ].join(' ')
      }
      return value.toString().toLocaleLowerCase().indexOf(search.toLocaleLowerCase()) !== -1
    },
    displayStatus(evaluation) {
      if (evaluation.status === 'review') {
        return 'To Do'
      } else if (evaluation.status === 'confirmed') {
        return 'Done'
      } else {
        return evaluation.status
      }
    },
    evaluationClass(evaluation, hover) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore muted--text': !hover && evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'secondary white--text border-bottom-none': evaluation.id === this.editRowId,
        'evaluation-row-review': evaluation.id !== this.editRowId && evaluation.status === 'review',
        'evaluation-row-xlisting': evaluation.id !== this.editRowId && !evaluation.status && (evaluation.crossListedWith || evaluation.roomSharedWith),
        'primary-contrast primary--text': (hover || evaluation.id === this.focusedEditButtonEvaluationId) && !this.isEditing(evaluation)
      }
    },
    evaluationPillClass(evaluation, hover) {
      return {
        'pill-confirmed': evaluation.status === 'confirmed',
        'pill-ignore': evaluation.status === 'ignore',
        'pill-review': evaluation.status === 'review',
        'sr-only': hover && this.allowEdits && !this.readonly
      }
    },
    instructorConfirmationText(instructor) {
      return `
        ${instructor.firstName} ${instructor.lastName} (${instructor.uid})
        is not currently listed in SIS data as an instructor for any courses.`
    },
    isEditing(evaluation) {
      return this.editRowId === evaluation.id
    },
    isStatusVisible(evaluation) {
      return !this.isEditing(evaluation)
        && evaluation.status
        && evaluation.id !== this.focusedEditButtonEvaluationId
    },
    minStartDate(evaluation) {
      return new Date(this.$_.get(evaluation, 'meetingDates.start'))
    },
    onCancelConfirm() {
      this.isConfirmingCancelEdit = false
      this.focusedEditButtonEvaluationId = this.$_.clone(this.pendingEditRowId)
      this.pendingEditRowId = null
      this.$putFocusNextTick(`edit-evaluation-${this.focusedEditButtonEvaluationId}-btn`)
    },
    onCancelEdit(evaluation) {
      this.alertScreenReader('Edit canceled.')
      this.afterEditEvaluation(evaluation)
    },
    onCancelNonSisInstructor() {
      this.isConfirmingNonSisInstructor = false
      this.pendingInstructor = null
    },
    onChangeSearchFilter(searchFilterResults) {
      this.searchFilterResults = searchFilterResults
      if (this.$_.size(this.selectedEvaluationIds)) {
        this.filterSelectedEvaluations({
          searchFilterResults: this.searchFilterResults,
          enabledStatuses: this.selectedFilterTypes
        })
      }
      if (!this.$_.some(this.searchFilterResults, {'id': this.editRowId})) {
        this.editRowId = null
      }
    },
    onConfirm() {
      this.isConfirmingCancelEdit = false
      this.editRowId = null
      const evaluation = this.$_.find(this.evaluations, ['id', this.pendingEditRowId])
      this.onEditEvaluation(evaluation)
    },
    onConfirmNonSisInstructor() {
      this.isConfirmingNonSisInstructor = false
    },
    onEditEvaluation(evaluation) {
      if (this.editRowId) {
        const editingEvaluation = this.$_.find(this.evaluations, ['id', this.editRowId])
        this.isConfirmingCancelEdit = editingEvaluation && (
          this.$_.get(this.pendingInstructor, 'uid') !== this.$_.get(editingEvaluation, 'instructor.uid')
          || this.selectedDepartmentForm !== this.$_.get(editingEvaluation, 'departmentForm.id')
          || this.selectedEvaluationStatus !== this.$_.get(editingEvaluation, 'status')
          || this.selectedEvaluationType !== this.$_.get(editingEvaluation, 'evaluationType.id')
          || this.selectedStartDate !== editingEvaluation.startDate
        )
      }
      if (this.isConfirmingCancelEdit) {
        this.pendingEditRowId = evaluation.id
      } else {
        this.editRowId = evaluation.id
        this.pendingInstructor = evaluation.instructor
        this.selectedDepartmentForm = this.$_.get(evaluation, 'departmentForm.id')
        this.selectedEvaluationStatus = this.$_.get(evaluation, 'status')
        this.selectedEvaluationType = this.$_.get(evaluation, 'evaluationType.id')
        this.selectedStartDate = evaluation.startDate
        this.$putFocusNextTick(`${this.readonly ? '' : 'select-evaluation-status'}`)
      }
    },
    onProceedMarkAsDone() {
      const evaluation = this.markAsDoneWarning.evaluation
      const fields = this.markAsDoneWarning.fields
      this.markAsDoneWarning = undefined
      this.updateEvaluation(evaluation, fields)
    },
    onSort() {
      const selectedEvaluationIds = this.$_.cloneDeep(this.selectedEvaluationIds)
      this.$nextTick(() => {
        this.setSelectedEvaluations(selectedEvaluationIds)
      })
    },
    validateAndSave(evaluation) {
      this.markAsDoneWarning = undefined
      const departmentFormId = this.selectedDepartmentForm || this.$_.get(evaluation, 'defaultDepartmentForm.id') || null
      const status = this.selectedEvaluationStatus === 'none' ? null : this.selectedEvaluationStatus
      const startDate = this.selectedStartDate ? this.$moment(this.selectedStartDate).format('YYYY-MM-DD') : null
      const fields = {
        departmentFormId,
        evaluationTypeId: this.selectedEvaluationType,
        instructorUid: this.$_.get(this.pendingInstructor, 'uid'),
        startDate,
        status
      }
      let warning
      if (status === 'confirmed') {
        // If evaluation start-date is in the past then put up a warning dialog.
        const proposedUpdate = {...evaluation, ...fields}
        warning = this.validateMarkAsDone([proposedUpdate])
      }
      if (warning) {
        this.markAsDoneWarning = {evaluation, fields, message: warning}
      } else {
        this.updateEvaluation(evaluation, fields)
      }
    },
    selectInstructor(instructor) {
      if (instructor) {
        instructor.emailAddress = instructor.email
        if (!instructor.isSisInstructor) {
          this.isConfirmingNonSisInstructor = true
        }
      }
      this.pendingInstructor = instructor
    },
    sort(sortBy, sortDesc) {
      this.sortBy = sortBy
      this.sortDesc = sortDesc
    },
    statusFilterEnabled(evaluation) {
      const status = evaluation.status || 'unmarked'
      return this.filterTypes[status].enabled
    },
    toggleFilter(type) {
      const filter = this.filterTypes[type]
      filter.enabled = !filter.enabled
      this.filterSelectedEvaluations({
          searchFilterResults: this.searchFilterResults,
          enabledStatuses: this.selectedFilterTypes
        })
      if (this.$_.some(this.evaluations, {'id': this.editRowId, 'status': type})) {
        this.editRowId = null
      }
      this.alertScreenReader(`Filter ${filter.label} ${filter.enabled ? 'enabled' : 'disabled'}.`)
    },
    toggleSelectAll() {
      if (this.allEvaluationsSelected || this.someEvaluationsSelected) {
        this.deselectAllEvaluations()
        this.alertScreenReader('All evaluations unselected')
      } else {
        this.alertScreenReader('All evaluations selected')
        this.selectAllEvaluations({
          searchFilterResults: this.searchFilterResults,
          enabledStatuses: this.selectedFilterTypes
        })
      }
    },
    updateEvaluation(evaluation, fields) {
      this.saving = true
      this.alertScreenReader('Saving evaluation row.')
      return new Promise(resolve => {
        if (fields.status === 'confirmed' &&
          !(fields.departmentFormId && fields.evaluationTypeId && fields.instructorUid)) {
          this.showErrorDialog('Cannot confirm an evaluation with missing fields.')
          this.saving = false
          resolve()
        } else {
          this.editEvaluation({
            evaluationId: evaluation.id,
            sectionId: evaluation.courseNumber,
            termId: this.selectedTermId,
            fields
          }).then(() => {
            this.alertScreenReader('Changes saved.')
            this.saving = false
            this.afterEditEvaluation(evaluation)
            this.deselectAllEvaluations()
            resolve()
          }).catch(error => {
            this.showErrorDialog(this.$_.get(error, 'response.data.message', 'An unknown error occurred.'))
            this.saving = false
            resolve()
          })
        }
      })
    },
    filterTypeCounts(type) {
      if (type === 'unmarked') {
        return this.evaluations.filter(e => e.status === null).length
      }
      return this.evaluations.filter(e => e.status === type).length
    }
  },
  created() {
    if (this.readonly) {
      this.evaluationHeaders = [{class: 'text-start text-nowrap pl-3', text: 'Department', value: 'department.id'}].concat(this.evaluationHeaders)
    } else if (this.allowEdits) {
      this.evaluationHeaders = [{class: 'text-start text-nowrap pl-1', text: 'Select', value: 'isSelected', width: '30px'}].concat(this.evaluationHeaders)
    }

    this.departmentForms = [{id: null, name: 'Revert'}].concat(this.activeDepartmentForms)
    this.evaluationTypes = [{id: null, name: 'Revert'}].concat(this.$config.evaluationTypes)

    this.rules.instructorUid = () => {
      return this.$_.get(this.pendingInstructor, 'uid') ? true : 'Instructor is required.'}
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
.evaluation-form-btn {
  width: 150px;
}
.evaluation-course-name {
  min-width: 200px;
}
.evaluation-course-number {
  min-width: 115px;
}
.evaluation-department-form {
  min-width: 155px;
}
.evaluation-instructor {
  min-width: 175px;
}
.evaluation-last-updated {
  min-width: 100px;
}
.evaluation-period {
  min-width: 135px;
}
.evaluation-row {
  vertical-align: top;
}
.evaluation-row.evaluation-row-enter-to {
  animation: 4s fadeOut;
  animation-timing-function: cubic-bezier(.05, -.12, .02, .32);
}
.evaluation-row.evaluation-row-enter-from,
.evaluation-row.evaluation-row-leave-to {
  opacity: 0;
  transform: translateX(50%);
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
.evaluation-search-input {
  max-width: 540px;
}
.evaluation-type {
  min-width: 145px;
}
.instructor-lookup {
  max-width: 168px !important;
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
.pill-confirmed {
  background-color: #176190;
}
.pill-ignore {
  background-color: #666;
}
.pill-invisible {
  border: none;
  padding: 0;
}
.pill-review {
  background-color: #478047;
}
.select-all-evals {
  height: 36px;
  width: 6.5rem;
}
.select-evaluation-status {
  width: 80%;
}
.sticky {
  position: sticky;
  top: 56px;
  z-index: 10;
}
.sticky-dark {
  background-color: #171717;
}
.sticky-light {
  background-color: #fff;
}
.xlisting-note {
  font-size: 0.8em;
}
</style>

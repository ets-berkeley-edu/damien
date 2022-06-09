<template>
  <div v-if="evaluations">
    <div class="elevation-2 sticky" :class="$vuetify.theme.dark ? 'sticky-dark' : 'sticky-light'">
      <v-row class="mt-0">
        <v-col cols="7" md="8" class="d-flex flex-column pt-2">
          <v-text-field
            id="evaluation-search-input"
            v-model="searchFilter"
            append-icon="mdi-magnify"
            class="flex-grow-0 flex-shrink-1 ml-4 pt-0 evaluation-search-input"
            color="tertiary"
            hide-details
            label="Find"
            max-width="600px"
            single-line
          ></v-text-field>
        </v-col>
        <v-col cols="5" md="4" class="pt-2">
          <AddCourseSection
            id="add-course-section"
            :evaluations="evaluations"
            :readonly="!allowEdits"
          />
        </v-col>
      </v-row>
      <v-row class="d-flex flex-column-reverse flex-md-row">
        <v-col
          cols="12"
          lg="7"
          md="8"
          class="d-flex"
        >
          <div class="d-flex align-self-stretch align-end mt-auto mx-4">
            <v-checkbox
              v-if="!readonly"
              id="select-all-evals-checkbox"
              class="align-center mt-0 pt-0"
              :disabled="$_.isEmpty(searchFilterResults)"
              hide-details
              :indeterminate="someEvaluationsSelected"
              :ripple="false"
              color="tertiary"
              :value="allEvaluationsSelected"
              @change="toggleSelectAll"
            >
              <template v-slot:label>
                <div v-if="!(someEvaluationsSelected || allEvaluationsSelected)" class="text-nowrap pl-1 py-2">
                  Select all
                </div>
              </template>
            </v-checkbox>
            <EvaluationActions v-if="!readonly" />
          </div>
        </v-col>
        <v-col cols="12" lg="5" md="4">
          <div class="d-flex flex-nowrap flex-md-wrap align-baseline justify-end mt-auto mx-4">
            <div class="mr-md-auto text-nowrap mr-2">Filter statuses:</div>
            <div class="d-flex flex-wrap">
              <v-chip
                v-for="type in $_.keys(filterTypes)"
                :id="`evaluations-filter-${type}`"
                :key="type"
                aria-controls="evaluation-table"
                :aria-selected="filterTypes[type].enabled"
                class="ma-1 px-4 text-center text-nowrap text-uppercase"
                :class="{
                  'secondary': filterTypes[type].enabled,
                  'inactive': !filterTypes[type].enabled
                }"
                :color="filterTypes[type].enabled ? 'secondary' : ''"
                role="tablist"
                small
                tabindex="0"
                :text-color="filterTypes[type].enabled ? 'white' : 'inactive-contrast'"
                @click="toggleFilter(type)"
                @keypress.enter.prevent="toggleFilter(type)"
              >
                <v-icon
                  v-if="filterTypes[type].enabled"
                  color="white"
                  small
                  left
                >
                  mdi-check-circle
                </v-icon>
                <v-icon
                  v-if="!filterTypes[type].enabled"
                  color="inactive-contrast"
                  small
                  left
                >
                  mdi-plus-circle
                </v-icon>
                {{ filterTypes[type].label }}
                {{ filterTypeCounts(type) }}
              </v-chip>
            </div>
          </div>
        </v-col>
      </v-row>
    </div>
    <v-data-table
      id="evaluation-table"
      disable-pagination
      :headers="headers"
      :search="searchFilter"
      hide-default-footer
      :items="evaluations"
      @current-items="onChangeSearchFilter"
    >
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
                <td v-if="readonly" :id="`evaluation-${rowIndex}-department`" class="py-1">
                  <router-link :to="`/department/${$_.get(evaluation.department, 'id')}`">
                    {{ $_.get(evaluation.department, 'name') }}
                  </router-link>
                </td>
                <td v-if="!readonly && allowEdits" class="text-center pr-1">
                  <v-checkbox
                    v-if="!isEditing(evaluation)"
                    :id="`evaluation-${rowIndex}-checkbox`"
                    :value="selectedEvaluationIds.includes(evaluation.id)"
                    class="pr-1"
                    :color="`${hover ? 'primary' : 'tertiary'}`"
                    :disabled="editRowId === evaluation.id"
                    :ripple="false"
                    @change="toggleSelectEvaluation(evaluation.id)"
                  ></v-checkbox>
                </td>
                <td
                  :id="`evaluation-${rowIndex}-status`"
                  :class="{'align-middle position-relative': !isEditing(evaluation)}"
                  class="px-1"
                >
                  <div
                    v-if="isStatusVisible(evaluation)"
                    class="pill mx-auto"
                    :class="evaluationPillClass(evaluation, hover)"
                  >
                    {{ evaluation.status }}
                  </div>
                  <div
                    v-if="allowEdits && !isEditing(evaluation) && (!readonly || !evaluation.status)"
                    class="pill pill-invisible mx-auto pl-0"
                  >
                    <v-btn
                      :id="`edit-evaluation-${evaluation.id}-btn`"
                      class="primary-contrast primary--text"
                      :class="{'sr-only': !hover && evaluation.id !== focusedEditButtonEvaluationId, 'focus-btn': evaluation.id === focusedEditButtonEvaluationId}"
                      block
                      :disabled="!allowEdits"
                      :ripple="false"
                      text
                      @click="onEditEvaluation(evaluation)"
                      @blur.native="() => focusedEditButtonEvaluationId = null"
                      @focus.native="() => focusedEditButtonEvaluationId = evaluation.id"
                      @keypress.enter.prevent="onEditEvaluation(evaluation)"
                    >
                      Edit
                    </v-btn>
                  </div>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <label id="select-evaluation-status-label" for="select-evaluation-status">
                      Status:
                    </label>
                    <select
                      id="select-evaluation-status"
                      v-model="selectedEvaluationStatus"
                      class="native-select-override light d-block mx-auto"
                      :disabled="saving"
                    >
                      <option v-for="s in evaluationStatuses" :key="s.text" :value="s.value">{{ s.text }}</option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-lastUpdated`" class="px-1" :class="{'pt-5': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
                  {{ $moment(evaluation.lastUpdated) | moment('MM/DD/YYYY') }}
                </td>
                <td :id="`evaluation-${rowIndex}-courseNumber`" class="px-1" :class="{'pt-5': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
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
                <td class="px-1" :class="{'pt-5': isEditing(evaluation), 'align-middle': !isEditing(evaluation)}">
                  <div :id="`evaluation-${rowIndex}-courseName`">
                    {{ evaluation.subjectArea }}
                    {{ evaluation.catalogId }}
                    {{ evaluation.instructionFormat }}
                    {{ evaluation.sectionNumber }}
                  </div>
                  <div :id="`evaluation-${rowIndex}-courseTitle`">
                    {{ evaluation.courseTitle }}
                  </div>
                </td>
                <td
                  :id="`evaluation-${rowIndex}-instructor`"
                  :class="{'pt-5': isEditing(evaluation) && evaluation.instructor, 'align-middle': !isEditing(evaluation)}"
                  class="px-1"
                >
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.firstName }}
                    {{ evaluation.instructor.lastName }}
                    ({{ evaluation.instructor.uid }})
                  </div>
                  <div v-if="evaluation.instructor">
                    {{ evaluation.instructor.emailAddress }}
                  </div>
                  <div v-if="!evaluation.instructor && isEditing(evaluation) && allowEdits">
                    <div class="mt-1 pb-2">
                      <label id="input-instructor-lookup-autocomplete-label" for="input-instructor-lookup-autocomplete">
                        Instructor<span class="sr-only"> search by name or UID</span>:
                      </label>
                      <PersonLookup
                        id="input-instructor-lookup-autocomplete"
                        class="instructor-lookup"
                        :disabled="saving"
                        :instructor-lookup="true"
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
                <td :id="`evaluation-${rowIndex}-departmentForm`" class="px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <div
                    v-if="evaluation.departmentForm && !isEditing(evaluation)"
                    :class="{'error--text': evaluation.conflicts.departmentForm}"
                  >
                    {{ evaluation.departmentForm.name }}
                    <div v-for="(conflict, index) in evaluation.conflicts.departmentForm" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value }} from {{ conflict.department }} department
                    </div>
                  </div>
                  <div
                    v-if="!evaluation.departmentForm && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    class="evaluation-error error--text"
                  >
                    <v-icon small color="error">mdi-alert-circle</v-icon> Department form required
                  </div>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
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
                <td :id="`evaluation-${rowIndex}-evaluationType`" class="px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <div v-if="evaluation.evaluationType && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.evaluationType}">
                    {{ evaluation.evaluationType.name }}
                    <div v-for="(conflict, index) in evaluation.conflicts.evaluationType" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon> Conflicts with value {{ conflict.value }} from {{ conflict.department }} department
                    </div>
                  </div>
                  <div
                    v-if="!evaluation.evaluationType && !isEditing(evaluation) && (evaluation.status === 'review' || evaluation.status === 'confirmed')"
                    class="evaluation-error error--text"
                  >
                    <v-icon small color="error">mdi-alert-circle</v-icon> Evaluation type required
                  </div>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <label id="select-evaluation-type-label" for="select-evaluation-type">
                      Evaluation Type:
                    </label>
                    <select
                      id="select-evaluation-type"
                      v-model="selectedEvaluationType"
                      class="native-select-override light"
                      :disabled="saving"
                    >
                      <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
                    </select>
                  </div>
                </td>
                <td :id="`evaluation-${rowIndex}-period`" class="px-1" :class="{'align-middle': !isEditing(evaluation)}">
                  <span v-if="evaluation.startDate && !isEditing(evaluation)" :class="{'error--text': evaluation.conflicts.evaluationPeriod}">
                    <div>{{ evaluation.startDate | moment('MM/DD/YY') }} - {{ evaluation.endDate | moment('MM/DD/YY') }}</div>
                    <div>{{ evaluation.modular ? 2 : 3 }} weeks</div>
                    <div v-for="(conflict, index) in evaluation.conflicts.evaluationPeriod" :key="index" class="evaluation-error error--text">
                      <v-icon small color="error">mdi-alert-circle</v-icon>
                      Conflicts with period starting
                      {{ $moment(conflict.value).format('MM/DD/YY') }}
                      from {{ conflict.department }} department
                    </div>
                  </span>
                  <div v-if="allowEdits && isEditing(evaluation)" class="mt-1 pb-2">
                    <div class="d-flex align-center">
                      <label id="input-evaluation-start-date-label" for="input-evaluation-start-date">
                        Start date:
                      </label>
                    </div>
                    <c-date-picker
                      v-model="selectedStartDate"
                      :min-date="minStartDate(evaluation)"
                      :max-date="maxStartDate(evaluation)"
                      title-position="left"
                    >
                      <template v-slot="{ inputValue, inputEvents }">
                        <input
                          id="input-evaluation-start-date"
                          class="datepicker-input input-override light mt-0"
                          :class="{'disabled': saving}"
                          :disabled="saving"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                        <div v-if="!selectedStartDate" id="error-msg-evaluation-start-date" class="evaluation-error">
                          <v-icon class="px-1" small color="white">mdi-alert-circle</v-icon>Required
                        </div>
                      </template>
                    </c-date-picker>
                  </div>
                </td>
              </tr>
            </v-hover>
            <tr v-if="isEditing(evaluation)" :key="`${evaluation.id}-edit`" class="secondary white--text border-top-none">
              <td></td>
              <td colspan="8" class="px-2">
                <div class="d-flex justify-end">
                  <v-btn
                    id="save-evaluation-edit-btn"
                    class="ma-2 evaluation-form-btn"
                    color="primary"
                    width="150px"
                    :disabled="disableControls || !rowValid || saving"
                    @click.prevent="saveEvaluation(evaluation)"
                    @keypress.enter.prevent="saveEvaluation(evaluation)"
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
      :model="isConfirmingCancelEdit"
      :cancel-action="onCancelConfirm"
      :perform-action="onConfirm"
      :text="'You have unsaved changes that will be lost.'"
      :title="'Cancel edit?'"
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
  <div v-else class="no-eligible-sections">
    <span>No eligible sections to load. You may still add a section manually.</span>
  </div>
</template>

<script>
import {getDepartmentForms} from '@/api/departmentForms'
import {getEvaluationTypes} from '@/api/evaluationTypes'
import AddCourseSection from '@/components/evaluation/AddCourseSection'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import EvaluationActions from '@/components/evaluation/EvaluationActions'
import PersonLookup from '@/components/admin/PersonLookup'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationTable',
  mixins: [Context, DepartmentEditSession, Util],
  components: {
    AddCourseSection,
    ConfirmDialog,
    EvaluationActions,
    PersonLookup
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
    evaluationStatuses: [
      {text: 'None', value: null},
      {text: 'To-do', value: 'review'},
      {text: 'Done', value: 'confirmed'},
      {text: 'Ignore', value: 'ignore'}
    ],
    evaluationTypes: [],
    filterTypes: {
      'unmarked': {label: 'None', enabled: true},
      'review': {label: 'To-Do', enabled: true},
      'confirmed': {label: 'Done', enabled: true},
      'ignore': {label: 'Ignore', enabled: false}
    },
    focusedEditButtonEvaluationId: null,
    headers: [
      {align: 'center', class: 'px-1 text-nowrap', text: 'Status', value: 'status', width: '120px'},
      {class: 'px-1 text-nowrap', text: 'Last Updated', value: 'lastUpdated', width: '75px'},
      {class: 'px-1 text-nowrap', text: 'Course Number', value: 'sortableCourseNumber', width: '80px'},
      {class: 'px-1 course-name', text: 'Course Name', value: 'sortableCourseName'},
      {class: 'px-1 text-nowrap', text: 'Instructor', value: 'sortableInstructor', width: '175px'},
      {class: 'px-1', text: 'Department Form', value: 'departmentForm.name', width: '155px'},
      {class: 'px-1', text: 'Evaluation Type', value: 'evaluationType.name', width: '145px'},
      {class: 'px-1 text-nowrap', text: 'Evaluation Period', value: 'startDate', width: '130px'}
    ],
    isConfirmingCancelEdit: false,
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
    selectedStartDate: null
  }),
  computed: {
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    },
    enabledStatusFilterTypes() {
      return this.$_.keys(this.$_.pickBy(this.filterTypes, 'enabled'))
    },
    rowValid() {
      const evaluation = this.$_.find(this.evaluations, ['id', this.editRowId])
      return this.selectedStartDate >= this.minStartDate(evaluation) && this.selectedStartDate <= this.maxStartDate(evaluation)
    },
    someEvaluationsSelected() {
      return !!(this.$_.size(this.selectedEvaluationIds) && this.$_.size(this.selectedEvaluationIds) < this.$_.size(this.evaluations))
    },
    allEvaluationsSelected() {
      return !!(this.$_.size(this.selectedEvaluationIds) && this.$_.size(this.selectedEvaluationIds) === this.$_.size(this.evaluations))
    }
  },
  methods: {
    afterEditEvaluation(evaluation) {
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
    clearPendingInstructor() {
      this.pendingInstructor = null
    },
    evaluationClass(evaluation, hover) {
      return {
        'evaluation-row-confirmed': evaluation.id !== this.editRowId && evaluation.status === 'confirmed',
        'evaluation-row-ignore muted--text': !hover && evaluation.id !== this.editRowId && evaluation.status === 'ignore',
        'secondary white--text border-bottom-none': evaluation.id === this.editRowId,
        'evaluation-row-review': evaluation.id !== this.editRowId && evaluation.status === 'review',
        'evaluation-row-xlisting': evaluation.id !== this.editRowId && !evaluation.status && (evaluation.crossListedWith || evaluation.roomSharedWith),
        'primary-contrast primary--text': (hover || evaluation.id === this.focusedEditButtonEvaluationId) && !this.readonly && !this.isEditing(evaluation)
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
    isEditing(evaluation) {
      return this.editRowId === evaluation.id
    },
    isStatusVisible(evaluation) {
      return !this.isEditing(evaluation)
        && evaluation.status
        && evaluation.id !== this.focusedEditButtonEvaluationId
    },
    maxStartDate(evaluation) {
      const courseEndDate = this.$moment(this.$_.get(evaluation, 'meetingDates.end'))
      const defaultEndDate = this.$moment(this.$config.termDates.default.end)

      let lastEndDate = courseEndDate > defaultEndDate ? courseEndDate : defaultEndDate
      if (lastEndDate === defaultEndDate && !this.selectedTerm.name.includes('Summer')) {
        lastEndDate = lastEndDate.add(2, 'day')
      }

      const courseLength = courseEndDate.diff(this.$_.get(evaluation, 'meetingDates.start'), 'days')
      if (courseLength < 90) {
        return lastEndDate.subtract(13, 'day').toDate()
      } else {
        return lastEndDate.subtract(20, 'day').toDate()
      }
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
    onChangeSearchFilter(searchFilterResults) {
      this.searchFilterResults = searchFilterResults
      if (this.$_.size(this.selectedEvaluationIds)) {
        this.filterSelectedEvaluations(searchFilterResults, this.enabledStatusFilterTypes)
      }
    },
    onConfirm() {
      this.isConfirmingCancelEdit = false
      this.editRowId = null
      const evaluation = this.$_.find(this.evaluations, ['id', this.pendingEditRowId])
      this.onEditEvaluation(evaluation)
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
    setPendingInstructor(instructor) {
      this.pendingInstructor = instructor
    },
    saveEvaluation(evaluation) {
      const fields = {
        'departmentFormId': this.selectedDepartmentForm,
        'evaluationTypeId': this.selectedEvaluationType,
        'instructorUid': this.$_.get(this.pendingInstructor, 'uid'),
        'status': this.selectedEvaluationStatus
      }
      if (this.selectedStartDate) {
        fields.startDate = this.$moment(this.selectedStartDate).format('YYYY-MM-DD')
      }
      this.updateEvaluation(evaluation, fields)
    },
    selectInstructor(instructor) {
      if (instructor) {
        instructor.emailAddress = instructor.email
      }
      this.setPendingInstructor(instructor)
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
          enabledStatuses: this.enabledStatusFilterTypes
        })
      this.alertScreenReader(`Filter ${filter.label} ${filter.enabled ? 'enabled' : 'disabled'}.`)
    },
    toggleSelectAll() {
      if (this.allEvaluationsSelected || this.someEvaluationsSelected) {
        this.deselectAllEvaluations()
      } else {
        this.selectAllEvaluations({
          searchFilterResults: this.searchFilterResults,
          enabledStatuses: this.enabledStatusFilterTypes
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
            fields
          }).then(() => {
            this.alertScreenReader('Changes saved.')
            this.saving = false
            this.afterEditEvaluation(evaluation)
            this.deselectAllEvaluations()
            resolve()
          }, error => {
            this.showErrorDialog(error)
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
      this.headers = [{class: 'text-nowrap', text: 'Department', value: 'department.id'}].concat(this.headers)
    } else if (this.allowEdits) {
      this.headers = [{class: 'text-nowrap pr-1', text: 'Select', width: '30px'}].concat(this.headers)
    }
    getDepartmentForms().then(data => {
      this.departmentForms = [{id: null, name: 'Revert'}].concat(data)
    })
    getEvaluationTypes().then(data => {
      this.evaluationTypes = [{id: null, name: 'None'}].concat(data)
    })
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
.filter-div {
  padding:  16px 16px 16px 50px;
}
</style>

<style scoped>
.align-middle {
  vertical-align: middle;
}
.evaluation-error {
  font-size: 0.8em;
  font-style: italic;
}
.evaluation-form-btn {
  width: 150px;
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
.hidden {
  visibility: hidden;
}
.input-department-form {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.instructor-lookup {
  max-width: 168px !important;
}
.no-eligible-sections {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 40px;
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
  background-color: #666;
}
.pill-ignore {
  background-color: #777;
}
.pill-invisible {
  border: none;
}
.pill-review {
  background-color: #595;
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

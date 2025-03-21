<template>
  <ModalDialog
    :is-open="model"
    :id-prefix="idPrefix"
    min-width="700"
    max-width="1000"
    :on-click-outside="onClickCancel"
    role="dialog"
    text-class="px-0"
    width="90%"
  >
    <template #title>{{ action }} {{ selectedEvaluationsDescription }}</template>
    <template #text>
      <v-container class="px-16 pb-4">
        <slot name="status" :status="selectedEvaluationStatus" :on="{change: e => selectedEvaluationStatus = e.target.value}"></slot>
        <PersonLookup
          v-if="isObject(instructor)"
          :disabled="disableControls"
          :id-prefix="`${idPrefix}-instructor-lookup`"
          :inline="true"
          input-class="bulk-action-form-input"
          :instructor-lookup="true"
          label="Instructor"
          label-class="v-label d-flex text-no-wrap align-center"
          list-label="Suggested Instructors List"
          :on-select-result="selectInstructor"
          :required="!midtermFormSelected"
        />
        <v-row v-if="midtermFormAvailable" class="d-flex align-center" dense>
          <v-col cols="4"></v-col>
          <v-col cols="8">
            <v-checkbox
              :id="`${idPrefix}-midterm-checkbox`"
              v-model="midtermFormSelected"
              :aria-describedby="undefined"
              color="primary"
              density="comfortable"
              :disabled="disableControls"
              hide-details
              label="Use midterm department forms"
            />
          </v-col>
        </v-row>
        <slot name="form" :form="selectedDepartmentForm" :on="{change: e => selectedDepartmentForm = toInteger(e.target.value)}"></slot>
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label :for="`${idPrefix}-select-type`" class="v-label d-block text-no-wrap py-1">
              Evaluation Type
            </label>
          </v-col>
          <v-col cols="8">
            <select
              :id="`${idPrefix}-select-type`"
              v-model="selectedEvaluationType"
              class="bulk-action-form-input v-theme--light"
              :disabled="disableControls"
            >
              <option v-for="et in evaluationTypes" :key="et.id" :value="et.id">{{ et.name }}</option>
            </select>
          </v-col>
        </v-row>
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label
              :for="`${idPrefix}-start-date-input`"
              class="v-label text-no-wrap"
            >
              Evaluation Start Date
            </label>
          </v-col>
          <v-col cols="8">
            <AccessibleDateInput
              aria-label="Select Date"
              :container-id="`${idPrefix}-dialog-text`"
              :disabled="disableControls"
              :get-value="() => selectedStartDate"
              :id-prefix="`${idPrefix}-start-date`"
              :min-date="get(validStartDates, 'min')"
              :max-date="get(validStartDates, 'max')"
              :set-value="selectedDate => selectedStartDate = selectedDate"
            />
          </v-col>
        </v-row>
      </v-container>
      <v-table v-if="size(selectedEvaluations)" density="compact" class="bg-surface-variant bulk-action-preview-table mt-2 pb-2">
        <caption class="bulk-action-preview-caption font-weight-bold pb-2 text-left"><div class="px-6 py-4">Preview Your Changes</div></caption>
        <thead>
          <tr>
            <th
              v-for="(clazz, colName) in previewHeaders"
              :key="clazz"
              class="px-1"
              :class="clazz"
            >
              {{ colName }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(evaluation, index) in selectedEvaluations" :key="index">
            <tr>
              <td :id="`preview-${index}-status`" class="bulk-action-status-col pr-1 py-1">
                <div v-if="evaluation.status" :class="{'text-decoration-line-through text-accent': action === 'Edit' && showSelectedStatus(evaluation)}">
                  {{ getStatusText(evaluation.status) }}
                </div>
                <div v-if="action === 'Edit' && showSelectedStatus(evaluation)">
                  {{ getStatusText(selectedEvaluationStatus) }}
                </div>
              </td>
              <td :id="`preview-${index}-courseNumber`" class="bulk-action-courseNumber-col pa-1">{{ evaluation.courseNumber }}</td>
              <td :id="`preview-${index}-courseName`" class="bulk-action-courseName-col pa-1">
                <div>{{ evaluation.subjectArea }} {{ evaluation.catalogId }}</div>
                <div>{{ evaluation.instructionFormat }} {{ evaluation.sectionNumber }}</div>
              </td>
              <td :id="`preview-${index}-instructor`" class="bulk-action-instructor-col pa-1">
                <div v-if="get(evaluation, 'instructor.uid')" :class="{'text-decoration-line-through text-accent': action === 'Edit' && showSelectedInstructor(evaluation)}">
                  {{ evaluation.instructor.firstName }} {{ evaluation.instructor.lastName }}
                  ({{ evaluation.instructor.uid }})
                </div>
                <div v-if="action === 'Edit' && showSelectedInstructor(evaluation)">
                  {{ selectedInstructor.firstName }} {{ selectedInstructor.lastName }}
                  ({{ selectedInstructor.uid }})
                </div>
              </td>
              <td :id="`preview-${index}-departmentForm`" class="bulk-action-departmentForm-col pa-1">
                <div v-if="evaluation.departmentForm" :class="{'text-decoration-line-through text-accent': action === 'Edit' && showSelectedDepartmentForm(evaluation)}">
                  {{ evaluation.departmentForm.name }}
                </div>
                <div v-if="action === 'Edit' && showSelectedDepartmentForm(evaluation)">
                  {{ selectedDepartmentFormName }}
                </div>
              </td>
              <td :id="`preview-${index}-evaluationType`" class="bulk-action-evaluationType-col pa-1">
                <div v-if="evaluation.evaluationType" :class="{'text-decoration-line-through text-accent text-accent': action === 'Edit' && showSelectedEvaluationType(evaluation)}">
                  {{ evaluation.evaluationType.name }}
                </div>
                <div v-if="action === 'Edit' && showSelectedEvaluationType(evaluation)">
                  {{ selectedEvaluationTypeName }}
                </div>
              </td>
              <td :id="`preview-${index}-startDate`" class="bulk-action-startDate-col pa-1">
                <div v-if="evaluation.startDate" :class="{'text-decoration-line-through text-accent': action === 'Edit' && showSelectedStartDate(evaluation)}">
                  {{ DateTime.fromJSDate(evaluation.startDate).toFormat('MM/dd/yy') }}
                </div>
                <div v-if="action === 'Edit' && showSelectedStartDate(evaluation)">
                  {{ DateTime.fromJSDate(selectedStartDate).toFormat('MM/dd/yy') }}
                </div>
              </td>
            </tr>
            <tr v-if="action === 'Duplicate'" :key="`${index}-dupe`">
              <td :id="`preview-${index}-dupe-status`" class="bulk-action-status-col pr-1"></td>
              <td :id="`preview-${index}-dupe-courseNumber`" class="bulk-action-courseNumber-col px-1">{{ evaluation.courseNumber }}</td>
              <td :id="`preview-${index}-dupe-courseName`" class="bulk-action-courseName-col px-1">
                <div>{{ evaluation.subjectArea }} {{ evaluation.catalogId }}</div>
                <div>{{ evaluation.instructionFormat }} {{ evaluation.sectionNumber }}</div>
              </td>
              <td :id="`preview-${index}-dupe-instructor`" class="bulk-action-instructor-col px-1">
                <div v-if="showSelectedInstructor(evaluation)">
                  {{ selectedInstructor.firstName }} {{ selectedInstructor.lastName }}
                  ({{ selectedInstructor.uid }})
                </div>
                <div v-if="!showSelectedInstructor(evaluation) && evaluation.instructor">
                  {{ evaluation.instructor.firstName }} {{ evaluation.instructor.lastName }}
                  ({{ evaluation.instructor.uid }})
                </div>
              </td>
              <td :id="`preview-${index}-dupe-departmentForm`" class="bulk-action-departmentForm-col px-1">
                <template v-if="midtermFormSelected && get(evaluation, 'departmentForm.name')">
                  {{ endsWith(evaluation.departmentForm.name, '_MID') ? evaluation.departmentForm.name : `${evaluation.departmentForm.name}_MID` }}
                </template>
                <template v-else>
                  {{ get(evaluation, 'departmentForm.name') }}
                </template>
              </td>
              <td :id="`preview-${index}-dupe-evaluationType`" class="bulk-action-evaluationType-col px-1">
                <div>
                  {{ showSelectedEvaluationType(evaluation) ? selectedEvaluationTypeName : get(evaluation, 'evaluationType.name') }}
                </div>
              </td>
              <td :id="`preview-${index}-dupe-startDate`" class="bulk-action-startDate-col px-1">
                <div>
                  {{ DateTime.fromISO(new Date(selectedStartDate || evaluation.startDate).toISOString()).toFormat("MM/dd/yy") }}
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </v-table>
    </template>
    <template #actions>
      <div class="align-center d-flex">
        <ProgressButton
          :id="`${idPrefix}-apply-course-action-btn`"
          :action="onClickApply"
          :disabled="disableApply"
          :in-progress="isApplying"
          text="Apply"
        />
        <v-btn
          :id="`${idPrefix}-cancel-duplicate-btn`"
          class="ml-2"
          :disabled="disableControls"
          text="Cancel"
          variant="outlined"
          @click="onClickCancel"
        />
      </div>
    </template>
  </ModalDialog>
  <ConfirmDialog
    :disabled="disableControls"
    :is-open="isConfirmingNonSisInstructor"
    :on-click-cancel="onCancelNonSisInstructor"
    :on-click-confirm="onConfirmNonSisInstructor"
    :text="instructorConfirmationText(selectedInstructor)"
    title="Add new instructor?"
  />
</template>

<script setup>
import AccessibleDateInput from '@/components/util/AccessibleDateInput'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import ModalDialog from '@/components/util/ModalDialog'
import PersonLookup from '@/components/admin/PersonLookup'
import ProgressButton from '@/components/util/ProgressButton'
import {EVALUATION_STATUSES, useDepartmentStore} from '@/stores/department/department-edit-session'
import {addInstructor} from '@/api/instructor'
import {computed, inject, onMounted, ref, watch} from 'vue'
import {endsWith, filter, find, get, isEmpty, isObject, map, max, min, size, toInteger} from 'lodash'
import {putFocusNextTick, toFormatFromJsDate} from '@/lib/utils'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {DateTime} from 'luxon'

const props = defineProps({
  action: {
    required: true,
    type: String
  },
  applyAction: {
    required: true,
    type: Function
  },
  cancelAction: {
    required: true,
    type: Function
  },
  departmentForm: {
    default: undefined,
    required: false,
    type: Number
  },
  evaluationStatus: {
    default: undefined,
    required: false,
    type: String
  },
  evaluationType: {
    default: undefined,
    required: false,
    type: Number
  },
  idPrefix: {
    default: 'update-evaluations',
    required: false,
    type: String
  },
  instructor: {
    default: undefined,
    required: false,
    type: Object
  },
  isApplying: {
    required: true,
    type: Boolean
  },
  isUpdating: {
    required: true,
    type: Boolean
  },
  midtermFormAvailable: {
    required: false,
    type: Boolean
  },
  midtermFormEnabled: {
    required: false,
    type: Boolean
  },
  startDate: {
    default: undefined,
    required: false,
    type: Date
  }
})

const {disableControls, evaluations} = storeToRefs(useDepartmentStore())
const evaluationTypes = ref([])
const isConfirmingNonSisInstructor = ref(false)
const midtermFormSelected = ref(false)
const model = ref(false)
const previewHeaders = {
  'Status': 'bulk-action-status-col',
  'Course Number': 'bulk-action-courseNumber-col',
  'Course Name': 'bulk-action-courseName-col',
  'Instructor': 'bulk-action-instructor-col',
  'Department Form': 'bulk-action-departmentForm-col',
  'Evaluation Type': 'bulk-action-evaluationType-col',
  'Start Date': 'bulk-action-startDate-col'
}
const selectedDepartmentForm = ref(undefined)
const selectedEvaluations = ref([])
const selectedEvaluationStatus = ref(undefined)
const selectedEvaluationType = ref(undefined)
const selectedInstructor = ref(undefined)
const selectedStartDate = ref(undefined)

const allowEdits = computed(() => {
  const currentUser = useContextStore().currentUser
  return currentUser.isAdmin || !useContextStore().isSelectedTermLocked
})
const disableApply = computed(() => {
  return disableControls.value ||
    !allowEdits.value ||
    (props.midtermFormAvailable && !midtermFormSelected.value && !get(selectedInstructor.value, 'uid'))
})
const selectedDepartmentFormName = computed(() => {
  return get(find(useContextStore().config.departmentForms, df => df.id === selectedDepartmentForm.value), 'name')
})
const selectedEvaluationsDescription = computed(() => {
  if (isEmpty(selectedEvaluations.value)) {
    return ''
  }
  return `${selectedEvaluations.value.length} ${selectedEvaluations.value.length === 1 ? 'row' : 'rows'}`
})
const selectedEvaluationTypeName = computed(() => {
  return get(find(useContextStore().config.evaluationTypes, et => et.id === selectedEvaluationType.value), 'name')
})
const selectedStartDay = computed(() => {
  return selectedStartDate.value ? toFormatFromJsDate(selectedStartDate.value, 'o') : null
})
const validStartDates = computed(() => {
  // The intersection of the selected rows' allowed evaluation start dates
  return {
    'max': min(map(selectedEvaluations.value, e => e.maxStartDate)),
    'min': max(map(selectedEvaluations.value, e => e.meetingDates.start))
  }
})

const duplicatingEvaluationId = inject('duplicatingEvaluationId', undefined)

onMounted(() => {
  evaluationTypes.value = [{id: null, name: 'Default'}].concat(useContextStore().config.evaluationTypes)
  model.value = props.isUpdating
  midtermFormSelected.value = props.midtermFormEnabled
})

watch(() => props.isUpdating, v => {
  model.value = v
})
watch(model, isOpen => {
  reset()
  if (isOpen) {
    if (props.action === 'Edit') {
      putFocusNextTick('update-evaluations-select-status')
    } else if (props.midtermFormAvailable) {
      putFocusNextTick(`${props.idPrefix}-midterm-checkbox`)
    } else {
      putFocusNextTick(isObject(props.instructor) ? `${props.idPrefix}-instructor-lookup` : `${props.idPrefix}-select-type`)
    }
  }
})

const getStatusText = status => {
  return status === 'none' ? null : get(find(EVALUATION_STATUSES, es => es.value === status), 'text')
}

const instructorConfirmationText = instructor => {
  if (instructor) {
    return `
      ${instructor.firstName} ${instructor.lastName} (${instructor.uid})
      is not currently listed in SIS data as an instructor for any courses.`
  }
  return ''
}

const onCancelNonSisInstructor = () => {
  isConfirmingNonSisInstructor.value = false
  selectedInstructor.value = null
}

const onClickApply = () => {
  props.applyAction({
    departmentForm: selectedDepartmentForm.value,
    evaluationStatus: selectedEvaluationStatus.value === 'none' ? null : selectedEvaluationStatus.value,
    evaluationType: selectedEvaluationType.value,
    instructor: selectedInstructor.value || props.instructor,
    midtermFormEnabled: midtermFormSelected.value,
    startDate: selectedStartDate.value
  })
  if (selectedInstructor.value && selectedInstructor.value.isSisInstructor === false) {
    addInstructor(selectedInstructor.value)
  }
}

const onClickCancel = () => {
  selectedDepartmentForm.value = null
  selectedEvaluationStatus.value = null
  selectedEvaluationType.value = null
  selectedInstructor.value = null
  selectedStartDate.value = null
  props.cancelAction()
}

const onConfirmNonSisInstructor = () => {
  isConfirmingNonSisInstructor.value = false
}

const showSelectedDepartmentForm = evaluation => {
  return selectedDepartmentForm.value && selectedDepartmentForm.value !== get(evaluation, 'departmentForm.id')
}

const showSelectedEvaluationType = evaluation => {
  return selectedEvaluationType.value && selectedEvaluationType.value !== get(evaluation, 'evaluationType.id')
}

const showSelectedInstructor = evaluation => {
  return get(selectedInstructor.value, 'uid') && selectedInstructor.value.uid !== get(evaluation, 'instructor.uid')
}

const showSelectedStartDate = evaluation => {
  return selectedStartDate.value && selectedStartDay.value !== toFormatFromJsDate(evaluation.startDate, 'o')
}

const showSelectedStatus = evaluation => {
  return selectedEvaluationStatus.value && selectedEvaluationStatus.value !== evaluation.status
}

const reset = () => {
  const filterCriteria = duplicatingEvaluationId.value ? {'id': duplicatingEvaluationId.value} : 'isSelected'
  selectedEvaluations.value = filter(evaluations.value, filterCriteria)
  selectedDepartmentForm.value = props.departmentForm
  selectedEvaluationStatus.value = props.evaluationStatus
  selectedEvaluationType.value = props.evaluationType
  selectedInstructor.value = props.instructor
  selectedStartDate.value = props.startDate
}

const selectInstructor = suggestion => {
  selectedInstructor.value = suggestion
  if (selectedInstructor.value) {
    selectedInstructor.value.emailAddress = selectedInstructor.value.email
    if (selectedInstructor.value.isSisInstructor === false) {
      isConfirmingNonSisInstructor.value = true
    }
  }
}
</script>

<style>
.bulk-action-form-input {
  max-width: 250px;
}
</style>

<style scoped>
.bulk-action-courseName-col {
  min-width: 6rem;
  width: 20%;
}
.bulk-action-courseNumber-col {
  min-width: 2.5rem;
  width: 10%;
}
.bulk-action-departmentForm-col {
  min-width: 7rem;
  width: 15%;
}
.bulk-action-evaluationType-col {
  min-width: 5rem;
  width: 15%;
}
.bulk-action-instructor-col {
  min-width: 7.5rem;
  width: 25%;
}
.bulk-action-preview-caption {
  font-size: 16px;
  font-weight: 500;
}
.bulk-action-startDate-col {
  min-width: 65px;
  padding-right: 12px !important;
  width: 10%;
}
.bulk-action-status-col {
  min-width: 3.65rem;
  padding-left: 12px !important;
  width: 5%;
}
</style>

<template>
  <div class="align-center d-flex">
    <div class="align-center d-flex flex-wrap pl-2">
      <div v-for="(action, key) in courseActions" :key="key" class="align-center d-flex">
        <div :class="`evaluation-${key}-btn`">
          <v-btn
            :id="`apply-course-action-btn-${key}`"
            :key="key"
            class="font-weight-bold text-capitalize text-no-wrap mx-0 px-2"
            color="primary"
            :disabled="disableControls || !allowEdits || !selectedEvaluationIds.length || isLoading || isInvalidAction(action)"
            variant="text"
            @click.stop="action.apply(key)"
          >
            <span v-if="!(isLoading && key !== 'duplicate' && applyingAction.key === key)">{{ action.text }}</span>
            <v-progress-circular
              v-if="isLoading && key !== 'duplicate' && applyingAction.key === key"
              :indeterminate="true"
              color="primary"
              rotate="5"
              size="20"
              width="3"
            />
          </v-btn>
        </div>
        <div v-if="key === 'ignore'" class="pipe-separator text-disabled">
          <span role="separator">|</span>
        </div>
      </div>
    </div>
    <UpdateEvaluations
      key="0"
      action="Duplicate"
      :apply-action="onConfirmDuplicate"
      :cancel-action="onCancelDuplicate"
      id-prefix="duplicate-evaluations"
      :is-applying="isApplying"
      :is-updating="isDuplicating"
      :midterm-form-available="midtermFormAvailable"
      v-bind="bulkUpdateOptions"
    />
    <UpdateEvaluations
      key="1"
      action="Edit"
      :apply-action="onConfirmEdit"
      :cancel-action="onCancelEdit"
      :is-applying="isApplying"
      :is-updating="isEditing"
      v-bind="bulkUpdateOptions"
    >
      <template #status="{status, on}">
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label for="update-evaluations-select-status" class="v-label">
              Status
            </label>
          </v-col>
          <v-col cols="8">
            <select
              id="update-evaluations-select-status"
              class="bulk-action-form-input v-theme--light"
              :disabled="disableControls"
              :status="status"
              :value="status"
              autocomplete="off"
              v-on="on"
            >
              <option v-for="s in EVALUATION_STATUSES" :key="s.text" :value="s.value">{{ s.text }}</option>
            </select>
          </v-col>
        </v-row>
      </template>
      <template #form="{form, on}">
        <v-row class="d-flex align-center" dense>
          <v-col cols="4">
            <label for="update-evaluations-select-form" class="v-label">
              Department Form
            </label>
          </v-col>
          <v-col>
            <select
              id="update-evaluations-select-form"
              class="bulk-action-form-input v-theme--light"
              :disabled="disableControls"
              :form="form"
              :value="form"
              autocomplete="off"
              v-on="on"
            >
              <option v-for="df in activeDepartmentForms" :key="df.id" :value="df.id">{{ df.name }}</option>
            </select>
          </v-col>
        </v-row>
      </template>
    </UpdateEvaluations>
    <ConfirmDialog
      confirm-button-label="Confirm anyway"
      :hide-confirm="!currentUser.isAdmin"
      :html="markAsDoneWarning"
      :icon="mdiAlertCircle"
      :is-open="!!markAsDoneWarning"
      :on-click-cancel="() => markAsDoneWarning = undefined"
      :on-click-confirm="onOverrideMarkAsDoneWarning"
      title="Warning"
    />
  </div>
</template>

<script setup>
import {filter as _filter, chain, compact, each, every, get, has, includes, map, noop, uniq} from 'lodash'
import {computed, inject, onMounted, ref, watch} from 'vue'
import {mdiAlertCircle} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {DateTime} from 'luxon'
import ConfirmDialog from '@/components/util/ConfirmDialog'
import UpdateEvaluations from '@/components/evaluation/UpdateEvaluations'
import {EVALUATION_STATUSES, useDepartmentStore} from '@/stores/department/department-edit-session'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {updateEvaluations} from '@/api/departments'
import {useContextStore} from '@/stores/context'
import {validateConfirmable, validateDuplicable, validateMarkAsDone} from '@/stores/department/utils'

const props = defineProps({
  reset: {
    default: () => {},
    required: false,
    type: Function
  }
})

const departmentStore = useDepartmentStore()
const {activeDepartmentForms, department, disableControls, evaluations, selectedEvaluationIds} = storeToRefs(departmentStore)

const applyingAction = ref(undefined)
const bulkUpdateOptions = ref({
  departmentForm: undefined,
  evaluationStatus: undefined,
  evaluationType: undefined,
  instructor: undefined,
  midtermFormEnabled: false,
  startDate: undefined
})
const courseActions = ref({})
const isApplying = ref(false)
const isDuplicating = ref(false)
const isEditing = ref(false)
const isLoading = ref(false)
const markAsDoneWarning = ref(undefined)
const midtermFormAvailable = ref(false)
const onOverrideMarkAsDoneWarning = ref(noop)

const currentUser = useContextStore().currentUser
const allowEdits = computed(() => {
  return currentUser.isAdmin || !useContextStore().isSelectedTermLocked
})
const selectedEvaluations = computed(() => {
  const filterCriteria = duplicatingEvaluationId.value ? {'id': duplicatingEvaluationId.value} : e => selectedEvaluationIds.value.includes(e.id)
  return _filter(evaluations.value, filterCriteria)
})

const duplicatingEvaluationId = inject('duplicatingEvaluationId', undefined)

watch(duplicatingEvaluationId, v => {
  if (v) {
    onClickDuplicate()
  }
})

onMounted(() => {
  courseActions.value = {
    // TO DO: Clean up dictionary keys and statuses
    review: {
      apply: onClickReview,
      completedText: 'Marked as to-do',
      inProgressText: 'Marking as to-do',
      status: 'review',
      key: 'review',
      text: 'Mark as to-do'
    },
    confirm: {
      apply: onClickMarkDone,
      completedText: 'Marked as done',
      inProgressText: 'Marking as done',
      status: 'confirmed',
      key: 'confirm',
      text: 'Mark as done'
    },
    unmark: {
      apply: onClickUnmark,
      completedText: 'Unmarked',
      inProgressText: 'Unmarking',
      status: null,
      key: 'unmark',
      text: 'Unmark'
    },
    ignore: {
      apply: onClickIgnore,
      completedText: 'Ignored',
      inProgressText: 'Ignoring',
      status: 'ignore',
      key: 'ignore',
      text: 'Ignore'
    },
    duplicate: {
      apply: onClickDuplicate,
      completedText: 'Duplicated',
      inProgressText: 'Duplicating',
      key: 'duplicate',
      text: 'Duplicate'
    },
    edit: {
      apply: onClickEdit,
      completedText: 'Edited',
      inProgressText: 'Editing',
      key: 'edit',
      text: 'Edit'
    }
  }
})

const onCancelDuplicate = () => {
  const nextFocusId = duplicatingEvaluationId.value ? `evaluation-menu-btn-${duplicatingEvaluationId.value}` : 'apply-course-action-btn-duplicate'
  reset()
  alertScreenReader('Canceled duplication.')
  putFocusNextTick(nextFocusId, {scroll: false})
}

const onCancelEdit = () => {
  reset()
  alertScreenReader('Canceled edit.')
  putFocusNextTick('apply-course-action-btn-edit', {scroll: false})
}

const onClickDuplicate = () => {
  showUpdateOptions()
  bulkUpdateOptions.value.instructor = {}
  midtermFormAvailable.value = department.value.usesMidtermForms
  if (midtermFormAvailable.value) {
    // Show midterm form option only if a midterm form exists for all selected evals.
    const availableFormNames = map(activeDepartmentForms.value, 'name')
    each(selectedEvaluations.value, e => {
      const formName = get(e, 'departmentForm.name')
      if (!formName || !(formName.endsWith('_MID') || availableFormNames.includes(formName + '_MID'))) {
        midtermFormAvailable.value = false
        return false
      }
    })
  }
  isDuplicating.value = true
  putFocusNextTick('duplicate-evaluations-instructor-lookup-input')
}

const onClickEdit = () => {
  showUpdateOptions()
  // Pre-populate form if shared by all selected evals
  const uniqueForms = chain(selectedEvaluations.value).map(e => get(e, 'departmentForm.id')).uniq().value()
  if (uniqueForms.length === 1) {
    bulkUpdateOptions.value.departmentForm = get(selectedEvaluations.value, '0.departmentForm.id')
  }
  // Show instructor lookup if instructor is missing from all selected evals
  if (every(selectedEvaluations.value, {'instructor': null})) {
    bulkUpdateOptions.value.instructor = {}
  }
  // Pre-populate status if shared by all selected evals
  const uniqueStatuses = chain(selectedEvaluations.value).map(e => get(e, 'status')).uniq().value()
  if (uniqueStatuses.length === 1) {
    bulkUpdateOptions.value.evaluationStatus = get(selectedEvaluations.value, '0.status', 'none')
  }
  isEditing.value = true
  putFocusNextTick('update-evaluations-select-status')
}

const onClickIgnore = key => {
  validateAndUpdate(key)
}

const onClickMarkDone = key => {
  const selected = _filter(evaluations.value, e => includes(selectedEvaluationIds.value, e.id))
  markAsDoneWarning.value = validateMarkAsDone(selected)
  if (markAsDoneWarning.value) {
    if (currentUser.isAdmin) {
      onOverrideMarkAsDoneWarning.value = () => {
        validateAndUpdate(key)
        markAsDoneWarning.value = null
      }
    }
  } else {
    validateAndUpdate(key)
  }
}

const onClickReview = key => {
  validateAndUpdate(key)
}

const onClickUnmark = key => {
  validateAndUpdate(key)
}

const onConfirmDuplicate = options => {
  bulkUpdateOptions.value = options
  validateAndUpdate('duplicate')
}

const onConfirmEdit = options => {
  const selected = _filter(evaluations.value, e => includes(selectedEvaluationIds.value, e.id))
  bulkUpdateOptions.value = options
  const evaluationsToValidate = compact(map(selected, e => {
    if ((bulkUpdateOptions.value.evaluationStatus || e.status) === 'confirmed') {
      return {
        ...e,
        status: bulkUpdateOptions.value.evaluationStatus || e.status,
        startDate: bulkUpdateOptions.value.startDate || e.startDate
      }
    }
  }))
  markAsDoneWarning.value = validateMarkAsDone(evaluationsToValidate)
  if (markAsDoneWarning.value) {
    if (currentUser.isAdmin) {
      onOverrideMarkAsDoneWarning.value = () => {
        validateAndUpdate('edit')
        markAsDoneWarning.value = null
      }
    }
  } else {
    validateAndUpdate('edit')
  }
}

const getEvaluationFieldsForUpdate = key => {
  let fields = null
  if (['duplicate', 'edit'].includes(key)) {
    fields = {}
    if (bulkUpdateOptions.value.departmentForm) {
      fields.departmentFormId = bulkUpdateOptions.value.departmentForm
    }
    if (has(bulkUpdateOptions.value, 'evaluationStatus')) {
      fields.status = bulkUpdateOptions.value.evaluationStatus
    }
    if (bulkUpdateOptions.value.evaluationType) {
      fields.evaluationTypeId = bulkUpdateOptions.value.evaluationType
    }
    if (bulkUpdateOptions.value.instructor) {
      fields.instructorUid = get(bulkUpdateOptions.value.instructor, 'uid')
    }
    if (bulkUpdateOptions.value.startDate) {
      fields.startDate = DateTime.fromJSDate(bulkUpdateOptions.value.startDate).toFormat('yyyy-MM-dd')
    }
    if (key === 'duplicate') {
      if (bulkUpdateOptions.value.midtermFormEnabled) {
        fields.midterm = 'true'
      }
    }
  }
  return fields
}

const isInvalidAction = action => {
  const uniqueStatuses = uniq(evaluations.value.filter(e => selectedEvaluationIds.value.includes(e.id)).map(e => e.status))
  return (uniqueStatuses.length === 1 && uniqueStatuses[0] === action.status)
}

const reset = () => {
  bulkUpdateOptions.value = {
    departmentForm: null,
    evaluationStatus: null,
    evaluationType: null,
    instructor: null,
    midtermFormEnabled: false,
    startDate: null,
  }
  isDuplicating.value = false
  isEditing.value = false
  applyingAction.value = null
  isApplying.value = false
  isLoading.value = false
  markAsDoneWarning.value = null
  midtermFormAvailable.value = false
  props.reset()
}

const showUpdateOptions = () => {
  // Pre-populate start date if shared by all selected evals.
  const uniqueStartDates = chain(selectedEvaluations.value).map(e => new Date(e.startDate).toDateString()).uniq().value()
  if (uniqueStartDates.length === 1) {
    bulkUpdateOptions.value.startDate = new Date(uniqueStartDates[0])
  }
  // Pre-populate type if shared by all selected evals
  const uniqueTypes = chain(selectedEvaluations.value).map(e => get(e, 'evaluationType.id')).uniq().value()
  if (uniqueTypes.length === 1) {
    bulkUpdateOptions.value.evaluationType = get(selectedEvaluations.value, '0.evaluationType.id')
  }
}

const update = (fields, key) => {
  disableControls.value = true
  isLoading.value = true
  const evaluationIds = duplicatingEvaluationId.value ? [duplicatingEvaluationId.value] : selectedEvaluationIds.value
  const duplicatingEvaluationsCount = applyingAction.value.key === 'duplicate' ? evaluationIds.length : 0
  const selectedCourseNumbers = uniq(evaluations.value
    .filter(e => evaluationIds.includes(e.id))
    .map(e => e.courseNumber))
  const refresh = () => {
    return selectedCourseNumbers.length === 1
      ? departmentStore.refreshSection(selectedCourseNumbers[0], useContextStore().selectedTermId, duplicatingEvaluationsCount)
      : departmentStore.refreshAll()
  }
  updateEvaluations(
    department.value.id,
    key,
    evaluationIds,
    useContextStore().selectedTermId,
    fields
  ).then(
    response => {
      refresh().then(() => {
        const selectedRowCount = applyingAction.value.key === 'duplicate' ? ((response.length || 0) / 2) : (response.length || 0)
        const target = `${selectedRowCount} ${selectedRowCount === 1 ? 'row' : 'rows'}`
        departmentStore.deselectAllEvaluations()
        alertScreenReader(`${applyingAction.value.completedText} ${target}`)
        putFocusNextTick(duplicatingEvaluationId.value ? `evaluation-menu-btn-${duplicatingEvaluationId.value}` : `apply-course-action-btn-${key}`, {scroll: false})
        reset()
      }).finally(() => {
        isApplying.value = false
        disableControls.value = false
      })
    },
    error => {
      departmentStore.showErrorDialog(get(error, 'response.data.message', 'An unknown error occurred.'))
      disableControls.value = false
      isApplying.value = false
      isLoading.value = false
    }
  )
}

const validateAndUpdate = key => {
  let valid = true
  const evaluationIds = duplicatingEvaluationId.value ? [duplicatingEvaluationId.value] : selectedEvaluationIds.value
  const target = `${evaluationIds.length || 0} ${evaluationIds.length === 1 ? 'row' : 'rows'}`
  applyingAction.value = courseActions.value[key]
  isApplying.value = true
  alertScreenReader(`${applyingAction.value.inProgressText} ${target}`)

  const fields = getEvaluationFieldsForUpdate(key)
  if (key === 'duplicate') {
    valid = validateDuplicable(evaluationIds, fields)
  } else if (key === 'confirm' || (key === 'edit' && bulkUpdateOptions.value.evaluationStatus === 'confirmed')) {
    valid = validateConfirmable(evaluationIds, fields)
  }
  if (valid) {
    update(fields, key)
  } else {
    isApplying.value = false
  }
}
</script>

<style scoped>
.evaluation-confirm-btn {
  min-width: 7.6em
}
.evaluation-duplicate-btn {
  min-width: 5.45em
}
.evaluation-edit-btn {
  min-width: 4.02em
}
.evaluation-ignore-btn {
  min-width: 4.05em
}
.evaluation-review-btn {
  min-width: 7.84em
}
.evaluation-unmark-btn {
  min-width: 4.65em
}
.pipe-separator {
  font-size: 20px;
  padding: 2px 2px 0 2px;
}
</style>

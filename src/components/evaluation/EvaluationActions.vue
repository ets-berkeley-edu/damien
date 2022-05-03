<template>
  <v-row>
    <v-col cols="12" sm="6">
      <div class="d-flex flex-row flex-grow-1 align-baseline mb-4">
        <select
          id="select-course-actions"
          v-model="selectedCourseAction"
          aria-labelledby="action-option-label"
          class="native-select-override"
          :class="$vuetify.theme.dark ? 'dark' : 'light'"
          :disabled="disableControls"
        >
          <option
            id="action-option-label"
            :key="0"
            disabled
            :value="undefined"
          >
            Course Actions
          </option>
          <option
            v-for="(action, index) in courseActions"
            :id="`action-option-${action.value}`"
            :key="index + 1"
            :value="action.value"
          >
            {{ action.text }}
          </option>
        </select>
        <v-btn
          id="apply-course-action-btn"
          class="mx-2"
          color="secondary"
          :disabled="disableControls || !selectedCourseAction || !evaluationIds.length || (bulkUpdateOptions.evalDatesEnabled && !bulkUpdateOptions.startDate)"
          @click="applyCourseAction"
          @keypress.enter.prevent="applyCourseAction"
        >
          Apply
        </v-btn>
      </div>
      <div v-if="selectedCourseAction === 'duplicate'" class="mb-4">
        <div class="d-flex align-center mt-2">
          <PersonLookup
            id="input-instructor-lookup-autocomplete"
            :instructor-lookup="true"
            placeholder="Instructor name or UID"
            :on-select-result="selectInstructor"
            solo
          />
        </div>
        <v-checkbox
          v-model="bulkUpdateOptions.midtermFormEnabled"
          class="text-nowrap"
          color="tertiary"
          :disabled="disableControls"
          hide-details="auto"
          label="Use midterm department forms"
        />
        <div class="d-flex align-center mt-2">
          <v-checkbox
            v-model="bulkUpdateOptions.evalDatesEnabled"
            class="text-nowrap mt-0 pt-0"
            color="tertiary"
            :disabled="disableControls"
            label="Set evaluation start date:"
            hide-details="auto"
          />
          <c-date-picker
            v-model="bulkUpdateOptions.startDate"
            class="mx-3"
            :min-date="$moment($config.currentTermDates.begin).toDate()"
            :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
            title-position="left"
          >
            <template v-slot="{ inputValue, inputEvents }">
              <input
                class="input-override my-0"
                :class="$vuetify.theme.dark ? 'dark' : 'light'"
                :disabled="disableControls"
                :value="inputValue"
                v-on="inputEvents"
              />
            </template>
          </c-date-picker>
        </div>
      </div>
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
        </v-card>
      </v-dialog>
    </v-col>
    <v-col cols="12" sm="6">
      <div class="d-flex flex-grow-1 align-baseline justify-end mb-4">
        <v-btn
          v-if="!isAddingSection"
          id="add-course-section-btn"
          class="text-capitalize pl-2 mt-1"
          color="tertiary"
          text
          @click="() => isAddingSection = true"
          @keypress.enter.prevent="() => isAddingSection = true"
        >
          <v-icon>mdi-plus-thick</v-icon>
          Add Course Section
        </v-btn>
        <AddCourseSection
          v-if="isAddingSection"
          id="add-course-section"
          :evaluations="evaluations"
          :on-submit="addCourseSection"
          :on-cancel="cancelAddSection"
        />
      </div>
    </v-col>
  </v-row>
</template>

<script>
import {addSection, updateEvaluations} from '@/api/departments'
import AddCourseSection from '@/components/evaluation/AddCourseSection.vue'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'

export default {
  name: 'EvaluationActions',
  components: {
    AddCourseSection,
    PersonLookup
  },
  mixins: [Context, DepartmentEditSession],
  props: {
    afterApply: {
      required: true,
      type: Function
    },
    evaluationIds: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    bulkUpdateOptions: {
      evalDatesEnabled: false,
      midtermFormEnabled: false,
      startDate: null,
    },
    courseActions: [
      {'text': 'Mark for review', 'value': 'mark'},
      {'text': 'Mark as confirmed', 'value': 'confirm'},
      {'text': 'Unmark', 'value': 'unmark'},
      {'text': 'Duplicate', 'value': 'duplicate'},
      {'text': 'Ignore', 'value': 'ignore'}
    ],
    isAddingSection: false,
    instructor: null,
    selectedCourseAction: undefined
  }),
  watch: {
    selectedCourseAction(action) {
      if (action === 'duplicate') {
        this.$putFocusNextTick('input-instructor-lookup-autocomplete')
      }
    }
  },
  methods: {
    addCourseSection(courseNumber) {
      this.isAddingSection = false
      addSection(this.department.id, courseNumber).then(this.refresh(`Section ${courseNumber} added.`))
    },
    applyCourseAction() {
      let fields = null
      if (this.selectedCourseAction === 'duplicate') {
        fields = {
          instructorUid: this.$_.get(this.instructor, 'uid')
        }
        if (this.bulkUpdateOptions.midtermFormEnabled) {
          fields.midterm = 'true'
        }
        if (this.bulkUpdateOptions.evalDatesEnabled) {
          const duration = (this.$config.currentTermDates.begin + 77) > this.bulkUpdateOptions.startDate ? 13 : 20
          fields.endDate = this.$moment(this.bulkUpdateOptions.startDate).add(duration, 'days').format('YYYY-MM-DD')
        }
      }
      if (this.selectedCourseAction !== 'confirm' || this.validateConfirmable(this.evaluationIds, fields.departmentFormId, fields.evaluationTypeId)) {
        this.setDisableControls(true)
        updateEvaluations(
          this.department.id,
          this.selectedCourseAction,
          this.evaluationIds,
          fields
        ).then(() => this.afterApply(), error => this.showErrorDialog(error.response.data.message))
        .finally(() => this.setDisableControls(false))
      }
    },
    cancelAddSection() {
      this.isAddingSection = false
      this.alertScreenReader('Section lookup canceled.')
      this.$putFocusNextTick('add-course-section-btn')
    },
    selectInstructor(suggestion) {
      this.instructor = suggestion
    }
  }
}
</script>

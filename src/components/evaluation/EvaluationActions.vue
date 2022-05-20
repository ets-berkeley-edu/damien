<template>
  <div class="d-flex align-center">
    <div v-if="!isDuplicating" class="d-flex">
      <template v-for="(action, index) in courseActions">
        <v-btn
          :id="`apply-course-action-btn-${action.value}`"
          :key="index"
          class="text-capitalize text-nowrap px-2"
          :color="$vuetify.theme.dark ? 'tertiary' : 'secondary'"
          :disabled="disableControls || !allowEdits || !selectedEvaluationIds.length"
          text
          @click="action.apply(action.value)"
          @keypress.enter.prevent="action.apply(action.value)"
        >
          {{ action.text }}
        </v-btn>
        <v-divider
          v-if="action.value === 'ignore'"
          :key="index + 2"
          class="align-self-stretch separator ma-2"
          inset
          role="presentation"
          vertical
        ></v-divider>
      </template>
    </div>
    <div v-if="isDuplicating" class="ma-3 pl-4">
      <div class="d-flex align-center mt-2">
        <PersonLookup
          id="bulk-duplicate-instructor-lookup-autocomplete"
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
        <label
          for="bulk-duplicate-start-date"
          class="v-label"
          :class="$vuetify.theme.dark ? 'theme--dark' : 'theme--light'"
        >
          Evaluation start date:
        </label>
        <c-date-picker
          v-model="bulkUpdateOptions.startDate"
          class="mx-3"
          :min-date="$moment($config.currentTermDates.begin).toDate()"
          :max-date="$moment($config.currentTermDates.end).subtract(20, 'days').toDate()"
          title-position="left"
        >
          <template v-slot="{ inputValue, inputEvents }">
            <input
              id="bulk-duplicate-start-date"
              class="datepicker-input input-override my-0"
              :class="$vuetify.theme.dark ? 'dark' : 'light'"
              :disabled="disableControls"
              maxlength="10"
              minlength="10"
              :value="inputValue"
              v-on="inputEvents"
            />
          </template>
        </c-date-picker>
      </div>
      <v-btn
        id="apply-course-action-btn"
        class="mt-2 mr-2"
        color="secondary"
        :disabled="disableControls || !allowEdits || $_.isEmpty(selectedEvaluationIds)"
        @click="applyAction('duplicate')"
        @keypress.enter.prevent="applyAction('duplicate')"
      >
        Apply
      </v-btn>
      <v-btn
        id="cancel-duplicate-btn"
        class="mt-2 mr-2"
        :disabled="disableControls"
        @click="cancelDuplicate"
        @keypress.enter.prevent="cancelDuplicate"
      >
        Cancel
      </v-btn>
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
  </div>
</template>

<script>
import {updateEvaluations} from '@/api/departments'
import Context from '@/mixins/Context'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import PersonLookup from '@/components/admin/PersonLookup'
import Util from '@/mixins/Util'

export default {
  name: 'EvaluationActions',
  components: {
    PersonLookup
  },
  mixins: [Context, DepartmentEditSession, Util],
  data: () => ({
    bulkUpdateOptions: {
      midtermFormEnabled: false,
      startDate: null,
    },
    courseActions: [],
    isAddingSection: false,
    instructor: null,
    isDuplicating: false
  }),
  created() {
    this.courseActions = [
      {'text': 'Mark for review', 'value': 'mark', 'apply': this.applyAction},
      {'text': 'Mark as confirmed', 'value': 'confirm', 'apply': this.applyAction},
      {'text': 'Unmark', 'value': 'unmark', 'apply': this.applyAction},
      {'text': 'Ignore', 'value': 'ignore', 'apply': this.applyAction},
      {'text': 'Duplicate', 'value': 'duplicate', 'apply': this.showDuplicateOptions}
    ]
  },
  computed: {
    allowEdits() {
      return this.$currentUser.isAdmin || !this.isSelectedTermLocked
    }
  },
  methods: {
    afterApply(action) {
      /* TODO: a more informative screen reader alert plus a visual indication of the affected row(s) */
      this.isDuplicating = false
      this.refreshAll().then(() => {
        this.alertScreenReader('Success')
        this.$putFocusNextTick(`apply-course-action-btn-${action}`)
      })

    },
    applyAction(action) {
      let fields = null
      if (action === 'duplicate') {
        fields = {
          instructorUid: this.$_.get(this.instructor, 'uid')
        }
        if (this.bulkUpdateOptions.midtermFormEnabled) {
          fields.midterm = 'true'
        }
        if (this.bulkUpdateOptions.startDate) {
          fields.startDate = this.$moment(this.bulkUpdateOptions.startDate).format('YYYY-MM-DD')
        }
      }
      if (action !== 'confirm' || this.validateConfirmable(this.selectedEvaluationIds, true, true)) {
        this.setDisableControls(true)
        updateEvaluations(
          this.department.id,
          action,
          this.selectedEvaluationIds,
          fields
        ).then(data => this.afterApply(action, data), error => this.showErrorDialog(error.response.data.message))
        .finally(() => this.setDisableControls(false))
      }
    },
    cancelDuplicate() {
      this.isDuplicating = false
      this.$putFocusNextTick('apply-course-action-btn-duplicate')
    },
    selectInstructor(suggestion) {
      this.instructor = suggestion
    },
    showDuplicateOptions() {
      this.isDuplicating = true
      this.$putFocusNextTick('bulk-duplicate-instructor-lookup-autocomplete')
    }
  }
}
</script>

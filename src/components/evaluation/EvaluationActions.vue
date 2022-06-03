<template>
  <div class="d-flex align-center">
    <div v-if="!isDuplicating" class="d-flex">
      <template v-for="(action, index) in courseActions">
        <v-btn
          :id="`apply-course-action-btn-${action.value}`"
          :key="index"
          class="text-capitalize text-nowrap px-2"
          :color="$vuetify.theme.dark ? 'tertiary' : 'secondary'"
          :disabled="disableControls || !allowEdits || !selectedEvaluationIds.length || isLoading || isInvalidAction(action)"
          text
          @click.stop="action.apply(action.value)"
          @keypress.enter.prevent="action.apply(action.value)"
        >
          <span v-if="!isLoading">{{ action.text }}</span>
        </v-btn>
        <v-divider
          v-if="action.value === 'ignore' && !isLoading"
          :key="index + 2"
          class="align-self-stretch primary--text separator ma-2"
          inset
          role="presentation"
          vertical
        ></v-divider>
      </template>
      <v-progress-circular
        v-if="isLoading"
        :indeterminate="true"
        rotate="5"
        size="20"
        width="3"
        color="tertiary"
        class="ma-2 pl-5"
      ></v-progress-circular>
    </div>
    <v-dialog
      id="duplicate-row-dialog"
      v-model="isDuplicating"
      aria-labelledby="duplicate-row-dialog-title"
      class="overflow-y-visible"
      width="500"
    >
      <v-card>
        <v-card-title id="duplicate-row-dialog-title" tabindex="-1">Duplicate</v-card-title>
        <v-card-text>
          <div class="d-flex align-center mt-2">
            <PersonLookup
              id="bulk-duplicate-instructor-lookup-autocomplete"
              :disabled="disableControls"
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
              :min-date="$moment($config.termDates.valid.begin).toDate()"
              :max-date="$moment($config.termDates.valid.end).subtract(13, 'days').toDate()"
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
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <div class="d-flex pa-2">
            <v-btn
              id="apply-course-action-btn"
              class="mt-2 mr-2"
              color="secondary"
              :disabled="disableControls || !allowEdits || $_.isEmpty(selectedEvaluationIds)"
              @click="applyAction('duplicate')"
              @keypress.enter.prevent="applyAction('duplicate')"
            >
              <span v-if="!isLoading">Apply</span>
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
        </v-card-actions>
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
    isDuplicating: false,
    isLoading: false
  }),
  created() {
    this.courseActions = [
      {'text': 'Mark for review', 'value': 'mark', 'status': 'review', 'apply': this.applyAction},
      {'text': 'Mark as confirmed', 'value': 'confirm', 'status': 'confirmed', 'apply': this.applyAction},
      {'text': 'Unmark', 'value': 'unmark', 'status': null, 'apply': this.applyAction},
      {'text': 'Ignore', 'value': 'ignore', 'status': 'ignore', 'apply': this.applyAction},
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
      this.isLoading = true
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
        this.isLoading = true
        this.setDisableControls(true)

        updateEvaluations(
          this.department.id,
          action,
          this.selectedEvaluationIds,
          fields
        ).then(data => this.afterApply(action, data), error => this.showErrorDialog(error.response.data.message))
        .finally(() => this.setDisableControls(false),
          this.isLoading = false
        )
      }
    },
    cancelDuplicate() {
      this.isDuplicating = false
      if (this.bulkUpdateOptions.startDate) {
        this.bulkUpdateOptions.startDate = null
      }
      this.alertScreenReader('Canceled.')
      this.$putFocusNextTick('apply-course-action-btn-duplicate')
    },
    reset() {
      this.bulkUpdateOptions = {
        midtermFormEnabled: false,
        startDate: null,
      }
      this.instructor = null,
      this.isDuplicating = false,
      this.isLoading = false
    },
    selectInstructor(suggestion) {
      this.instructor = suggestion
    },
    showDuplicateOptions() {
      this.isDuplicating = true

      /* Find all the dates from the selected evals, format them, then find if they're unique*/
      const uniqueStartDates = this.evaluations
                    .filter(ev => this.selectedEvaluationIds.includes(ev.id))
                    .map(ev => new Date(ev.startDate).toDateString())
                    .filter((date, idx, val) => val.indexOf(date) === idx)

      if (uniqueStartDates.length === 1) {
        this.bulkUpdateOptions.startDate = new Date(uniqueStartDates[0])
      }
      
      
      this.$putFocusNextTick('bulk-duplicate-instructor-lookup-autocomplete')
    },
    isInvalidAction(action) {
      const uniqueStatuses = this.$_.uniq(this.evaluations
                  .filter(e => this.selectedEvaluationIds.includes(e.id))
                  .map(e => e.status))

      return (uniqueStatuses.length === 1 && uniqueStatuses[0] === action.status)
    }
  }
}
</script>

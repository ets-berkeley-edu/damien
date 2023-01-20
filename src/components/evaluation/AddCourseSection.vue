<template>
  <div class="d-flex align-baseline add-course-section">
    <v-btn
      v-if="!isAddingSection"
      id="add-course-section-btn"
      class="text-capitalize pl-2 mr-3 mt-1"
      color="tertiary"
      :disabled="!allowEdits"
      text
      @click="() => isAddingSection = true"
      @keypress.enter.prevent="() => isAddingSection = true"
    >
      <v-icon>mdi-plus-thick</v-icon>
      Add Course Section
    </v-btn>
    <div v-if="isAddingSection" class="full-width px-4">
      <div v-if="!section">
        <v-form>
          <label for="lookup-course-number-input" class="form-label">
            Course Number
          </label>
          <v-text-field
            id="lookup-course-number-input"
            ref="lookupCourseNumberInput"
            v-model="courseNumber"
            class="mt-1"
            color="tertiary"
            :error-messages="errorMessage"
            maxlength="5"
            :rules="[rules.courseNumber, rules.notPresent]"
            dense
            outlined
            required
            @keypress.enter.prevent="lookupSection"
            @keydown.esc="onCancel"
          >
            <template #message="{message}">
              <div :id="sectionError ? 'section-not-found-error' : 'lookup-course-number-error'" class="text-condensed">
                <v-icon v-if="sectionError" color="error" small>mdi-alert</v-icon>
                {{ message }}
              </div>
            </template>
          </v-text-field>
          <div>
            <v-btn
              id="lookup-course-number-submit"
              class="text-capitalize mr-2 mb-1"
              color="secondary"
              elevation="2"
              :disabled="!courseNumberReady"
              @click="lookupSection"
              @keypress.enter.prevent="lookupSection"
            >
              Look Up
            </v-btn>
            <v-btn
              id="lookup-course-number-cancel"
              class="text-capitalize ml-1 mb-1"
              elevation="2"
              outlined
              text
              @click="onCancel"
              @keypress.enter.prevent="onCancel"
            >
              Cancel
            </v-btn>
          </div>
        </v-form>
      </div>
      <div v-if="section">
        <h3 id="add-section-title">
          {{ section.subjectArea }}
          {{ section.catalogId }}
          {{ section.instructionFormat }}
          {{ section.sectionNumber }}
        </h3>
        <div id="add-section-course-number" class="mt-1">Course number {{ section.courseNumber }}</div>
        <div id="add-section-course-title" class="mt-1 mb-3">{{ section.courseTitle }}</div>
        <div>
          <v-btn
            id="add-course-section-submit"
            class="text-capitalize mr-2 mb-1"
            color="secondary"
            :disabled="disableControls"
            elevation="2"
            @click="onSubmit(section.courseNumber)"
            @keypress.enter.prevent="onSubmit(section.courseNumber)"
          >
            Confirm
          </v-btn>
          <v-btn
            id="add-course-section-cancel"
            class="text-capitalize ml-1 mb-1"
            elevation="2"
            outlined
            text
            @click="onCancel"
            @keypress.enter.prevent="onCancel"
          >
            Cancel
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {getSection} from '@/api/sections'
import Context from '@/mixins/Context.vue'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'

export default {
  name: 'AddCourseSection',
  mixins: [Context, DepartmentEditSession],
  props: {
    allowEdits: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    courseNumber: null,
    errorMessage: '',
    isAddingSection: false,
    rules: {},
    section: null,
    sectionError: false
  }),
  watch: {
    courseNumber() {
      this.errorMessage = null
      this.sectionError = false
    },
    isAddingSection(isAddingSection) {
      if (isAddingSection) {
        this.alertScreenReader('Add course section form is ready.')
        this.$putFocusNextTick('lookup-course-number-input')
      }
    }
  },
  computed: {
    courseNumberReady() {
      return this.courseNumber && /^\d{5}/.test(this.courseNumber) && (this.rules.notPresent(this.courseNumber) === true)
    }
  },
  created() {
    this.rules = {
      courseNumber: value => !value || /^\d+$/.test(value) || 'Invalid course number.',
      notPresent: value => !this.$_.find(this.evaluations, {courseNumber: value}) || `Course number ${value} already present on page.`
    }
  },
  methods: {
    lookupSection() {
      this.errorMessage = null
      if (this.$refs.lookupCourseNumberInput.validate()) {
        getSection(this.courseNumber, this.selectedTermId).then(data => {
          this.alertScreenReader(`Section ${this.courseNumber} found.`)
          this.courseNumber = null
          this.section = data
          this.$putFocusNextTick('add-section-title')
        }, () => {
          this.sectionError = true
          this.errorMessage = `Section ${this.courseNumber} not found.`
          this.alertScreenReader(this.errorMessage)
          this.$putFocusNextTick('lookup-course-number-input')
        })
      }
    },
    onCancel() {
      this.courseNumber = null
      this.errorMessage = null
      if (this.section) {
        this.section = null
        this.alertScreenReader('Canceled. Add course section form is ready.')
        this.$putFocusNextTick('lookup-course-number-input')
      } else {
        this.isAddingSection = false
        this.alertScreenReader('Section lookup canceled.')
        this.$putFocusNextTick('add-course-section-btn')
      }
    },
    onSubmit(courseNumber) {
      this.alertScreenReader(`Adding section ${courseNumber}.`)
      this.addSection({
          sectionId: courseNumber,
          termId: this.selectedTermId
        }).then(() => {
        this.isAddingSection = false
        this.courseNumber = null
        this.errorMessage = null
        this.section = null
        this.alertScreenReader(`Section ${courseNumber} added.`)
      }, error => this.showErrorDialog(error.response.data.message))
      .finally(() => this.setDisableControls(false))
    }
  }
}
</script>

<style scoped>
.add-course-section {
  max-width: 300px;
  justify-content: flex-end;
  margin-left: auto;
}
.form-label {
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.full-width {
  width: 100%;
  width: -moz-available;
  width: -webkit-fill-available;
  width: stretch;
}
</style>

<template>
  <v-form class="pa-3 mb-4">
    <div v-if="!section">
      <div v-if="sectionError" class="d-flex justify-start mb-3">
        <div class="pr-2">
          <v-icon color="red">mdi-alert</v-icon>
        </div>
        <div id="section-not-found-error">
          {{ sectionError }}
        </div>
      </div>
      <v-form>
        <label for="lookup-course-number-input" class="form-label">
          Course Number
        </label>
        <v-text-field
          id="lookup-course-number-input"
          v-model="courseNumber"
          class="mt-1"
          maxlength="5"
          :rules="[rules.courseNumber, rules.notPresent]"
          dense
          outlined
          required
        ></v-text-field>
        <v-btn
          id="lookup-course-number-submit"
          class="text-capitalize mr-2"
          color="secondary"
          elevation="2"
          :disabled="!courseNumberReady"
          @click="lookupSection"
        >
          Look Up
        </v-btn>
        <v-btn
          id="lookup-course-number-cancel"
          class="text-capitalize ml-1"
          color="secondary"
          elevation="2"
          outlined
          text
          @click="onCancel"
        >
          Cancel
        </v-btn>
      </v-form>
    </div>
    <div v-if="section">
      <h3 id="add-section-title">
        {{ section.subjectArea }} 
        {{ section.catalogId }}
        {{ section.instructionFormat }}
        {{ section.sectionNumber }}
      </h3>
      <div class="mt-2 mb-2">Course number {{ section.courseNumber }}</div>
      <div class="mt-2 mb-4">{{ section.courseTitle }}</div>
      <v-btn
        id="add-course-section-submit"
        class="text-capitalize mr-2"
        color="secondary"
        elevation="2"
        @click="onSubmit(section.courseNumber)"
      >
        Confirm
      </v-btn>
      <v-btn
        id="add-course-section-cancel"
        class="text-capitalize ml-1"
        color="secondary"
        elevation="2"
        outlined
        text
        @click="cancelSection"
      >
        Cancel
      </v-btn>
    </div>
  </v-form>
</template>

<script>
import {getSection} from '@/api/sections'
import Context from '@/mixins/Context.vue'

export default {
  name: 'AddCourseSection',
  mixins: [Context],
  props: {
    evaluations: {
      required: true,
      type: Array
    },
    onSubmit: {
      required: true,
      type: Function
    },
    onCancel: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    courseNumber: null,
    rules: {},
    section: null,
    sectionError: null
  }),
  computed: {
    courseNumberReady() {
      return this.courseNumber && /^\d{5}/.test(this.courseNumber) && (this.rules.notPresent(this.courseNumber) === true)
    }
  },
  created() {
    this.rules = {
      courseNumber: value => /^\d+$/.test(value) || 'Invalid course number.',
      notPresent: value => !this.$_.find(this.evaluations, {courseNumber: value}) || `Course number ${value} already present on page.`
    }
    this.alertScreenReader('Add course section form is ready.')
  },
  methods: {
    cancelSection() {
      this.section = null
      this.alertScreenReader('Canceled. Add course section form is ready.')
    },
    lookupSection() {
      getSection(this.courseNumber).then(data => {
        this.alertScreenReader(`Section ${this.courseNumber} found.`)
        this.courseNumber = null
        this.section = data
        this.sectionError = null
        this.$putFocusNextTick('add-section-title')
      }, () => {
        this.sectionError = `Section ${this.courseNumber} not found.`
        this.courseNumber = null
        this.alertScreenReader(this.sectionError)    
      })
    }
  }
}
</script>

<style scoped>
.form-label {
  font-size: 15px;
  font-weight: 700;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
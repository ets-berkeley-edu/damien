<template>
  <div v-if="!loading">
    <v-row>
      <v-col cols="12" md="7" class="d-flex justify-start">
        <h1>{{ department.deptName }} ({{ $_.keys(department.catalogListings).join(', ') }}) - {{ $_.get(selectedTerm, 'name') }}</h1>
      </v-col>
      <v-col
        v-if="$currentUser.isAdmin"
        cols="12"
        md="5"
        class="d-flex justify-end"
      >
        <label id="select-term-label" for="select-term" class="pa-3">
          Previous terms:
        </label>
        <v-select
          id="select-term"
          v-model="selectedTermId"
          :disabled="disableControls"
          item-text="name"
          item-value="id"
          :items="availableTerms"
          label="Select..."
          solo
          @change="refresh"
        >
          <span :id="`term-option-${data.item.id}`" slot="item" slot-scope="data">{{ data.item.name }}</span>
        </v-select>
        <v-btn class="ma-2" :disabled="!selectedTerm" @click="refresh">Apply</v-btn>
      </v-col>
    </v-row>
    <v-container v-if="$currentUser.isAdmin" class="mx-0 px-0 pb-6">
      <v-row justify="start">
        <v-col cols="12" md="4">
          <h2 class="pb-1 px-2">Department Contacts</h2>
          <DepartmentContact
            v-for="(contact, index) in contacts"
            :key="contact.id"
            :contact="contact"
            :index="index"
          />
          <v-btn
            v-if="!isAddingContact"
            id="add-dept-contact-btn"
            class="text-capitalize pl-2 mt-1"
            color="secondary"
            text
            @click="() => isAddingContact = true"
          >
            <v-icon>mdi-plus-thick</v-icon>
            Add Contact
          </v-btn>
          <EditDepartmentContact
            v-if="isAddingContact"
            :id="`add-department-contact`"
            :after-save="afterSaveContact"
            :on-cancel="onCancelAddContact"
          />
        </v-col>
        <v-col cols="12" md="8"><DepartmentNote /></v-col>
      </v-row>
    </v-container>
    <v-row>
      <v-col cols="12" md="4">
        <v-select
          id="select-term"
          v-model="selectedCourseAction"
          item-text="text"
          item-value="value"
          :items="courseActions"
          label="Course Actions"
          solo
        >
        </v-select>
      </v-col>
      <v-col cols="12" md="4">
        <v-btn @click="applyCourseAction">
          Apply
        </v-btn>
      </v-col>
      <v-col cols="12" md="4">
        <v-btn
          v-if="!isAddingSection"
          id="add-course-section-btn"
          class="text-capitalize pl-2 mt-1"
          color="secondary"
          text
          @click="() => isAddingSection = true"
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
      </v-col>
    </v-row>
    <v-card outlined class="elevation-1">
      <EvaluationTable :evaluations="evaluations" :update-evaluation="updateEvaluation" />
    </v-card>
  </div>
</template>

<script>
import {addSection, updateEvaluations} from '@/api/departments'
import AddCourseSection from '@/components/evaluation/AddCourseSection.vue'
import Context from '@/mixins/Context.vue'
import DepartmentContact from '@/components/admin/DepartmentContact'
import DepartmentEditSession from '@/mixins/DepartmentEditSession'
import DepartmentNote from '@/components/admin/DepartmentNote'
import EditDepartmentContact from '@/components/admin/EditDepartmentContact'
import EvaluationTable from '@/components/evaluation/EvaluationTable'

export default {
  name: 'Department',
  components: {AddCourseSection, DepartmentContact, DepartmentNote, EditDepartmentContact, EvaluationTable},
  mixins: [Context, DepartmentEditSession],
  data: () => ({
    availableTerms: undefined,
    courseActions: [
      {'text': 'Mark for review', 'value': 'mark'},
      {'text': 'Mark as confirmed', 'value': 'confirm'},
      {'text': 'Duplicate', 'value': 'duplicate'}
    ],
    department: {},
    evaluations: [],
    isAddingContact: false,
    isAddingSection: false,
    selectedCourseAction: undefined,
    selectedTermId: undefined
  }),
  computed: {
    selectedEvaluationIds() {
      return this.$_.reduce(this.evaluations, (ids, e) => {
        if (e.isSelected) {
          ids.push(e.id)
        }
        return ids
      }, [])
    }
  },
  created() {
    this.availableTerms = this.$config.availableTerms
    this.selectedTermId = this.$config.currentTermId
    this.refresh()
  },
  methods: {
    addCourseSection(courseNumber) {
      this.isAddingSection = false
      addSection(this.department.id, courseNumber).then(this.refresh(`Section ${courseNumber} added.`))
    },
    afterSaveContact() {
      this.isAddingContact = false
      this.alertScreenReader('Contact saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    applyCourseAction() {
      updateEvaluations(this.department.id, this.selectedCourseAction, this.selectedEvaluationIds).then(this.refresh)
    },
    cancelAddSection() {
      this.isAddingSection = false
      this.alertScreenReader('Section lookup canceled.')
    },
    onCancelAddContact() {
      this.isAddingContact = false
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$putFocusNextTick('add-dept-contact-btn')
    },
    refresh(screenreaderAlert) {
      this.$loading()
      const departmentId = this.$_.get(this.$route, 'params.departmentId')
      const termId = this.selectedTermId
      this.init({departmentId, termId}).then(department => {
        this.department = department
        this.evaluations = department.evaluations
        this.$_.each(this.evaluations, e => e.isSelected = false)
        this.$ready(department.deptName, screenreaderAlert)
      })
    },
    updateEvaluation(evaluationId, fields) {
      updateEvaluations(this.department.id, 'edit', [evaluationId], fields).then(this.refresh)
    }
  }
}
</script>

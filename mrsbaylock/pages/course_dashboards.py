"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""
import copy
import time

from flask import current_app as app
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.action_chains import ActionChains as Act
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboards(DamienPages):

    COURSE_ACTIONS_SELECT = (By.XPATH, '//label[text()="Course Actions"]/following-sibling::div')
    USE_MIDTERM_FORM_CBX = (By.XPATH, '//label[text()="Use midterm department forms"]/preceding-sibling::div/input')
    USE_END_DATE_CBX = (By.XPATH, '//label[text()="Set end date:"]/preceding-sibling::div/input')
    USE_END_DATE_INPUT = (By.XPATH, '//input[@type="date"]')
    ACTION_APPLY_BUTTON = (By.XPATH, '(//button[contains(., "Apply")])[2]')

    def set_row_status(self, evaluation, status):
        app.logger.info(f'Setting CCN {evaluation.ccn} to {status}')
        self.click_eval_checkbox(evaluation)
        self.wait_for_element_and_click(CourseDashboards.COURSE_ACTIONS_SELECT)
        self.click_menu_option(status)
        self.wait_for_element_and_click(CourseDashboards.ACTION_APPLY_BUTTON)

    def mark_for_review(self, evaluation):
        self.set_row_status(evaluation, 'Mark for review')
        evaluation.status = EvaluationStatus.FOR_REVIEW

    def mark_as_confirmed(self, evaluation):
        self.set_row_status(evaluation, 'Mark as confirmed')
        evaluation.status = EvaluationStatus.CONFIRMED

    def ignore(self, evaluation):
        self.set_row_status(evaluation, 'Ignore')
        evaluation.status = EvaluationStatus.IGNORED

    def unmark(self, evaluation):
        self.set_row_status(evaluation, 'Unmark')
        evaluation.status = None

    def duplicate_section(self, evaluation, evaluations, midterm=None, end_date=None):
        app.logger.info(f'Duplicating row for CCN {evaluation.ccn}')
        self.click_eval_checkbox(evaluation)
        self.wait_for_element_and_click(CourseDashboards.COURSE_ACTIONS_SELECT)
        self.click_menu_option('Duplicate')
        if midterm:
            self.wait_for_page_and_click_js(CourseDashboards.USE_MIDTERM_FORM_CBX)
        if end_date:
            s = end_date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting end date {s}')
            self.wait_for_page_and_click_js(CourseDashboards.USE_END_DATE_CBX)
            self.wait_for_element_and_type(CourseDashboards.USE_END_DATE_INPUT, s)
        self.wait_for_element_and_click(CourseDashboards.ACTION_APPLY_BUTTON)
        dupe = copy.deepcopy(evaluation)
        if midterm:
            dupe.dept_form = f'{evaluation.dept_form}_MID'
        if end_date:
            dupe.end_date = end_date
        evaluations.append(dupe)
        return dupe

    FILTER_UNMARKED = (By.ID, 'evaluations-filter-unmarked')
    FILTER_REVIEW = (By.ID, 'evaluations-filter-review')
    FILTER_CONFIRMED = (By.ID, 'evaluations-filter-confirmed')
    FILTER_IGNORE = (By.ID, 'evaluations-filter-ignore')

    def select_filter(self, filter_loc):
        if 'filter-inactive' in self.element(filter_loc).attribute('class'):
            self.wait_for_element_and_click(filter_loc)
            time.sleep(1)

    def deselect_filter(self, filter_loc):
        if 'filter-inactive' not in self.element(filter_loc).attribute('class'):
            self.wait_for_element_and_click(filter_loc)
            time.sleep(1)

    def select_unmarked_filter(self):
        app.logger.info('Selecting unmarked filter')
        self.select_filter(CourseDashboards.FILTER_UNMARKED)

    def deselect_unmarked_filter(self):
        app.logger.info('Deselecting unmarked filter')
        self.deselect_filter(CourseDashboards.FILTER_UNMARKED)

    def select_review_filter(self):
        app.logger.info('Selecting to-review filter')
        self.select_filter(CourseDashboards.FILTER_REVIEW)

    def deselect_review_filter(self):
        app.logger.info('Deselecting to-review filter')
        self.deselect_filter(CourseDashboards.FILTER_REVIEW)

    def select_confirmed_filter(self):
        app.logger.info('Selecting confirmed filter')
        self.select_filter(CourseDashboards.FILTER_CONFIRMED)

    def deselect_confirmed_filter(self):
        app.logger.info('Selecting confirmed filter')
        self.deselect_filter(CourseDashboards.FILTER_CONFIRMED)

    def select_ignored_filter(self):
        app.logger.info('Selecting ignored filter')
        self.select_filter(CourseDashboards.FILTER_IGNORE)

    def deselect_ignored_filter(self):
        app.logger.info('Selecting ignored filter')
        self.deselect_filter(CourseDashboards.FILTER_IGNORE)

    ADD_SECTION_BUTTON = (By.ID, 'add-course-section-btn')
    SECTION_LOOKUP_INPUT = (By.ID, 'lookup-course-number-input')
    SECTION_LOOKUP_BUTTON = (By.ID, 'lookup-course-number-submit')
    SECTION_LOOKUP_CANCEL_BUTTON = (By.ID, 'lookup-course-number-cancel')
    INVALID_SECTION_MSG = (By.XPATH, '//div[text()="Invalid course number."]')
    DUPE_SECTION_MSG = (By.XPATH, '//div[@class="v-messages__message" and contains(., "already present on page.")]')
    SECTION_NOT_FOUND_MSG = (By.ID, 'section-not-found-error')
    FOUND_SECTION_CODE = (By.ID, 'add-section-title')
    FOUND_SECTION_CCN = (By.XPATH, '//h3[@id="add-section-title"]/following-sibling::div[1]')
    FOUND_SECTION_TITLE = (By.XPATH, '//h3[@id="add-section-title"]/following-sibling::div[2]')
    ADD_SECTION_CONFIRM_BUTTON = (By.ID, 'add-course-section-submit')
    ADD_SECTION_CANCEL_BUTTON = (By.ID, 'add-course-section-cancel')

    def click_add_section(self):
        app.logger.info('Clicking the add-section button')
        self.wait_for_element_and_click(CourseDashboards.ADD_SECTION_BUTTON)

    def enter_section(self, ccn):
        app.logger.info(f'Looking up CCN {ccn}')
        self.wait_for_element_and_type(CourseDashboards.SECTION_LOOKUP_INPUT, ccn)

    def look_up_section(self, ccn):
        self.enter_section(ccn)
        self.wait_for_element_and_click(CourseDashboards.SECTION_LOOKUP_BUTTON)

    def click_cancel_lookup_section(self):
        self.wait_for_element_and_click(CourseDashboards.SECTION_LOOKUP_CANCEL_BUTTON)

    def click_confirm_add_section(self):
        app.logger.info('Clicking the confirm button to add a section')
        self.wait_for_element_and_click(CourseDashboards.ADD_SECTION_CONFIRM_BUTTON)

    def click_cancel_add_section(self):
        app.logger.info('Clicking the cancel button for adding a section')
        self.wait_for_element_and_click(CourseDashboards.ADD_SECTION_CANCEL_BUTTON)

    EVALUATION_ROW = (By.XPATH, '//tr[contains(@class, "evaluation-row")]')
    EVAL_CHANGE_INSTR_BUTTON = (By.XPATH, '//button[contains(@id, "-change-instructor")]')
    EVAL_CHANGE_DEPT_FORM_INPUT = (By.XPATH, '//input[@id="select-department-form"]/..')
    EVAL_CHANGE_EVAL_TYPE_INPUT = (By.XPATH, '//input[@id="select-evaluation-type"]/..')
    EVAL_CHANGE_OPTION_LIST = (By.XPATH, '//div[@role="listbox"]')
    EVAL_CHANGE_START_DATE_INPUT = (By.XPATH, '(//input[@type="date"])[1]')
    EVAL_CHANGE_END_DATE_INPUT = (By.XPATH, '(//input[@type="date"])[2]')

    @staticmethod
    def eval_row_xpath(evaluation):
        uid = f'[contains(., "{evaluation.instructor.uid}")]' if evaluation.instructor.uid else ''
        return f'//tr[contains(., "{evaluation.ccn}")]{uid}'

    def wait_for_eval_rows(self):
        time.sleep(1)
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_all_elements_located(CourseDashboards.EVALUATION_ROW),
        )

    def visible_eval_identifiers(self):
        self.wait_for_eval_rows()
        time.sleep(1)
        identifiers = []
        for index, value in enumerate(self.elements(CourseDashboards.EVALUATION_ROW)):
            cell = self.element((By.XPATH, f'//tr[contains(@class, "evaluation-row")][{index + 1}]/td[2]'))
            idx = cell.get_attribute('id').split('-')[1]
            ccn = self.element((By.ID, f'evaluation-{idx}-courseNumber')).text.strip().split('\n')[0]
            uid_loc = (By.XPATH, f'//td[@id="evaluation-{idx}-instructor"]/div')
            uid = ''
            if self.is_present(uid_loc):
                uid = self.element(uid_loc).text.strip().split()[-1].replace('(', '').replace(')', '')
            e_type = self.element((By.ID, f'evaluation-{idx}-evaluationType')).text.strip()
            identifiers.append(f'{ccn}-{uid}-{e_type}')
        return identifiers

    def click_eval_checkbox(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//input[contains(@id, "checkbox")]'
        self.wait_for_page_and_click_js((By.XPATH, xpath))

    def eval_status_el(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "status")]'
        return self.element((By.XPATH, xpath))

    def eval_status(self, evaluation):
        return self.eval_status_el(evaluation).text

    def eval_last_update(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "lastUpdated")]'
        return self.element((By.XPATH, xpath)).text

    def eval_ccn(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "courseNumber")]'
        return self.element((By.XPATH, xpath)).text.strip().split('\n')[0]

    def eval_course(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//div[contains(@id, "courseName")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_title(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//div[contains(@id, "courseTitle")]'
        return self.element((By.XPATH, xpath)).text

    def eval_instructor(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "instructor")]'
        return self.element((By.XPATH, xpath)).text

    def eval_dept_form(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "departmentForm")]/div'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_type(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "evaluationType")]/div'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_course_start(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "startDate")]/span'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_course_end(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "endDate")]/span'
        return self.element((By.XPATH, xpath)).text.strip()

    def click_edit_evaluation(self, evaluation):
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_element_located((By.XPATH, f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "status")]')),
        )
        self.mouseover(self.eval_status_el(evaluation))
        self.wait_for_element_and_click((By.XPATH, f'{self.eval_row_xpath(evaluation)}//button'))

    def change_instructor(self, evaluation, instructor=None):
        if evaluation.instructor.uid:
            self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_INSTR_BUTTON)
        if instructor:
            app.logger.info(f'Adding UID {instructor.uid} as a instructor on CCN {evaluation.ccn}')
            self.look_up_contact_uid(instructor.uid)
            self.click_look_up_result(instructor)
            evaluation.instructor = instructor
        else:
            app.logger.info('Setting no instructor')
            evaluation.instructor.uid = None

    def change_dept_form(self, evaluation, dept_form):
        app.logger.info(f'Setting dept form {dept_form} on CCN {evaluation.ccn}')
        self.wait_for_element(CourseDashboards.EVAL_CHANGE_DEPT_FORM_INPUT, utils.get_short_timeout())
        Act(self.driver).send_keys_to_element(self.element(CourseDashboards.EVAL_CHANGE_DEPT_FORM_INPUT), dept_form.name)
        time.sleep(1)

    def change_eval_type(self, evaluation, eval_type):
        app.logger.info(f'Setting evaluation type {eval_type} on CCN {evaluation.ccn}')
        self.wait_for_element(CourseDashboards.EVAL_CHANGE_EVAL_TYPE_INPUT, utils.get_short_timeout())
        Act(self.driver).send_keys_to_element(self.element(CourseDashboards.EVAL_CHANGE_EVAL_TYPE_INPUT), eval_type.name)
        time.sleep(1)

    def change_eval_start_date(self, evaluation, date=None):
        if date:
            s = date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting start date {s} on CCN {evaluation.ccn}')
            self.wait_for_element_and_type(CourseDashboards.EVAL_CHANGE_START_DATE_INPUT, s)
        else:
            self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_START_DATE_INPUT)
            self.hit_delete()

    def change_eval_end_date(self, evaluation, date=None):
        if date:
            s = date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting end date {s} on CCN {evaluation.ccn}')
            self.wait_for_element_and_type(CourseDashboards.EVAL_CHANGE_END_DATE_INPUT, s)
        else:
            self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_END_DATE_INPUT)
            self.hit_delete()

    def click_save_eval_changes(self, evaluation):
        app.logger.info(f'Saving changes for CCN {evaluation.ccn}')
        loc = By.XPATH, f'{self.eval_row_xpath(evaluation)}//button[contains(., "Save")]'
        self.wait_for_element_and_click(loc)

    def click_cancel_eval_changes(self, evaluation):
        app.logger.info(f'Canceling changes for CCN {evaluation.ccn}')
        loc = By.XPATH, f'{self.eval_row_xpath(evaluation)}//button[contains(., "Cancel")]'
        if self.is_present(loc):
            self.wait_for_element_and_click(loc)

    def wait_for_validation_error(self, msg):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located((By.XPATH, f'//div[contains(text(), "{msg}")]')),
        )

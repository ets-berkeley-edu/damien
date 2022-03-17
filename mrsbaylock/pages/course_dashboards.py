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
import time

from flask import current_app as app
from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboards(DamienPages):

    COURSE_ACTIONS_SELECT = (By.ID, 'select-term')
    FILTER_UNMARKED = (By.ID, 'evaluations-filter-unmarked')
    FILTER_REVIEW = (By.ID, 'evaluations-filter-review')
    FILTER_CONFIRMED = (By.ID, 'evaluations-filter-confirmed')
    FILTER_IGNORE = (By.ID, 'evaluations-filter-ignore')
    APPLY_FILTER_BUTTON = (By.XPATH, '//label[text()="Course Actions"]/ancestor::div[@class="row"]//button[contains(., "Apply")]')

    def click_unmarked_filter(self):
        app.logger.info('Filtering for unmarked evaluations')
        self.wait_for_element_and_click(CourseDashboards.FILTER_UNMARKED)
        time.sleep(1)

    def click_review_filter(self):
        app.logger.info('Filtering for to-review evaluations')
        self.wait_for_element_and_click(CourseDashboards.FILTER_REVIEW)
        time.sleep(1)

    def click_confirmed_filter(self):
        app.logger.info('Filtering for unmarked evaluations')
        self.wait_for_element_and_click(CourseDashboards.FILTER_CONFIRMED)
        time.sleep(1)

    def click_ignored_filter(self):
        app.logger.info('Filtering for ignored evaluations')
        self.wait_for_element_and_click(CourseDashboards.FILTER_IGNORE)
        time.sleep(1)

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

    def click_confirm_add_section(self):
        app.logger.info('Clicking the confirm button to add a section')
        self.wait_for_element_and_click(CourseDashboards.ADD_SECTION_CONFIRM_BUTTON)

    def click_cancel_add_section(self):
        app.logger.info('Clicking the cancel button for adding a section')
        self.wait_for_element_and_click(CourseDashboards.ADD_SECTION_CANCEL_BUTTON)

    EVALUATION_ROW = (By.XPATH, '//tr[contains(@class, "evaluation-row")]')
    EVAL_CHANGE_INSTR_BUTTON = (By.XPATH, '//button[contains(@id, "-change-instructor")]')
    EVAL_CHANGE_DEPT_FORM_INPUT = (By.ID, 'select-department-form')
    EVAL_CHANGE_EVAL_TYPE_INPUT = (By.ID, 'select-evaluation-type')
    EVAL_CHANGE_START_DATE_INPUT = (By.XPATH, '(//input[@type="date"])[1]')
    EVAL_CHANGE_END_DATE_INPUT = (By.XPATH, '(//input[@type="date"])[2]')
    EVAL_CHANGE_SAVE_BUTTON = (By.XPATH, '//button[contains(., "Save")]')
    EVAL_CHANGE_CXL_BUTTON = (By.XPATH, '//button[contains(., "Cancel")]')

    @staticmethod
    def eval_row_xpath(evaluation):
        uid = f'[contains(., "{evaluation.instructor.uid}")]' if evaluation.instructor else ''
        return f'//tr[contains(., "{evaluation.ccn}")]{uid}'

    def wait_for_eval_rows(self):
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
        self.wait_for_element_and_click((By.XPATH, xpath))

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
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "departmentForm")]'
        return self.element((By.XPATH, xpath)).text

    def eval_type(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "evaluationType")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_start(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "startDate")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_end(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "endDate")]'
        return self.element((By.XPATH, xpath)).text

    def click_edit_evaluation(self, evaluation):
        self.mouseover(self.eval_status_el(evaluation))
        self.wait_for_element_and_click((By.XPATH, f'{self.eval_row_xpath(evaluation)}//button'))

    def change_instructor(self, evaluation, instructor=None):
        self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_INSTR_BUTTON)
        if instructor:
            app.logger.info(f'Adding UID {instructor.uid} as a instructor on CCN {evaluation.ccn}')
            self.look_up_contact_uid(instructor.uid)
            self.click_look_up_result(instructor)
        else:
            app.logger.info('Setting no instructor')

    def change_dept_form(self, evaluation, dept_form):
        app.logger.info(f'Setting dept form {dept_form} on CCN {evaluation.ccn}')
        self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_DEPT_FORM_INPUT)
        self.click_menu_option(dept_form)

    def change_eval_type(self, evaluation, eval_type):
        app.logger.info(f'Setting evaluation type {eval_type} on CCN {evaluation.ccn}')
        self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_EVAL_TYPE_INPUT)
        self.click_menu_option(eval_type)

    def change_eval_start_date(self, evaluation, date_string):
        app.logger.info(f'Setting start date {date_string} on CCN {evaluation.ccn}')
        self.wait_for_element_and_type(CourseDashboards.EVAL_CHANGE_START_DATE_INPUT, date_string)

    def change_eval_end_date(self, evaluation, date_string):
        app.logger.info(f'Setting end date {date_string} on CCN {evaluation.ccn}')
        self.wait_for_element_and_type(CourseDashboards.EVAL_CHANGE_END_DATE_INPUT, date_string)

    def click_save_eval_changes(self, evaluation):
        app.logger.info(f'Saving changes for CCN {evaluation.ccn}')
        self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_SAVE_BUTTON)

    def click_cancel_eval_changes(self, evaluation):
        app.logger.info(f'Canceling changes for CCN {evaluation.ccn}')
        self.wait_for_element_and_click(CourseDashboards.EVAL_CHANGE_CXL_BUTTON)

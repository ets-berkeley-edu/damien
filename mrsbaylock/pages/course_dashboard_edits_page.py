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
from mrsbaylock.pages.course_dashboards import CourseDashboards
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboardEditsPage(CourseDashboards):

    def load_dept_page(self, dept):
        app.logger.info(f'Loading page for {dept.name}')
        self.driver.get(f"{app.config['BASE_URL']}/department/{dept.dept_id}")
        self.wait_for_eval_rows()

    EXPAND_CONTACTS_BUTTON = (By.XPATH, '//button[contains(., "Expand")]')

    def expand_dept_contact_list(self):
        app.logger.info('Expanding the list of contacts')
        self.wait_for_page_and_click(CourseDashboardEditsPage.EXPAND_CONTACTS_BUTTON)

    @staticmethod
    def dept_contact_xpath(user):
        return f'//div[contains(@id, "department-contact-")][contains(., "{user.first_name}") and contains(., "{user.last_name}")]'

    def wait_for_contact(self, user):
        app.logger.info(f'Waiting for UID {user.uid} to appear')
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_element_located((By.XPATH, self.dept_contact_xpath(user))),
        )
        time.sleep(1)

    def dept_contact_name(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}//strong')).text

    def expand_dept_contact(self, user):
        el = self.dept_contact_email_loc(user)
        if not self.is_present(el) or not self.element(el).is_displayed():
            xpath = f'//button[contains(., "{user.first_name}") and contains(., "{user.last_name}")]'
            self.wait_for_page_and_click_js((By.XPATH, xpath))

    def dept_contact_email_loc(self, user):
        return By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "email")]'

    def dept_contact_email(self, user):
        return self.element(self.dept_contact_email_loc(user)).text.strip()

    def dept_contact_comms_perms(self, user):
        return self.element(
            (By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "notifications")]')).text.strip()

    def dept_contact_blue_perms(self, user):
        return self.element(
            (By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "permissions")]')).text.strip()

    def dept_contact_dept_forms(self, user):
        els = self.elements((By.XPATH, f'{self.dept_contact_xpath(user)}//span[contains(@id, "-form-")]'))
        forms = list(map(lambda el: el.text.strip(), els))
        forms.sort()
        return forms

    # COURSE ACTIONS

    COURSE_ACTIONS_SELECT = (By.ID, 'select-course-actions')
    REVIEW_BUTTON = (By.ID, 'apply-course-action-btn-review')
    CONFIRM_BUTTON = (By.ID, 'apply-course-action-btn-confirm')
    UNMARK_BUTTON = (By.ID, 'apply-course-action-btn-unmark')
    IGNORE_BUTTON = (By.ID, 'apply-course-action-btn-ignore')
    DUPE_BUTTON = (By.ID, 'apply-course-action-btn-duplicate')
    DUPE_SECTION_INSTR_INPUT = (By.ID, 'bulk-duplicate-instructor-lookup-autocomplete')
    DUPE_EVAL_TYPE_SELECT = (By.ID, 'bulk-duplicate-select-type')
    DUPE_CXL_BUTTON = (By.ID, 'cancel-duplicate-btn')
    USE_MIDTERM_FORM_CBX = (By.XPATH, '//label[text()="Use midterm department forms"]/preceding-sibling::div')
    USE_START_DATE_INPUT = (By.ID, 'bulk-duplicate-start-date')
    ACTION_APPLY_BUTTON = (By.XPATH, '//button[contains(., "Apply")]')

    def click_bulk_done_button(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.CONFIRM_BUTTON)

    def click_bulk_to_do_button(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.REVIEW_BUTTON)

    def click_bulk_unmark_button(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.UNMARK_BUTTON)

    def click_bulk_ignore_button(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.IGNORE_BUTTON)

    def bulk_set_row_status(self, evaluations, status):
        for evaluation in evaluations:
            app.logger.info(f'Setting CCN {evaluation.ccn} to {status}')
            self.click_eval_checkbox(evaluation)
        if status == EvaluationStatus.FOR_REVIEW:
            self.click_bulk_to_do_button()
        elif status == EvaluationStatus.CONFIRMED:
            self.click_bulk_done_button()
        elif status == EvaluationStatus.UNMARKED:
            self.click_bulk_unmark_button()
        elif status == EvaluationStatus.IGNORED:
            self.click_bulk_ignore_button()
        time.sleep(2)

    def bulk_mark_for_review(self, evaluations):
        self.bulk_set_row_status(evaluations, EvaluationStatus.FOR_REVIEW)
        for evaluation in evaluations:
            evaluation.status = EvaluationStatus.FOR_REVIEW

    def bulk_mark_as_confirmed(self, evaluations):
        self.bulk_set_row_status(evaluations, EvaluationStatus.CONFIRMED)
        for evaluation in evaluations:
            evaluation.status = EvaluationStatus.CONFIRMED

    def bulk_ignore(self, evaluations):
        self.bulk_set_row_status(evaluations, EvaluationStatus.IGNORED)
        for evaluation in evaluations:
            evaluation.status = EvaluationStatus.IGNORED

    def bulk_unmark(self, evaluations):
        self.bulk_set_row_status(evaluations, EvaluationStatus.UNMARKED)
        for evaluation in evaluations:
            evaluation.status = EvaluationStatus.UNMARKED

    def duplicate_section(self, evaluation, evaluations, midterm=None, start_date=None, instructor=None,
                          eval_type=None):
        app.logger.info(f'Duplicating row for CCN {evaluation.ccn}')
        self.click_eval_checkbox(evaluation)
        self.wait_for_page_and_click(CourseDashboardEditsPage.DUPE_BUTTON)
        if instructor:
            self.look_up_uid(instructor.uid, CourseDashboardEditsPage.DUPE_SECTION_INSTR_INPUT)
            self.click_look_up_result(instructor)
        if midterm:
            self.wait_for_element_and_click(CourseDashboardEditsPage.USE_MIDTERM_FORM_CBX)
        if start_date:
            s = start_date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting start date {s}')
            self.wait_for_element_and_type(CourseDashboardEditsPage.USE_START_DATE_INPUT, s)
            self.hit_tab()
            self.hit_tab()
        if eval_type:
            app.logger.info(f'Setting evaluation type {eval_type}')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.DUPE_EVAL_TYPE_SELECT, eval_type)
        else:
            app.logger.info('Setting default evaluation type')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.DUPE_EVAL_TYPE_SELECT, 'Default')
        time.sleep(1)
        self.wait_for_page_and_click_js(CourseDashboardEditsPage.ACTION_APPLY_BUTTON)
        time.sleep(utils.get_short_timeout())
        dupe = copy.deepcopy(evaluation)
        if instructor:
            dupe.instructor = instructor
        if midterm:
            dupe.dept_form = f'{evaluation.dept_form}_MID'
        if start_date:
            dupe.eval_start_date = start_date
        if eval_type:
            dupe.eval_type = eval_type
        evaluations.append(dupe)
        return dupe

    def cancel_dupe(self):
        app.logger.info('Cancelling dupe')
        self.wait_for_element_and_click(CourseDashboardEditsPage.DUPE_CXL_BUTTON)
        time.sleep(1)

    # FILTERS

    FILTER_UNMARKED = (By.ID, 'evaluations-filter-unmarked')
    FILTER_REVIEW = (By.ID, 'evaluations-filter-review')
    FILTER_CONFIRMED = (By.ID, 'evaluations-filter-confirmed')
    FILTER_IGNORE = (By.ID, 'evaluations-filter-ignore')

    def select_filter(self, filter_loc):
        if 'inactive' in self.element(filter_loc).get_attribute('class'):
            self.wait_for_page_and_click(filter_loc)
            time.sleep(2)

    def deselect_filter(self, filter_loc):
        if 'inactive' not in self.element(filter_loc).get_attribute('class'):
            self.wait_for_element_and_click(filter_loc)
            time.sleep(2)

    def select_unmarked_filter(self):
        app.logger.info('Selecting unmarked filter')
        self.select_filter(CourseDashboardEditsPage.FILTER_UNMARKED)

    def deselect_unmarked_filter(self):
        app.logger.info('Deselecting unmarked filter')
        self.deselect_filter(CourseDashboardEditsPage.FILTER_UNMARKED)

    def select_review_filter(self):
        app.logger.info('Selecting to-review filter')
        self.select_filter(CourseDashboardEditsPage.FILTER_REVIEW)

    def deselect_review_filter(self):
        app.logger.info('Deselecting to-review filter')
        self.deselect_filter(CourseDashboardEditsPage.FILTER_REVIEW)

    def select_confirmed_filter(self):
        app.logger.info('Selecting confirmed filter')
        self.select_filter(CourseDashboardEditsPage.FILTER_CONFIRMED)

    def deselect_confirmed_filter(self):
        app.logger.info('Selecting confirmed filter')
        self.deselect_filter(CourseDashboardEditsPage.FILTER_CONFIRMED)

    def select_ignored_filter(self):
        app.logger.info('Selecting ignored filter')
        self.select_filter(CourseDashboardEditsPage.FILTER_IGNORE)

    def deselect_ignored_filter(self):
        app.logger.info('Selecting ignored filter')
        self.deselect_filter(CourseDashboardEditsPage.FILTER_IGNORE)

    # ADD SECTION LOOKUP

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
        self.wait_for_page_and_click(CourseDashboardEditsPage.ADD_SECTION_BUTTON)

    def enter_section(self, ccn):
        app.logger.info(f'Looking up CCN {ccn}')
        self.wait_for_element_and_type(CourseDashboardEditsPage.SECTION_LOOKUP_INPUT, ccn)

    def look_up_section(self, ccn):
        self.enter_section(ccn)
        self.wait_for_element_and_click(CourseDashboardEditsPage.SECTION_LOOKUP_BUTTON)

    def click_cancel_lookup_section(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.SECTION_LOOKUP_CANCEL_BUTTON)

    def click_confirm_add_section(self):
        app.logger.info('Clicking the confirm button to add a section')
        self.wait_for_element_and_click(CourseDashboardEditsPage.ADD_SECTION_CONFIRM_BUTTON)

    def click_cancel_add_section(self):
        app.logger.info('Clicking the cancel button for adding a section')
        self.wait_for_element_and_click(CourseDashboardEditsPage.ADD_SECTION_CANCEL_BUTTON)

    # EVALUATION ROWS

    EVAL_CHANGE_STATUS_SELECT = (By.ID, 'select-evaluation-status')
    EVAL_CHANGE_INSTR_BUTTON = (By.XPATH, '//button[contains(@id, "-change-instructor")]')
    EVAL_CHANGE_INSTR_INPUT = (By.ID, 'input-instructor-lookup-autocomplete')
    EVAL_CHANGE_DEPT_FORM_SELECT = (By.ID, 'select-department-form')
    EVAL_CHANGE_DEPT_FORM_OPTION = (By.XPATH, '//div[@id="select-department-form"]//li')
    EVAL_CHANGE_DEPT_FORM_NO_OPTION = (By.XPATH, '//li[contains(text(), "Sorry, no matching options.")]')
    EVAL_CHANGE_EVAL_TYPE_SELECT = (By.ID, 'select-evaluation-type')
    EVAL_CHANGE_START_DATE_INPUT = (By.XPATH, '//input[contains(@class, "datepicker-input")]')
    EVAL_CHANGE_START_REQ_MSG = (By.XPATH, '//span[contains(text(), "Required")]')
    EVAL_CHANGE_SAVE_BUTTON = (By.ID, 'save-evaluation-edit-btn')
    EVAL_CHANGE_CANCEL_BUTTON = (By.ID, 'cancel-evaluation-edit-btn')

    def click_eval_checkbox(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//input[contains(@id, "checkbox")]'
        app.logger.info(f'Selecting {evaluation.ccn}')
        self.wait_for_page_and_click_js((By.XPATH, xpath))

    def click_edit_evaluation(self, evaluation):
        self.scroll_to_top()
        app.logger.info(f'Waiting for element locator {self.eval_row_xpath(evaluation)}//button')
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_element_located(
                (By.XPATH, f'{self.eval_row_xpath(evaluation)}//button')),
        )
        self.hide_damien_footer()
        self.scroll_to_element(self.eval_row_el(evaluation))
        self.mouseover(self.eval_row_el(evaluation))
        time.sleep(1)
        self.wait_for_page_and_click_js((By.XPATH, f'{self.eval_row_xpath(evaluation)}//button'))

    def select_eval_status(self, evaluation, status):
        app.logger.info(f"Setting CCN {evaluation.ccn} to {status.value['option']}")
        el = Select(self.element(CourseDashboardEditsPage.EVAL_CHANGE_STATUS_SELECT))
        el.select_by_visible_text(status.value['option'])

    def enter_instructor(self, evaluation, instructor):
        app.logger.info(f'Adding UID {instructor.uid} as instructor on CCN {evaluation.ccn}')
        self.look_up_uid(instructor.uid, CourseDashboardEditsPage.EVAL_CHANGE_INSTR_INPUT)
        self.click_look_up_result(instructor)
        evaluation.instructor = instructor

    def click_dept_form_input(self):
        self.wait_for_element_and_click(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT)

    def visible_dept_form_options(self):
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT, utils.get_short_timeout())
        select_el = Select(self.element(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT))
        return list(map(lambda o: o.text.strip(), select_el.options))

    def wait_for_no_dept_form_option(self):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_NO_OPTION))

    def change_dept_form(self, evaluation, dept_form=None):
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT, utils.get_short_timeout())
        if dept_form:
            app.logger.info(f'Setting dept form {dept_form} on CCN {evaluation.ccn}')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT,
                                                  dept_form)
        else:
            app.logger.info('Reverting evaluation type')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_SELECT, 'Revert')
        time.sleep(1)

    def visible_eval_type_options(self):
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, utils.get_short_timeout())
        select_el = Select(self.element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT))
        return list(map(lambda o: o.text.strip(), select_el.options))

    def change_eval_type(self, evaluation, eval_type=None):
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, utils.get_short_timeout())
        if eval_type:
            app.logger.info(f'Setting evaluation type {eval_type} on CCN {evaluation.ccn}')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, eval_type)
        else:
            app.logger.info('Reverting evaluation type')
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, 'Revert')
        time.sleep(1)

    def enter_eval_start_date(self, date):
        app.logger.info(f'Entering evaluation start date {date}')
        self.wait_for_element_and_type(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT, date.strftime('%m/%d/%Y'))

    def change_eval_start_date(self, evaluation, date=None):
        self.wait_for_element_and_click(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT)
        for i in range(10):
            self.hit_delete()
            self.hit_backspace()
            time.sleep(0.5)
        if date:
            date_str = date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting start date {date_str} on CCN {evaluation.ccn}')
            self.element(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT).send_keys(date_str)
        self.hit_tab()
        self.hit_tab()

    def save_eval_changes_button_disabled(self):
        time.sleep(2)
        app.logger.info(f"Save changes button disabled attribute is {self.element(self.EVAL_CHANGE_SAVE_BUTTON).get_attribute('disabled')}")
        return self.element(self.EVAL_CHANGE_SAVE_BUTTON).get_attribute('disabled') == 'disabled'

    def click_save_eval_changes(self, evaluation):
        app.logger.info(f'Saving changes for CCN {evaluation.ccn}')
        self.wait_for_page_and_click_js(self.EVAL_CHANGE_SAVE_BUTTON)

    def save_eval_changes(self, evaluation):
        self.click_save_eval_changes(evaluation)
        self.when_not_present(self.EVAL_CHANGE_SAVE_BUTTON, utils.get_short_timeout())

    def click_cancel_eval_changes(self):
        app.logger.info('Canceling changes')
        if self.is_present(self.EVAL_CHANGE_CANCEL_BUTTON):
            self.wait_for_page_and_click_js(self.EVAL_CHANGE_CANCEL_BUTTON)
            time.sleep(1)

    def wait_for_validation_error(self, msg):
        app.logger.info(f'Waiting for validation error at //div[contains(text(), "{msg}")]')
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{msg}")]')),
        )

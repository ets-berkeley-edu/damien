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
import datetime
import time

from flask import current_app as app
from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboards import CourseDashboards
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.action_chains import ActionChains as Act
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboardEditsPage(CourseDashboards):

    @staticmethod
    def dept_contact_xpath(user):
        return f'//div[contains(@id, "department-contact-")][contains(., "{user.first_name} {user.last_name}")]'

    def wait_for_contact(self, user):
        app.logger.info(f'Waiting for UID {user.uid} to appear')
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, self.dept_contact_xpath(user))),
        )

    def dept_contact_name(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}//strong')).text

    def expand_dept_contact(self, user):
        el = self.dept_contact_email_loc(user)
        if not self.is_present(el) or not self.element(el).is_displayed():
            self.wait_for_page_and_click_js((By.XPATH, f'//button[contains(., "{user.first_name} {user.last_name}")]'))

    def dept_contact_email_loc(self, user):
        return By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "email")]'

    def dept_contact_email(self, user):
        return self.element(self.dept_contact_email_loc(user)).text.strip()

    def dept_contact_comms_perms(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "notifications")]')).text.strip()

    def dept_contact_blue_perms(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}//div[contains(@id, "permissions")]')).text.strip()

    def dept_contact_dept_forms(self, user):
        els = self.elements((By.XPATH, f'{self.dept_contact_xpath(user)}//span[contains(@id, "-form-")]'))
        forms = list(map(lambda el: DepartmentForm(el.text.strip()), els))
        forms.sort(key=lambda f: f.name)
        return forms

    # COURSE ACTIONS

    COURSE_ACTIONS_SELECT = (By.ID, 'select-course-actions')
    USE_MIDTERM_FORM_CBX = (By.XPATH, '//label[text()="Use midterm department forms"]/preceding-sibling::div/input')
    USE_END_DATE_CBX = (By.XPATH, '//label[text()="Set end date:"]/preceding-sibling::div/input')
    USE_END_DATE_INPUT = (By.XPATH, '//input[@type="date"]')
    ACTION_APPLY_BUTTON = (By.XPATH, '//button[contains(., "Apply")]')

    def set_row_status(self, evaluation, status):
        app.logger.info(f'Setting CCN {evaluation.ccn} to {status}')
        self.click_eval_checkbox(evaluation)
        select_el = Select(self.element(CourseDashboardEditsPage.COURSE_ACTIONS_SELECT))
        select_el.select_by_visible_text(status)
        self.wait_for_element_and_click(CourseDashboardEditsPage.ACTION_APPLY_BUTTON)

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
        select_el = Select(self.element(CourseDashboardEditsPage.COURSE_ACTIONS_SELECT))
        select_el.select_by_visible_text('Duplicate')
        if midterm:
            self.wait_for_page_and_click_js(CourseDashboardEditsPage.USE_MIDTERM_FORM_CBX)
        if end_date:
            s = end_date.strftime('%m/%d/%Y')
            app.logger.info(f'Setting end date {s}')
            self.wait_for_page_and_click_js(CourseDashboardEditsPage.USE_END_DATE_CBX)
            self.wait_for_element_and_type(CourseDashboardEditsPage.USE_END_DATE_INPUT, s)
        self.wait_for_element_and_click(CourseDashboardEditsPage.ACTION_APPLY_BUTTON)
        dupe = copy.deepcopy(evaluation)
        if midterm:
            dupe.dept_form = f'{evaluation.dept_form}_MID'
        if end_date:
            dupe.end_date = end_date
        evaluations.append(dupe)
        return dupe

    # FILTERS

    FILTER_UNMARKED = (By.ID, 'evaluations-filter-unmarked')
    FILTER_REVIEW = (By.ID, 'evaluations-filter-review')
    FILTER_CONFIRMED = (By.ID, 'evaluations-filter-confirmed')
    FILTER_IGNORE = (By.ID, 'evaluations-filter-ignore')

    def select_filter(self, filter_loc):
        if 'filter-inactive' in self.element(filter_loc).get_attribute('class'):
            self.wait_for_element_and_click(filter_loc)
            time.sleep(1)

    def deselect_filter(self, filter_loc):
        if 'filter-inactive' not in self.element(filter_loc).get_attribute('class'):
            self.wait_for_element_and_click(filter_loc)
            time.sleep(1)

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
        self.wait_for_element_and_click(CourseDashboardEditsPage.ADD_SECTION_BUTTON)

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

    EVAL_CHANGE_INSTR_BUTTON = (By.XPATH, '//button[contains(@id, "-change-instructor")]')
    EVAL_CHANGE_DEPT_FORM_INPUT = (By.XPATH, '//div[@id="select-department-form"]//input')
    EVAL_CHANGE_DEPT_FORM_OPTION = (By.XPATH, '//div[@id="select-department-form"]//li')
    EVAL_CHANGE_DEPT_FORM_NO_OPTION = (By.XPATH, '//li[contains(text(), "Sorry, no matching options.")]')
    EVAL_CHANGE_EVAL_TYPE_SELECT = (By.ID, 'select-evaluation-type')
    EVAL_CHANGE_START_DATE_INPUT = (By.XPATH, '//div[contains(text(), "Start date:")]/following-sibling::span/input')
    EVAL_CHANGE_SAVE_BUTTON = (By.ID, 'save-evaluation-edit-btn')
    EVAL_CHANGE_CANCEL_BUTTON = (By.ID, 'cancel-evaluation-edit-btn')

    def click_eval_checkbox(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//input[contains(@id, "checkbox")]'
        self.wait_for_page_and_click_js((By.XPATH, xpath))

    def click_edit_evaluation(self, evaluation):
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_element_located(
                (By.XPATH, f'{self.eval_row_xpath(evaluation)}//button')),
        )
        self.hide_damien_footer()
        self.mouseover(self.eval_status_el(evaluation))
        self.wait_for_element_and_click((By.XPATH, f'{self.eval_row_xpath(evaluation)}//button'))

    def change_instructor(self, evaluation, instructor=None):
        if evaluation.instructor.uid:
            self.wait_for_element_and_click(CourseDashboardEditsPage.EVAL_CHANGE_INSTR_BUTTON)
        if instructor:
            app.logger.info(f'Adding UID {instructor.uid} as a instructor on CCN {evaluation.ccn}')
            self.look_up_contact_uid(instructor.uid)
            self.click_look_up_result(instructor)
            evaluation.instructor = instructor
        else:
            app.logger.info('Setting no instructor')
            evaluation.instructor.uid = None

    def click_dept_form_input(self):
        self.wait_for_page_and_click_js(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_INPUT)

    def visible_dept_form_options(self):
        els = self.elements(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_OPTION)
        return list(map(lambda el: el.text.strip(), els))

    def enter_dept_form(self, dept_form):
        for i in dept_form.name:
            Act(self.driver).send_keys_to_element(self.element(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_INPUT), i)
            time.sleep(0.5)

    def wait_for_no_dept_form_option(self):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_NO_OPTION))

    def change_dept_form(self, evaluation, dept_form=None):
        app.logger.info(f'Setting dept form {vars(dept_form)} on CCN {evaluation.ccn}')
        self.click_dept_form_input()
        if dept_form:
            self.wait_for_element_and_type(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_INPUT, dept_form.name)
            self.click_menu_option(dept_form.name)
        else:
            self.element(CourseDashboardEditsPage.EVAL_CHANGE_DEPT_FORM_INPUT).clear()
        time.sleep(1)

    def visible_eval_type_options(self):
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, utils.get_short_timeout())
        select_el = Select(self.element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT))
        return list(map(lambda o: o.text.strip(), select_el.options))

    def change_eval_type(self, evaluation, eval_type=None):
        app.logger.info(f'Setting evaluation type {vars(eval_type)} on CCN {evaluation.ccn}')
        self.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, utils.get_short_timeout())
        if eval_type:
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, eval_type.name)
        else:
            self.wait_for_select_and_click_option(CourseDashboardEditsPage.EVAL_CHANGE_EVAL_TYPE_SELECT, '')
        time.sleep(1)

    def enter_eval_start_date(self, date):
        app.logger.info(f'Entering evaluation start date {date}')
        self.wait_for_element_and_type(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT, date.strftime('%m/%d/%Y'))

    def change_eval_start_date(self, evaluation, date=None):
        if date:
            app.logger.info(f"Setting start date {date.strftime('%m/%d/%Y')} on CCN {evaluation.ccn}")
            self.wait_for_element_and_click(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT)
            self.select_datepicker_date(date)
        else:
            self.wait_for_element_and_click(CourseDashboardEditsPage.EVAL_CHANGE_START_DATE_INPUT)
            self.hit_delete()

    def save_eval_changes_button_disabled(self):
        app.logger.info(f"Save changes button disabled attribute is {self.element(self.EVAL_CHANGE_SAVE_BUTTON).get_attribute('disabled')}")
        return self.element(self.EVAL_CHANGE_SAVE_BUTTON).get_attribute('disabled') == 'disabled'

    def click_save_eval_changes(self, evaluation):
        app.logger.info(f'Saving changes for CCN {evaluation.ccn}')
        self.wait_for_element_and_click(self.EVAL_CHANGE_SAVE_BUTTON)

    def click_cancel_eval_changes(self, evaluation):
        app.logger.info(f'Canceling changes for CCN {evaluation.ccn}')
        if self.is_present(self.EVAL_CHANGE_CANCEL_BUTTON):
            self.wait_for_element_and_click(self.EVAL_CHANGE_CANCEL_BUTTON)

    def wait_for_validation_error(self, msg):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located((By.XPATH, f'//div[contains(text(), "{msg}")]')),
        )

    CALENDAR_MONTH = (By.XPATH, '//div[@class="vc-title"]')
    CALENDAR_BACK_BUTTON = (By.XPATH, '//div[@class="vc-arrow is-left"]')
    CALENDAR_FORWARD_BUTTON = (By.XPATH, '//div[@class="vc-arrow is-right"]')

    def navigate_to_datepicker_month(self, month):
        while month != self.element(CourseDashboardEditsPage.CALENDAR_MONTH).text:
            visible_month = datetime.datetime.strptime(self.element(CourseDashboardEditsPage.CALENDAR_MONTH).text, '%B %Y')
            if visible_month > datetime.datetime.strptime(month, '%B %Y'):
                self.wait_for_element_and_click(CourseDashboardEditsPage.CALENDAR_BACK_BUTTON)
            else:
                self.wait_for_element_and_click(CourseDashboardEditsPage.CALENDAR_FORWARD_BUTTON)
            time.sleep(1)

    def select_datepicker_date(self, date):
        start_date_str = date.strftime('%Y-%m-%d')
        self.navigate_to_datepicker_month(date.strftime('%B %Y'))
        self.wait_for_element_and_click((By.XPATH, f'//div[contains(@class, "id-{start_date_str}")]'))

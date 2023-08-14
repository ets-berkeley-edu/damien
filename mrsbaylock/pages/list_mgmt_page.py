"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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


class ListMgmtPage(DamienPages):

    ADD_DEPT_FORM_BUTTON = (By.ID, 'add-dept-form-btn')
    ADD_DEPT_FORM_INPUT = (By.ID, 'input-dept-form-name')
    ADD_DEPT_FORM_SAVE_BUTTON = (By.ID, 'save-dept-form-btn')
    ADD_DEPT_FORM_CXL_BUTTON = (By.ID, 'cancel-save-dept-form-btn')

    @staticmethod
    def dept_form_delete_button(dept_form):
        return By.XPATH, f'//div[@id="dept-forms-table"]//span[text()="{dept_form}"]/following-sibling::button'

    def visible_dept_form_names(self):
        time.sleep(1)
        els = self.elements((By.XPATH, '//button[contains(@id, "delete-dept-form")]/preceding-sibling::span'))
        forms = []
        for el in els:
            forms.append(el.text)
        return forms

    def add_dept_form(self, dept_form):
        app.logger.info(f'Adding department form {dept_form}')
        self.mouseover(self.element(ListMgmtPage.MENU_BUTTON))
        self.wait_for_element_and_click(ListMgmtPage.ADD_DEPT_FORM_BUTTON)
        self.wait_for_element_and_type(ListMgmtPage.ADD_DEPT_FORM_INPUT, dept_form)
        self.wait_for_element_and_click(ListMgmtPage.ADD_DEPT_FORM_SAVE_BUTTON)
        self.wait_for_element(ListMgmtPage.dept_form_delete_button(dept_form), utils.get_short_timeout())

    def delete_dept_form(self, dept_form):
        app.logger.info(f'Deleting department form {dept_form}')
        self.wait_for_page_and_click_js(ListMgmtPage.dept_form_delete_button(dept_form))
        self.wait_for_element_and_click(ListMgmtPage.DELETE_CONFIRM_BUTTON)
        self.when_not_present(ListMgmtPage.dept_form_delete_button(dept_form), utils.get_short_timeout())

    ADD_EVAL_TYPE_BUTTON = (By.ID, 'add-eval-type-btn')
    ADD_EVAL_TYPE_INPUT = (By.ID, 'input-eval-type-name')
    ADD_EVAL_TYPE_SAVE_BUTTON = (By.ID, 'save-eval-type-btn')
    ADD_EVAL_TYPE_CXL_BUTTON = (By.ID, 'cancel-save-eval-type-btn')

    @staticmethod
    def eval_type_delete_button(eval_type):
        return By.XPATH, f'//div[@id="evaluation-types-table"]//span[text()="{eval_type}"]/following-sibling::button'

    def visible_eval_type_names(self):
        time.sleep(1)
        els = self.elements((By.XPATH, '//button[contains(@id, "delete-eval-type")]/preceding-sibling::span'))
        types = []
        for el in els:
            types.append(el.text)
        return types

    def add_eval_type(self, eval_type):
        app.logger.info(f'Adding evaluation type {eval_type}')
        self.wait_for_element_and_click(ListMgmtPage.ADD_EVAL_TYPE_BUTTON)
        self.wait_for_element_and_type(ListMgmtPage.ADD_EVAL_TYPE_INPUT, eval_type)
        self.wait_for_element_and_click(ListMgmtPage.ADD_EVAL_TYPE_SAVE_BUTTON)
        self.wait_for_element(ListMgmtPage.eval_type_delete_button(eval_type), utils.get_short_timeout())

    def delete_eval_type(self, eval_type):
        app.logger.info(f'Deleting evaluation type {eval_type}')
        self.wait_for_page_and_click_js(ListMgmtPage.eval_type_delete_button(eval_type))
        self.wait_for_element_and_click(ListMgmtPage.DELETE_CONFIRM_BUTTON)
        self.when_not_present(ListMgmtPage.eval_type_delete_button(eval_type), utils.get_short_timeout())

    ADD_INSTR_BUTTON = (By.ID, 'add-instructor-btn')
    ADD_INSTR_UID_INPUT = (By.ID, 'input-instructor-uid')
    ADD_INSTR_CSID_INPUT = (By.ID, 'input-instructor-csid')
    ADD_INSTR_FIRST_NAME_INPUT = (By.ID, 'input-instructor-first-name')
    ADD_INSTR_LAST_NAME_INPUT = (By.ID, 'input-instructor-last-name')
    ADD_INSTR_EMAIL_INPUT = (By.ID, 'input-instructor-email')
    ADD_INSTR_SAVE_BUTTON = (By.ID, 'save-instructor-btn')
    ADD_INSTR_CXL_BUTTON = (By.ID, 'cancel-save-instructor-btn')

    def add_manual_instructor(self, user):
        app.logger.info(f'Adding manual instructor UID {user.uid}')
        self.wait_for_element_and_click(ListMgmtPage.ADD_INSTR_BUTTON)
        self.wait_for_element_and_type(ListMgmtPage.ADD_INSTR_UID_INPUT, user.uid)
        self.wait_for_element_and_type(ListMgmtPage.ADD_INSTR_CSID_INPUT, user.csid)
        self.wait_for_element_and_type(ListMgmtPage.ADD_INSTR_FIRST_NAME_INPUT, user.first_name)
        self.wait_for_element_and_type(ListMgmtPage.ADD_INSTR_LAST_NAME_INPUT, user.last_name)
        self.wait_for_element_and_type(ListMgmtPage.ADD_INSTR_EMAIL_INPUT, user.email)
        self.wait_for_element_and_click(ListMgmtPage.ADD_INSTR_SAVE_BUTTON)

    @staticmethod
    def manual_instr_row_xpath(user):
        return f'//div[@id="instructors-table"]//tr[contains(., "{user.uid}")]'

    def wait_for_manual_instructor(self, user):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located((By.XPATH, ListMgmtPage.manual_instr_row_xpath(user))),
        )

    def delete_manual_instructor(self, user):
        self.wait_for_manual_instructor(user)
        self.wait_for_element_and_click((By.XPATH, f'{ListMgmtPage.manual_instr_row_xpath(user)}//button'))
        self.wait_for_element_and_click(ListMgmtPage.DELETE_CONFIRM_BUTTON)
        self.when_not_present((By.XPATH, ListMgmtPage.manual_instr_row_xpath(user)), utils.get_short_timeout())

    SERVICE_ALERT_INPUT = (By.ID, 'service-announcement-textarea')
    SERVICE_ALERT_POST_CBX = (By.XPATH, '//input[@id="service-announcement-published"]/..')
    SERVICE_ALERT_SAVE_BUTTON = (By.ID, 'service-announcement-save')

    def enter_service_alert(self, alert_text):
        app.logger.info(f'Entering service alert {alert_text}')
        self.remove_and_enter_chars(ListMgmtPage.SERVICE_ALERT_INPUT, alert_text)

    def click_publish_alert_cbx(self):
        self.wait_for_element_and_click(ListMgmtPage.SERVICE_ALERT_POST_CBX)

    def save_service_alert(self):
        self.wait_for_element_and_click(ListMgmtPage.SERVICE_ALERT_SAVE_BUTTON)

    def is_service_alert_posted(self):
        loc = By.ID, 'service-announcement-published'
        return True if (self.element(loc).get_attribute('aria-checked') == 'true') else False

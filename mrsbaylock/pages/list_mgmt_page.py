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
from selenium.webdriver.common.by import By


class ListMgmtPage(DamienPages):

    ADD_DEPT_FORM_BUTTON = (By.ID, 'add-dept-form-btn')
    ADD_DEPT_FORM_INPUT = (By.ID, 'input-dept-form-name')
    ADD_DEPT_FORM_SAVE_BUTTON = (By.ID, 'save-dept-form-btn')
    ADD_DEPT_FORM_CXL_BUTTON = (By.ID, 'cancel-save-dept-form-btn')

    @staticmethod
    def dept_form_delete_button(dept_form):
        return By.XPATH, f'//div[@id="dept-forms-table"]//span[text()="{dept_form.name}"]/following-sibling::button'

    def visible_dept_form_names(self):
        time.sleep(1)
        els = self.elements((By.XPATH, '//button[contains(@id, "delete-dept-form")]/preceding-sibling::span'))
        forms = []
        for el in els:
            forms.append(el.text)
        return forms

    def add_dept_form(self, dept_form):
        app.logger.info(f'Adding department form {dept_form.name}')
        self.mouseover(self.element(ListMgmtPage.MENU_BUTTON))
        self.wait_for_element_and_click(ListMgmtPage.ADD_DEPT_FORM_BUTTON)
        self.wait_for_element_and_type(ListMgmtPage.ADD_DEPT_FORM_INPUT, dept_form.name)
        self.wait_for_element_and_click(ListMgmtPage.ADD_DEPT_FORM_SAVE_BUTTON)
        time.sleep(1)

    def delete_dept_form(self, dept_form):
        app.logger.info(f'Deleting department form {dept_form.name}')
        self.wait_for_page_and_click_js(ListMgmtPage.dept_form_delete_button(dept_form))
        self.wait_for_element_and_click(ListMgmtPage.DELETE_CONFIRM_BUTTON)
        time.sleep(1)

    ADD_EVAL_TYPE_BUTTON = (By.ID, 'add-eval-type-btn')
    ADD_EVAL_TYPE_INPUT = (By.ID, 'input-eval-type-name')
    ADD_EVAL_TYPE_SAVE_BUTTON = (By.ID, 'save-eval-type-btn')
    ADD_EVAL_TYPE_CXL_BUTTON = (By.ID, 'cancel-save-eval-type-btn')

    @staticmethod
    def eval_type_delete_button(eval_type):
        return By.XPATH, f'//div[@id="evaluation-types-table"]//span[text()="{eval_type.name}"]/following-sibling::button'

    def visible_eval_type_names(self):
        time.sleep(1)
        els = self.elements((By.XPATH, '//button[contains(@id, "delete-eval-type")]/preceding-sibling::span'))
        types = []
        for el in els:
            types.append(el.text)
        return types

    def add_eval_type(self, eval_type):
        app.logger.info(f'Adding evaluation type {eval_type.name}')
        self.wait_for_element_and_click(ListMgmtPage.ADD_EVAL_TYPE_BUTTON)
        self.wait_for_element_and_type(ListMgmtPage.ADD_EVAL_TYPE_INPUT, eval_type.name)
        self.wait_for_element_and_click(ListMgmtPage.ADD_EVAL_TYPE_SAVE_BUTTON)
        time.sleep(1)

    def delete_eval_type(self, eval_type):
        app.logger.info(f'Deleting evaluation type {eval_type.name}')
        self.wait_for_page_and_click_js(ListMgmtPage.eval_type_delete_button(eval_type))
        self.wait_for_element_and_click(ListMgmtPage.DELETE_CONFIRM_BUTTON)
        time.sleep(1)

    ADD_INSTR_BUTTON = (By.ID, 'add-instructor-btn')
    ADD_INSTR_UID_INPUT = (By.ID, 'input-instructor-uid')
    ADD_INSTR_CSID_INPUT = (By.ID, 'input-instructor-csid')
    ADD_INSTR_FIRST_NAME_INPUT = (By.ID, 'input-instructor-first-name')
    ADD_INSTR_LAST_NAME_INPUT = (By.ID, 'input-instructor-last-name')
    ADD_INSTR_EMAIL_INPUT = (By.ID, 'input-instructor-email')
    ADD_INSTR_SAVE_BUTTON = (By.ID, 'save-instructor-btn')
    ADD_INSTR_CXL_BUTTON = (By.ID, 'cancel-save-instructor-btn')

    def add_instructor(self, user):
        app.logger.info(f'Adding manual instructor UID {user.uid}')
        self.wait_for_element_and_click(ListMgmtPage.ADD_INSTR_BUTTON)
        # TODO

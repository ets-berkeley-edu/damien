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

from flask import current_app as app
from mrsbaylock.models.blue_perm import BluePerm
from mrsbaylock.pages.course_dashboards import CourseDashboards
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class DeptDetailsAdminPage(CourseDashboards):

    ADD_CONTACT_BUTTON = (By.ID, 'add-dept-contact-btn')
    ADD_CONTACT_LOOKUP_INPUT = (By.ID, 'input-person-lookup-autocomplete')
    ADD_CONTACT_EMAIL = (By.ID, 'input-email-add-contact')
    EMAIL_REQUIRED_MSG = (By.XPATH, '//div[@text()="E-mail is required"]')
    EMAIL_INVALID_MSG = (By.XPATH, '//div[text()="E-mail must be valid"]')
    CONTACT_COMMS_CBX = (By.XPATH, '//input[contains(@id, "checkbox-communications-")]')
    CONTACT_NO_BLUE_RADIO = (By.XPATH, '//input[contains(@id, "radio-no-blue-")]')
    CONTACT_REPORTS_RADIO = (By.XPATH, '//input[contains(@id, "radio-reports-only-")]')
    CONTACT_RESPONSES_RADIO = (By.XPATH, '//input[contains(@id, "radio-response-rates-")]')
    ADD_CONTACT_SAVE_BUTTON = (By.ID, 'save-dept-contact-add-contact-btn')
    ADD_CONTACT_CANCEL_BUTTON = (By.ID, 'cancel-dept-contact-add-contact-btn')
    DELETE_CONFIRM_BUTTON = (By.ID, 'confirm-dialog-btn')
    DELETE_CANCEL_BUTTON = (By.ID, 'cancel-dialog-btn')

    DEPT_NOTE = (By.ID, 'dept-note')
    DEPT_NOTE_EDIT_BUTTON = (By.ID, 'edit-dept-note-btn')
    DEPT_NOTE_TEXTAREA = (By.ID, 'dept-note-textarea')
    DEPT_NOTE_SAVE_BUTTON = (By.ID, 'save-dept-note-btn')
    DEPT_NOTE_CXL_BUTTON = (By.ID, 'cancel-dept-note-btn')
    DEPT_NOTE_DELETE_BUTTON = (By.ID, 'delete-dept-note-btn')

    # CONTACTS

    @staticmethod
    def dept_contact_xpath(user):
        return f'//div[contains(@id, "department-contact-")][contains(., "{user.email}")]/div'

    @staticmethod
    def add_contact_lookup_result(user):
        return By.XPATH, f'//div[contains(@id, "list-item")][contains(., "{user.uid}")]'

    @staticmethod
    def dept_contact_edit_button(user):
        return By.ID, f'edit-dept-contact-{user.user_id}-btn'

    @staticmethod
    def dept_contact_delete_button(user):
        return By.ID, f'delete-dept-contact-{user.user_id}-btn'

    def dept_contact_name(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}/strong')).text

    def dept_contact_comms_perms(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}/div[2]')).text.strip()

    def dept_contact_blue_perms(self, user):
        return self.element((By.XPATH, f'{self.dept_contact_xpath(user)}/div[3]')).text.strip()

    def click_add_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_BUTTON)

    def click_cancel_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON, 1)

    def click_edit_contact(self, user):
        self.wait_for_element_and_click(self.dept_contact_edit_button(user))

    def click_delete_contact(self, user):
        self.wait_for_element_and_click(self.dept_contact_delete_button(user))

    def look_up_contact_uid(self, uid):
        app.logger.info(f'Looking up UID {uid}')
        self.wait_for_element_and_type(DeptDetailsAdminPage.ADD_CONTACT_LOOKUP_INPUT, uid)

    def look_up_contact_name(self, name):
        app.logger.info(f'Looking up {name}')
        self.wait_for_element_and_type(DeptDetailsAdminPage.ADD_CONTACT_LOOKUP_INPUT, name)

    def click_look_up_result(self, user):
        self.wait_for_page_and_click(self.add_contact_lookup_result(user))

    def enter_contact_email(self, email):
        app.logger.info(f'Entering email {email}')
        self.wait_for_element_and_type(DeptDetailsAdminPage.ADD_CONTACT_EMAIL, email)

    def enter_user_flags(self, user):
        if not user.receives_comms:
            self.wait_for_element_and_click(DeptDetailsAdminPage.CONTACT_COMMS_CBX)
        if user.blue_permissions == BluePerm.NO_BLUE:
            self.wait_for_element_and_click(DeptDetailsAdminPage.CONTACT_NO_BLUE_RADIO)
        elif user.blue_permissions == BluePerm.BLUE_REPORTS:
            self.wait_for_element_and_click(DeptDetailsAdminPage.CONTACT_REPORTS_RADIO)
        elif user.blue_permissions == BluePerm.BLUE_REPORTS_RESPONSES:
            self.wait_for_element_and_click(DeptDetailsAdminPage.CONTACT_RESPONSES_RADIO)

    def add_contact(self, user):
        app.logger.info(f'Adding UID {user.uid} as a contact')
        self.look_up_contact_uid(user.uid)
        self.click_look_up_result(user)
        self.enter_contact_email(user.email)
        self.enter_user_flags(user)
        self.click_save_new_contact()
        self.wait_for_contact(user)

    def click_save_new_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_SAVE_BUTTON)

    def cancel_new_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON)

    def wait_for_contact(self, user):
        app.logger.info(f'Waiting for UID {user.uid} to appear')
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, self.dept_contact_xpath(user))),
        )

    # NOTE

    def edit_dept_note(self, note):
        app.logger.info(f'Setting dept note to "{note}"')
        self.wait_for_element_and_click(DeptDetailsAdminPage.DEPT_NOTE_EDIT_BUTTON)
        self.wait_for_element_and_type(DeptDetailsAdminPage.DEPT_NOTE_TEXTAREA, note)

    def save_dept_note(self):
        app.logger.info('Saving dept note')
        self.wait_for_element_and_click(DeptDetailsAdminPage.DEPT_NOTE_SAVE_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.DEPT_NOTE_TEXTAREA, utils.get_short_timeout())

    def verify_dept_note(self, dept):
        if dept.note:
            Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(DeptDetailsAdminPage.DEPT_NOTE))
            assert self.element(DeptDetailsAdminPage.DEPT_NOTE).text == f'{dept.note}'
        else:
            self.when_not_present(DeptDetailsAdminPage.DEPT_NOTE, utils.get_short_timeout())

    def cxl_dept_note(self):
        app.logger.info('Canceling dept note')
        self.wait_for_element_and_click(DeptDetailsAdminPage.DEPT_NOTE_CXL_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.DEPT_NOTE_TEXTAREA, utils.get_short_timeout())

    def delete_dept_note(self):
        app.logger.info('Deleting dept note')
        self.wait_for_element_and_click(DeptDetailsAdminPage.DEPT_NOTE_DELETE_BUTTON)
        self.wait_for_element_and_click(DeptDetailsAdminPage.DELETE_CONFIRM_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.DEPT_NOTE_DELETE_BUTTON, utils.get_short_timeout())
        assert not self.is_present(DeptDetailsAdminPage.DEPT_NOTE)

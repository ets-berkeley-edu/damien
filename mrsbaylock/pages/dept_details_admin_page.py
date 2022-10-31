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
from mrsbaylock.models.blue_perm import BluePerm
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class DeptDetailsAdminPage(CourseDashboardEditsPage):

    TERM_SELECT = (By.ID, 'select-term')

    @staticmethod
    def term_option_locator(term):
        return By.XPATH, f'//option[@id="term-option-{term.term_id}"]'

    def select_term(self, term):
        app.logger.info(f'Selecting term {term.name}')
        self.wait_for_page_and_click_js(DeptDetailsAdminPage.TERM_SELECT)
        self.wait_for_element_and_click(DeptDetailsAdminPage.term_option_locator(term))
        time.sleep(1)

    # Add contact

    ADD_CONTACT_BUTTON = (By.ID, 'add-dept-contact-btn')
    ADD_CONTACT_EMAIL = (By.ID, 'input-email-add-contact')
    EMAIL_REQUIRED_MSG = (By.XPATH, '//div[text()="E-mail is required"]')
    EMAIL_INVALID_MSG = (By.XPATH, '//div[text()="E-mail must be valid"]')
    CONTACT_COMMS_CBX = (By.XPATH, '//input[contains(@id, "checkbox-communications-")]')
    CONTACT_NO_BLUE_RADIO = (By.XPATH, '//input[contains(@id, "radio-no-blue-")]/..')
    CONTACT_REPORTS_RADIO = (By.XPATH, '//input[contains(@id, "radio-reports-only-")]/..')
    CONTACT_RESPONSES_RADIO = (By.XPATH, '//input[contains(@id, "radio-response-rates-")]/..')
    ADD_CONTACT_DEPT_FORM_INPUT = (By.XPATH, '//legend[text()=" Department Forms "]/following-sibling::div//input')
    ADD_CONTACT_DEPT_FORM_OPTION = (By.XPATH, '//li[@role="option"]')
    ADD_CONTACT_SAVE_BUTTON = (By.ID, 'save-dept-contact-add-contact-btn')
    ADD_CONTACT_CANCEL_BUTTON = (By.ID, 'cancel-dept-contact-add-contact-btn')

    @staticmethod
    def dept_contact_form_option(form):
        return By.XPATH, f'//div[@class="v-list-item__title"]/span[text()="{form.name}"]'

    @staticmethod
    def dept_contact_form_remove_button(form):
        return By.XPATH, f'//button[contains(@aria-label, "Remove {form.name}")]'

    def click_add_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_BUTTON)

    def click_cancel_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON, 1)

    def enter_new_contact_email(self, email):
        app.logger.info(f'Entering email {email}')
        self.remove_and_enter_chars(DeptDetailsAdminPage.ADD_CONTACT_EMAIL, email)

    def clear_dept_form_input(self, user=None):
        if user:
            self.wait_for_element_and_click(DeptDetailsAdminPage.dept_contact_form_edit_input(user))
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(DeptDetailsAdminPage.ADD_CONTACT_DEPT_FORM_INPUT),
        )
        self.wait_for_page_and_click_js(DeptDetailsAdminPage.ADD_CONTACT_DEPT_FORM_INPUT)
        self.remove_chars(DeptDetailsAdminPage.ADD_CONTACT_DEPT_FORM_INPUT)

    def enter_and_select_dept_form(self, form):
        self.enter_chars(DeptDetailsAdminPage.ADD_CONTACT_DEPT_FORM_INPUT, form.name)
        self.wait_for_element_and_click(DeptDetailsAdminPage.dept_contact_form_option(form))
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(DeptDetailsAdminPage.dept_contact_form_remove_button(form)),
        )

    def select_dept_forms(self, dept_forms, user=None):
        self.clear_dept_form_input(user)
        for form in dept_forms:
            self.enter_and_select_dept_form(form)

    def remove_dept_forms(self, dept_forms):
        for form in dept_forms:
            self.wait_for_element_and_click(DeptDetailsAdminPage.dept_contact_form_remove_button(form))
            self.when_not_present(DeptDetailsAdminPage.dept_contact_form_remove_button(form), 1)

    def enter_user_flags(self, user, dept):
        role = next(filter(lambda r: (r.dept_id == dept.dept_id), user.dept_roles))
        checked = True if self.element(DeptDetailsAdminPage.CONTACT_COMMS_CBX).get_attribute('aria-checked') == 'true' else False
        if (not role.receives_comms and checked) or (role.receives_comms and not checked):
            self.wait_for_page_and_click_js(DeptDetailsAdminPage.CONTACT_COMMS_CBX)
        if user.blue_permissions == BluePerm.NO_BLUE:
            self.element(DeptDetailsAdminPage.CONTACT_NO_BLUE_RADIO).click()
        elif user.blue_permissions == BluePerm.BLUE_REPORTS:
            self.element(DeptDetailsAdminPage.CONTACT_REPORTS_RADIO).click()
        elif user.blue_permissions == BluePerm.BLUE_REPORTS_RESPONSES:
            self.element(DeptDetailsAdminPage.CONTACT_RESPONSES_RADIO).click()

    def click_save_new_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_SAVE_BUTTON)

    def cancel_new_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.ADD_CONTACT_CANCEL_BUTTON)

    def add_contact(self, user, dept):
        app.logger.info(f'Adding UID {user.uid} as a contact')
        self.look_up_contact_uid(user.uid)
        self.click_look_up_result(user)
        self.enter_new_contact_email(user.email)
        self.enter_user_flags(user, dept)
        self.select_dept_forms(user.dept_forms)
        self.hit_escape()
        self.click_save_new_contact()
        self.wait_for_contact(user)
        user.user_id = utils.get_user_id(user)
        dept.users.append(user)

    # Edit contact

    @staticmethod
    def dept_contact_edit_button(user):
        return By.ID, f'edit-dept-contact-{user.user_id}-btn'

    @staticmethod
    def dept_contact_delete_button(user):
        return By.ID, f'delete-dept-contact-{user.user_id}-btn'

    @staticmethod
    def dept_contact_save_edit_button(user):
        return By.ID, f'save-dept-contact-{user.uid}-btn'

    @staticmethod
    def dept_contact_cancel_edit_button(user):
        return By.ID, f'cancel-dept-contact-{user.uid}-btn'

    @staticmethod
    def dept_contact_email_edit_input(user):
        return By.ID, f'input-email-{user.uid}'

    @staticmethod
    def dept_contact_form_edit_input(user):
        return By.ID, f'autocomplete-select-deptForms-{user.uid}'

    def click_edit_contact(self, user):
        self.wait_for_page_and_click_js(self.dept_contact_edit_button(user))

    def enter_dept_contact_email_edit(self, user, email):
        app.logger.info(f'Entering email {email} for UID {user.uid}')
        self.remove_and_enter_chars(DeptDetailsAdminPage.dept_contact_email_edit_input(user), email)

    def edit_contact(self, user, dept):
        app.logger.info(f'Editing contact UID {user.uid}')
        self.click_edit_contact(user)
        self.enter_dept_contact_email_edit(user, user.email)
        self.enter_user_flags(user, dept)
        self.select_dept_forms(user.dept_forms)
        self.hit_escape()
        self.wait_for_element_and_click(DeptDetailsAdminPage.dept_contact_save_edit_button(user))

    def click_cancel_contact_edits(self, user):
        self.wait_for_element_and_click(DeptDetailsAdminPage.dept_contact_cancel_edit_button(user))

    # Delete contact

    def click_delete_contact(self, user):
        self.wait_for_element_and_click(self.dept_contact_delete_button(user))

    def confirm_delete_contact(self, user):
        self.wait_for_element_and_click(DeptDetailsAdminPage.DELETE_CONFIRM_BUTTON)
        time.sleep(1)

    def cancel_delete_contact(self):
        self.wait_for_element_and_click(DeptDetailsAdminPage.DELETE_CANCEL_BUTTON)

    DEPT_NOTE = (By.ID, 'dept-note')
    DEPT_NOTE_EDIT_BUTTON = (By.ID, 'edit-dept-note-btn')
    DEPT_NOTE_TEXTAREA = (By.ID, 'dept-note-textarea')
    DEPT_NOTE_SAVE_BUTTON = (By.ID, 'save-dept-note-btn')
    DEPT_NOTE_CXL_BUTTON = (By.ID, 'cancel-dept-note-btn')
    DEPT_NOTE_DELETE_BUTTON = (By.ID, 'delete-dept-note-btn')

    def edit_dept_note(self, note):
        app.logger.info(f'Setting dept note to "{note}"')
        self.wait_for_page_and_click(DeptDetailsAdminPage.DEPT_NOTE_EDIT_BUTTON)
        self.wait_for_element_and_type(DeptDetailsAdminPage.DEPT_NOTE_TEXTAREA, note)

    def save_dept_note(self):
        app.logger.info('Saving dept note')
        self.wait_for_element_and_click(DeptDetailsAdminPage.DEPT_NOTE_SAVE_BUTTON)
        self.when_not_present(DeptDetailsAdminPage.DEPT_NOTE_TEXTAREA, utils.get_short_timeout())

    def wait_for_note(self):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(DeptDetailsAdminPage.DEPT_NOTE),
        )

    def verify_dept_note(self, note=None):
        if note:
            self.wait_for_note()
            assert self.element(DeptDetailsAdminPage.DEPT_NOTE).text.strip() == note.strip()
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

    def send_notif_to_dept(self, dept, email, recipients_to_exclude=None):
        app.logger.info(f'Sending notification to {dept.name}')
        self.open_notif_form()
        self.enter_notif_subj(email.subject)
        self.enter_notif_body(email.body)
        if recipients_to_exclude:
            self.notif_expand_dept_recipient_members(dept)
            for recip in recipients_to_exclude:
                self.notif_remove_recipient(dept, recip)
        self.click_notif_send()
        time.sleep(3)

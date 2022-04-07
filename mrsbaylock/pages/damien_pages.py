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
from mrsbaylock.pages.page import Page
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class DamienPages(Page):

    STATUS_LINK = (By.ID, 'sidebar-link-Status Board')
    COURSE_ERRORS_BOARD_LINK = (By.ID, 'sidebar-link-Course Errors Board')
    GRP_MGMT_LINK = (By.ID, 'sidebar-link-Group Management')
    LIST_MGMT_LINK = (By.ID, 'sidebar-link-List Management')

    ADD_CONTACT_LOOKUP_INPUT = (By.ID, 'input-person-lookup-autocomplete')

    MENU_BUTTON = (By.ID, 'btn-main-menu')
    LOG_OUT_LINK = (By.ID, 'menu-item-log-out')

    @staticmethod
    def menu_option_locator(option_str):
        return By.XPATH, f'//*[@role="option"][contains(., "{option_str}")]'

    def click_menu_option(self, option_text):
        app.logger.info(f"Clicking the option '{option_text}'")
        self.wait_for_element_and_click(DamienPages.menu_option_locator(option_text))

    def is_menu_option_disabled(self, option_text):
        return self.element(DamienPages.menu_option_locator(option_text)).get_attribute('aria-disabled') == 'true'

    def wait_for_admin_login(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_element_located(DamienPages.STATUS_LINK))

    def click_menu_button(self):
        self.wait_for_element_and_click(DamienPages.MENU_BUTTON)

    def open_menu(self):
        if not self.is_present(DamienPages.LOG_OUT_LINK) or not self.element(DamienPages.LOG_OUT_LINK).is_displayed():
            app.logger.info('Clicking header menu button')
            self.click_menu_button()

    def log_out(self):
        app.logger.info('Logging out')
        self.open_menu()
        self.wait_for_element_and_click(DamienPages.LOG_OUT_LINK)
        # In case logout doesn't work the first time, try again
        time.sleep(2)
        if self.is_present(DamienPages.LOG_OUT_LINK):
            self.open_menu()
            self.wait_for_element_and_click(DamienPages.LOG_OUT_LINK)

    def click_status_board(self):
        app.logger.info('Clicking link to the Status Board')
        self.wait_for_element_and_click(DamienPages.STATUS_LINK)

    def click_course_errors(self):
        app.logger.info('Clicking link to Courser Errors')
        self.wait_for_element_and_click(DamienPages.COURSE_ERRORS_BOARD_LINK)

    def click_group_mgmt(self):
        app.logger.info('Clicking link to Group Mgmt')
        self.wait_for_element_and_click(DamienPages.GRP_MGMT_LINK)

    def click_list_mgmt(self):
        app.logger.info('Clicking link to List Mgmt')
        self.wait_for_element_and_click(DamienPages.LIST_MGMT_LINK)

    @staticmethod
    def dept_link_loc(dept):
        return By.XPATH, f'//a[contains(@href, "/department/{dept.dept_id}") and contains(text(), "{dept.name}")]'

    def click_dept_link(self, dept):
        app.logger.info(f'Clicking the link for {dept.name}')
        self.wait_for_element_and_click(self.dept_link_loc(dept))

    @staticmethod
    def add_contact_lookup_result(user):
        return By.XPATH, f'//div[contains(@id, "list-item")][contains(., "{user.uid}")]'

    def look_up_contact_uid(self, uid):
        app.logger.info(f'Looking up UID {uid}')
        self.remove_and_enter_chars(DamienPages.ADD_CONTACT_LOOKUP_INPUT, uid)

    def look_up_contact_name(self, name):
        app.logger.info(f'Looking up {name}')
        self.remove_and_enter_chars(DamienPages.ADD_CONTACT_LOOKUP_INPUT, name)

    def click_look_up_result(self, user):
        self.wait_for_page_and_click(self.add_contact_lookup_result(user))

    NOTIF_FORM_BUTTON = (By.ID, 'open-notification-form-btn')
    NOTIF_SUBJ_INPUT = (By.ID, 'input-notification-subject')
    NOTIF_BODY_INPUT = (By.ID, 'input-notification-message')
    NOTIF_SEND_BUTTON = (By.ID, 'send-notification-btn')
    NOTIF_CXL_BUTTON = (By.ID, 'cancel-send-notification-btn')
    NOTIF_DEPT_RECIPIENT = (By.XPATH, '//h4[contains(@id, "dept-head-")]')

    def open_notif_form(self):
        self.wait_for_page_and_click_js(DamienPages.NOTIF_FORM_BUTTON)
        Wait(self.driver, 1).until(ec.visibility_of_element_located(DamienPages.NOTIF_SEND_BUTTON))

    def notif_dept_recipients(self):
        return list(map(lambda el: el.text, self.elements(DamienPages.NOTIF_DEPT_RECIPIENT)))

    @staticmethod
    def notif_expand_dept_xpath(dept):
        return f'//h4[contains(@id, "dept-head-")][text()="{dept.name}"]/..'

    def notif_expand_dept_recipient_members(self, dept):
        app.logger.info(f'Expanding notification department {dept.name}')
        if self.element((By.XPATH, DamienPages.notif_expand_dept_xpath(dept))).get_attribute('aria-expanded'):
            app.logger.info('Recipient list is already expanded')
        else:
            app.logger.info('Expanding recipient list')
            self.wait_for_element_and_click((By.XPATH, DamienPages.notif_expand_dept_xpath(dept)))

    def notif_dept_recipient_emails(self, dept):
        time.sleep(1)
        els = self.elements((By.XPATH, f'{DamienPages.notif_expand_dept_xpath(dept)}/following-sibling::div//button/..'))
        return list(map(lambda e: e.text.strip().replace(')', '').split(' (')[-1], els))

    @staticmethod
    def notif_dept_recipient_remove_btn(dept, user):
        xpath = f'{DamienPages.notif_expand_dept_xpath(dept)}/following-sibling::div//span[contains(text(), "{user.email}")]/button'
        return By.XPATH, xpath

    def notif_remove_recipient(self, dept, user):
        app.logger.info(f'Removing {user.email} from {dept.name} recipient list')
        self.wait_for_element_and_click(DamienPages.notif_dept_recipient_remove_btn(dept, user))
        self.when_not_present(DamienPages.notif_dept_recipient_remove_btn(dept, user), 1)

    def enter_notif_subj(self, subj):
        app.logger.info(f'Entering subject {subj}')
        self.remove_and_enter_chars(DamienPages.NOTIF_SUBJ_INPUT, subj)

    def enter_notif_body(self, body):
        app.logger.info(f'Entering body {body}')
        self.remove_and_enter_chars(DamienPages.NOTIF_BODY_INPUT, body)

    def click_notif_send(self):
        app.logger.info('Clicking send button')
        self.wait_for_element_and_click(DamienPages.NOTIF_SEND_BUTTON)
        time.sleep(2)  # TODO - wait for confirmation

    def click_notif_cxl(self):
        app.logger.info('Clicking cancel button')
        self.wait_for_element_and_click(DamienPages.NOTIF_CXL_BUTTON)
        self.when_not_present(DamienPages.NOTIF_SUBJ_INPUT, utils.get_short_timeout())

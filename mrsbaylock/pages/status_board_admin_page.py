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

import datetime
import time

from flask import current_app as app
from selenium.webdriver.common.by import By

from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils


class StatusBoardAdminPage(DamienPages):

    EVAL_STATUS_DASH_HEADING = (By.XPATH, '//h1[contains(text(), "Evaluation Status Dashboard")]')

    def load_page(self):
        app.logger.info('Loading the dept status page')
        self.driver.get(f'{app.config["BASE_URL"]}/status')
        self.wait_for_depts()

    def wait_for_depts(self):
        self.when_visible((By.XPATH, '//a[starts-with(@id, "link-to-dept-")]'), utils.get_medium_timeout())

    LOCK_BOX = (By.ID, 'toggle-term-locked')

    def toggle_term_lock(self):
        app.logger.info('Locking current term edits')
        self.wait_for_page_and_click(StatusBoardAdminPage.LOCK_BOX)

    def is_current_term_locked(self):
        time.sleep(1)
        return 'Unlock' in self.element(StatusBoardAdminPage.LOCK_BOX).get_dom_attribute('title')

    NOTIF_SELECT_ALL_CBX = (By.ID, 'checkbox-select-dept-all')
    NOTIF_APPLY_BUTTON = (By.ID, 'open-notification-form-btn')

    @staticmethod
    def notif_select_dept_cbx(dept):
        return By.XPATH, f'//input[@id="checkbox-select-dept-{dept.dept_id}"]'

    def check_dept_notif_cbx(self, dept):
        app.logger.info(f'Clicking the notification checkbox for {dept.name}')
        self.wait_for_page_and_click_js(StatusBoardAdminPage.notif_select_dept_cbx(dept))

    def check_all_dept_notif_cbx(self):
        app.logger.info('Clicking the select-all notification checkbox')
        self.wait_for_page_and_click_js(StatusBoardAdminPage.NOTIF_SELECT_ALL_CBX)

    def send_notif_to_depts(self, email, recipients_to_exclude=None):
        self.open_notif_form()
        self.enter_notif_subj(email.subject)
        self.enter_notif_body(email.body)
        if recipients_to_exclude:
            for recip in recipients_to_exclude:
                user = recip['user']
                dept = recip['dept']
                self.notif_expand_dept_recipient_members(dept)
                self.notif_remove_recipient(dept, user)
        self.click_notif_send()
        self.when_not_present(DamienPages.NOTIF_SEND_BUTTON, utils.get_medium_timeout())
        time.sleep(2)

    @staticmethod
    def dept_row_xpath(dept):
        return f'//a[@href="/department/{dept.dept_id}"]/ancestor::tr'

    def dept_last_update_date(self, dept):
        xpath = f'{StatusBoardAdminPage.dept_row_xpath(dept)}/td[@class="department-lastUpdated"]'
        self.wait_for_element((By.XPATH, xpath), utils.get_short_timeout())
        if self.is_present((By.XPATH, f'{xpath}/span')):
            return datetime.datetime.strptime(self.element((By.XPATH, f'{xpath}/span')).text.strip(), '%b %d, %Y').date()
        else:
            return None

    def dept_errors_count(self, dept):
        xpath = f'{StatusBoardAdminPage.dept_row_xpath(dept)}/td[@class="department-errors"]'
        self.wait_for_element((By.XPATH, xpath), utils.get_short_timeout())
        if self.is_present((By.ID, f'errors-count-dept-{dept.dept_id}')):
            return int(self.element((By.XPATH, f'{xpath}//span')).text.strip())
        elif self.is_present((By.XPATH, f'{xpath}/i[@alt="no errors"]')):
            return 0

    def dept_confirmed_all(self, dept):
        time.sleep(2)
        xpath = f'{StatusBoardAdminPage.dept_row_xpath(dept)}/td[@class="department-confirmed"]/i[@alt="all confirmed"]'
        return self.is_present((By.XPATH, xpath))

    def dept_confirmed_count(self, dept):
        xpath = f'{StatusBoardAdminPage.dept_row_xpath(dept)}/td[@class="department-confirmed"]/span/span'
        self.wait_for_element((By.XPATH, xpath), utils.get_short_timeout())
        count = self.element((By.XPATH, xpath)).text.split(' / ')
        return int(count[0]), int(count[1])

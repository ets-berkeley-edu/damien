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

import csv
import glob
import os
import re
import shutil
import time
import zipfile

from flask import current_app as app
from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class StatusBoardAdminPage(DamienPages):

    EVAL_STATUS_DASH_HEADING = (By.XPATH, '//h1[contains(text(), "Evaluation Status Dashboard")]')

    def load_page(self):
        app.logger.info('Loading the dept status page')
        self.driver.get(f'{app.config["BASE_URL"]}/status')
        self.wait_for_depts()

    def wait_for_depts(self):
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.visibility_of_any_elements_located((By.XPATH, '//a[starts-with(@id, "link-to-dept-")]')),
        )

    LOCK_BOX = (By.XPATH, '//label[text()=" Lock current term "]/following-sibling::div//input/..')
    UNLOCK_BOX = (By.XPATH, '//label[text()=" Unlock current term "]/following-sibling::div//input/..')

    def lock_current_term(self):
        app.logger.info('Locking current term edits')
        self.wait_for_element_and_click(StatusBoardAdminPage.LOCK_BOX)

    def unlock_current_term(self):
        app.logger.info('Unlocking current term edits')
        self.wait_for_element_and_click(StatusBoardAdminPage.UNLOCK_BOX)

    def is_current_term_locked(self):
        time.sleep(1)
        return True if (self.is_present(StatusBoardAdminPage.UNLOCK_BOX)) else False

    NOTIF_SELECT_ALL_CBX = (By.ID, 'checkbox-select-dept-all')
    NOTIF_APPLY_BUTTON = (By.ID, 'open-notification-form-btn')

    @staticmethod
    def notif_select_dept_cbx(dept):
        dept_str = re.sub('[& ]', '-', dept.name.lower().replace(',', ''))
        return By.ID, f'checkbox-select-dept-{dept_str}'

    def check_dept_notif_cbx(self, dept):
        app.logger.info(f'Clicking the notification checkbox for {dept.name}')
        self.wait_for_element_and_click(StatusBoardAdminPage.notif_select_dept_cbx(dept))

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

    # PUBLISH

    PUBLISH_BUTTON = (By.ID, 'publish-btn')
    TERM_EXPORT_BUTTON = (By.XPATH, '//button[contains(., "Term Exports")]')
    TERM_EXPORT_LINK = (By.XPATH, '//a[contains(@id, "term-export-")]')

    def expand_term_exports(self):
        self.wait_for_element(StatusBoardAdminPage.TERM_EXPORT_BUTTON, utils.get_medium_timeout())
        if not self.element(StatusBoardAdminPage.TERM_EXPORT_BUTTON).get_attribute('aria-expanded'):
            self.click_element(StatusBoardAdminPage.TERM_EXPORT_BUTTON)

    def publish_to_blue(self):
        self.expand_term_exports()
        initial_count = len(self.elements(StatusBoardAdminPage.TERM_EXPORT_LINK))
        app.logger.info(f'There are currently {initial_count} previous export links')
        tries = 0
        retries = utils.get_medium_timeout()
        app.logger.info('Publishing to Blue')
        self.wait_for_page_and_click(StatusBoardAdminPage.PUBLISH_BUTTON)
        time.sleep(1)
        while tries <= retries:
            tries += 1
            try:
                new_count = len(self.elements(StatusBoardAdminPage.TERM_EXPORT_LINK))
                app.logger.info(f'There are now {new_count} export links')
                assert new_count > initial_count
                break
            except AssertionError:
                if tries == retries:
                    app.logger.info('Timed out waiting for publishing to finish')
                    raise
                else:
                    time.sleep(1)

    def download_export_csvs(self):
        app.logger.info(f'Downloading export CSVs to {utils.default_download_dir()}')

        if os.path.isdir(utils.default_download_dir()):
            shutil.rmtree(utils.default_download_dir())
        os.mkdir(utils.default_download_dir())

        self.publish_to_blue()
        time.sleep(1)
        el = self.elements(StatusBoardAdminPage.TERM_EXPORT_LINK)[0]
        el.click()
        tries = 0
        max_tries = 15
        while tries <= max_tries:
            tries += 1
            try:
                assert len(glob.glob(f'{utils.default_download_dir()}/*.zip')) == 1
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)

        file = glob.glob(f'{utils.default_download_dir()}/*.zip')[0]
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(utils.default_download_dir())

    @staticmethod
    def parse_csv(file_name):
        file = f'{utils.default_download_dir()}/{file_name}.csv'
        rows = []
        with open(file) as csv_file:
            for row in csv.DictReader(csv_file):
                rows.append(row)
        return rows

    def parse_supervisors_csv(self):
        csv = self.parse_csv('supervisors')
        rows = []
        for row in csv:
            depts = list(row.values())[8::]
            depts = list(filter(None, depts))
            depts.sort()
            rows.append({
                'LDAP_UID': row['LDAP_UID'],
                'SIS_ID': row['SIS_ID'],
                'FIRST_NAME': row['FIRST_NAME'],
                'LAST_NAME': row['LAST_NAME'],
                'EMAIL_ADDRESS': row['EMAIL_ADDRESS'],
                'SUPERVISOR_GROUP': row['SUPERVISOR_GROUP'],
                'PRIMARY_ADMIN': row['PRIMARY_ADMIN'],
                'SECONDARY_ADMIN': row['SECONDARY_ADMIN'],
                'DEPTS': depts,
            })
        return rows

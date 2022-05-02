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

from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class GroupMgmtPage(DamienPages):

    def dept_row_index(self, dept):
        idx = self.element((By.XPATH, f'//a[@href="/department/{dept.dept_id}"]/..')).get_attribute('id').split('-')[1]
        return int(idx)

    def dept_row_link(self, dept):
        self.element((By.XPATH, f'//a[@href="/department/{dept.dept_id}"]'))

    def wait_for_dept_row(self, dept):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located((By.XPATH, f'//a[@href="/department/{dept.dept_id}"]')),
        )

    def dept_row_course_count(self, idx):
        return self.element((By.ID, f'department-{idx}-courses')).text.strip()

    @staticmethod
    def dept_user_row_xpath(idx, user):
        return f'//td[contains(@id, "department-{idx}")][text()="{user.uid}"]/..'

    def dept_user_name(self, idx, user):
        xpath = f'{GroupMgmtPage.dept_user_row_xpath(idx, user)}/td[contains(@id, "name") and contains(@id, "contact")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def dept_user_email(self, idx, user):
        xpath = f'{GroupMgmtPage.dept_user_row_xpath(idx, user)}/td[contains(@id, "email")]'
        return self.element((By.XPATH, xpath)).text

    def dept_user_comms(self, idx, user):
        xpath = f'{GroupMgmtPage.dept_user_row_xpath(idx, user)}/td[contains(@id, "comms")]/span'
        return self.element((By.XPATH, xpath)).get_attribute('innerText')

    def dept_user_blue_perm(self, idx, user):
        xpath = f'{GroupMgmtPage.dept_user_row_xpath(idx, user)}/td[contains(@id, "blue")]//span'
        return self.element((By.XPATH, xpath)).get_attribute('innerText').strip()

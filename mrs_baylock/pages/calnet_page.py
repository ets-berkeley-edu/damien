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
from mrs_baylock.pages.page import Page
from mrs_baylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CalNetPage(Page):

    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'password')
    SUBMIT_BUTTON = (By.ID, 'submit')
    INVALID_CREDENTIALS_MSG = (By.XPATH, '//span[contains(text(), "Invalid credentials.")]')
    DUO_FRAME = (By.XPATH, '//div[@id="duo_iframe"]/iframe')
    REMEMBER_ME = (By.NAME, 'dampen_choice')
    SEND_PUSH = (By.XPATH, '//button[text()="Send Me a Push "]')

    def log_in(self, username, password):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.title_contains('CAS – Central Authentication Service')
        )
        if username == 'secret' or password == 'secret':
            if utils.browser_is_headless():
                app.logger.error('Browser is running in headless mode, manual login is not supported')
                raise RuntimeError
            else:
                app.logger.debug('Waiting for manual login')
                self.wait_for_element_and_type(CalNetPage.USERNAME_INPUT, 'PLEASE LOG IN MANUALLY')
        else:
            app.logger.info(f'{username} is logging in')
            self.wait_for_element_and_type(CalNetPage.USERNAME_INPUT, username)
            self.wait_for_element_and_type(CalNetPage.PASSWORD_INPUT, password)
            self.wait_for_element_and_click(CalNetPage.SUBMIT_BUTTON)
            time.sleep(2)
            if self.is_present(CalNetPage.DUO_FRAME):
                self.driver.switch_to.frame(self.element(CalNetPage.DUO_FRAME))
                if not self.element(CalNetPage.REMEMBER_ME).is_selected():
                    self.wait_for_element_and_click(CalNetPage.REMEMBER_ME)
                self.wait_for_element_and_click(CalNetPage.SEND_PUSH)
            elif self.is_present(CalNetPage.INVALID_CREDENTIALS_MSG):
                app.logger.error('Invalid credentials')
                raise RuntimeError
        Wait(self.driver, utils.get_long_timeout()).until(
            not ec.title_contains('CAS – Central Authentication Service')
        )

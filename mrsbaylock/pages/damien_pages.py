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

    MENU_BUTTON = (By.ID, 'btn-main-menu')
    LOG_OUT_LINK = (By.ID, 'menu-item-log-out')

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

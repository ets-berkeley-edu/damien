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
from mrsbaylock.pages.page import Page
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class ApiPage(Page):

    def hit_cache_clear(self):
        self.driver.get(f'{app.config["BASE_URL"]}/api/cache/clear')

    def clear_cache(self):
        self.hit_cache_clear()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "cleared")]')),
        )

    def hit_refresh_loch(self):
        self.driver.get(f'{app.config["BASE_URL"]}/api/job/refresh_unholy_loch')

    def wait_for_refresh_job(self):
        tries = 0
        max_tries = 90
        while tries <= max_tries:
            tries += 1
            try:
                app.logger.info('Checking refresh job status')
                time.sleep(15)
                self.driver.get(f'{app.config["BASE_URL"]}/api/job/status')
                self.wait_for_element((By.XPATH, '//*[contains(text(), "status")]'), utils.get_short_timeout())
                assert self.is_present((By.XPATH, '//*[contains(text(), "done")]'))
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)

    def refresh_unholy_loch(self):
        app.logger.info('Refreshing the Unholy Loch')
        self.hit_refresh_loch()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "started")]')),
        )
        self.wait_for_refresh_job()

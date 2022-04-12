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

from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboards(DamienPages):

    EVALUATION_ROW = (By.XPATH, '//tr[contains(@class, "evaluation-row")]')

    @staticmethod
    def eval_row_xpath(evaluation):
        uid = f'[contains(., "{evaluation.instructor.uid}")]' if evaluation.instructor.uid else ''
        return f'//tr[contains(., " {evaluation.ccn} ")]{uid}'

    @staticmethod
    def section_row(evaluation):
        return By.XPATH, f'//tr[contains(., "{evaluation.ccn}")]'

    def wait_for_eval_rows(self):
        time.sleep(1)
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_all_elements_located(CourseDashboards.EVALUATION_ROW),
        )

    def visible_eval_identifiers(self):
        self.wait_for_eval_rows()
        time.sleep(1)
        identifiers = []
        for index, value in enumerate(self.elements(CourseDashboards.EVALUATION_ROW)):
            cell = self.element((By.XPATH, f'//tr[contains(@class, "evaluation-row")][{index + 1}]/td[2]'))
            idx = cell.get_attribute('id').split('-')[1]
            ccn = self.element((By.ID, f'evaluation-{idx}-courseNumber')).text.strip().split('\n')[0]
            uid_loc = (By.XPATH, f'//td[@id="evaluation-{idx}-instructor"]/div')
            uid = ''
            if self.is_present(uid_loc):
                uid = self.element(uid_loc).text.strip().split()[-1].replace('(', '').replace(')', '')
            e_type = self.element((By.ID, f'evaluation-{idx}-evaluationType')).text.strip()
            identifiers.append(f'{ccn}-{uid}-{e_type}')
        return identifiers

    def eval_status_el(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "status")]'
        return self.element((By.XPATH, xpath))

    def eval_status(self, evaluation):
        return self.eval_status_el(evaluation).text

    def eval_last_update(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "lastUpdated")]'
        return self.element((By.XPATH, xpath)).text

    def eval_ccn(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "courseNumber")]'
        return self.element((By.XPATH, xpath)).text.strip().split('\n')[0]

    def eval_course(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//div[contains(@id, "courseName")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_title(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}//div[contains(@id, "courseTitle")]'
        return self.element((By.XPATH, xpath)).text

    def eval_instructor(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "instructor")]'
        return self.element((By.XPATH, xpath)).text

    def eval_dept_form(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "departmentForm")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_type(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "evaluationType")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_period_dates(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "period")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_period_duration(self, evaluation):
        xpath = f'{self.eval_row_xpath(evaluation)}/td[contains(@id, "period")]/span/div[2]'
        return self.element((By.XPATH, xpath)).text.strip()

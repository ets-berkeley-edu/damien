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

    EVALUATION_ROW = (By.CLASS_NAME, 'evaluation-row')

    @staticmethod
    def eval_row_xpath(section, instructor):
        return f'//tr[contains(., "{section.ccn}")][contains(., "{instructor.uid}")]'

    def wait_for_eval_rows(self):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_all_elements_located(CourseDashboards.EVALUATION_ROW),
        )

    def visible_eval_identifiers(self):
        self.wait_for_eval_rows()
        time.sleep(2)
        identifiers = []
        for index, value in enumerate(self.elements(CourseDashboards.EVALUATION_ROW)):
            ccn = self.element((By.ID, f'evaluation-{index}-courseNumber')).text.strip()
            uid_loc = (By.XPATH, f'//td[@id="evaluation-{index}-instructor"]/div')
            uid = ''
            if self.is_present(uid_loc):
                uid = self.element(uid_loc).text.strip().split()[-1].replace('(', '').replace(')', '')
            identifiers.append(f'{ccn}-{uid}')
        return identifiers

    def eval_status(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "status")]'
        return self.element((By.XPATH, xpath)).text

    def eval_last_update(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "lastUpdated")]'
        return self.element((By.XPATH, xpath)).text

    def eval_ccn(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "courseNumber")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}//div[contains(@id, "courseName")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_title(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}//div[contains(@id, "courseTitle")]'
        return self.element((By.XPATH, xpath)).text

    def eval_instructor(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "instructor")]'
        return self.element((By.XPATH, xpath)).text

    def eval_dept_form(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "departmentForm")]'
        return self.element((By.XPATH, xpath)).text

    def eval_type(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "evaluationType")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_start(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "startDate")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_end(self, section, instructor):
        xpath = f'{self.eval_row_xpath(section, instructor)}/td[contains(@id, "endDate")]'
        return self.element((By.XPATH, xpath)).text

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
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvalExports:

    term = utils.get_current_term()
    utils.reset_test_data(term)
    all_contacts = utils.get_all_users()
    dept = utils.get_test_dept_1()
    evals = evaluation_utils.get_evaluations(term, dept)
    confirmed = []

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.clear_cache()

    def test_confirm_complete_evals(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        for row in self.evals:
            if row.instructor.uid and row.dept_form and row.eval_type:
                self.dept_details_admin_page.click_eval_checkbox(row)
                self.confirmed.append(row)
        self.dept_details_admin_page.click_bulk_done_button()
        time.sleep(2)

    def test_publish(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.download_export_csvs()

    def test_course_students(self):
        expected_course_students = utils.expected_course_students(self.confirmed)
        actual_course_students = self.status_board_admin_page.parse_csv('course_students')
        unexpected = [x for x in actual_course_students if x not in expected_course_students]
        missing = [x for x in expected_course_students if x not in actual_course_students]
        app.logger.info(f'Unexpected {unexpected}')
        app.logger.info(f'Missing {missing}')
        assert not unexpected
        assert not missing

    def test_course_instructors(self):
        expected_course_instructors = utils.expected_course_instructors(self.confirmed)
        actual_course_instructors = self.status_board_admin_page.parse_csv('course_instructors')
        unexpected = [x for x in actual_course_instructors if x not in expected_course_instructors]
        missing = [x for x in expected_course_instructors if x not in actual_course_instructors]
        app.logger.info(f'Unexpected {unexpected}')
        app.logger.info(f'Missing {missing}')
        assert not unexpected
        assert not missing

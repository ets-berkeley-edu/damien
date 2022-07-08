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

from datetime import timedelta

from flask import current_app as app
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.dept_details_admin_page import DeptDetailsAdminPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


@pytest.mark.usefixtures('page_objects')
class TestDeptUser:

    term = utils.get_current_term()
    dept = utils.get_dept('Environmental Science, Policy and Management')
    utils.reset_test_data(term)
    evaluations = evaluation_utils.get_evaluations(term, dept)
    contact = next(filter(lambda u: (len(u.dept_roles) == 1), dept.users))

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_log_in_landing_page(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.log_out()
        self.login_page.dev_auth(self.contact)
        self.dept_details_dept_page.wait_for_eval_rows()

    # USER PERMISSIONS

    def test_no_status_page(self):
        self.driver.get(f'{app.config["BASE_URL"]}/status')
        self.homepage.wait_for_title('404 | Course Evaluations')

    def test_no_publish_page(self):
        self.driver.get(f'{app.config["BASE_URL"]}/publish?term={self.term.term_id}')
        self.homepage.wait_for_title('404 | Course Evaluations')

    def test_no_group_mgmt_page(self):
        self.driver.get(f'{app.config["BASE_URL"]}/departments')
        self.homepage.wait_for_title('404 | Course Evaluations')

    def test_no_list_mgmt_page(self):
        self.driver.get(f'{app.config["BASE_URL"]}/lists')
        self.homepage.wait_for_title('404 | Course Evaluations')

    def test_foreign_dept_page(self):
        all_depts = utils.get_participating_depts()
        foreign_dept = next(filter(lambda d: d.dept_id != self.dept, all_depts))
        self.driver.get(f'{app.config["BASE_URL"]}/department/{foreign_dept.dept_id}')
        self.homepage.wait_for_title('404 | Course Evaluations')

    def test_api_cache(self):
        self.api_page.hit_cache_clear()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "Unauthorized")]')),
        )

    def test_api_unholy_loch(self):
        self.api_page.hit_refresh_loch()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located((By.XPATH, '//*[contains(text(), "Unauthorized")]')),
        )

    def test_no_notifications(self):
        self.homepage.load_page()
        self.dept_details_dept_page.wait_for_eval_rows()
        assert not self.dept_details_dept_page.is_present(DeptDetailsAdminPage.NOTIF_FORM_BUTTON)

    def test_dept_page_no_add_contact(self):
        assert not self.dept_details_dept_page.is_present(DeptDetailsAdminPage.ADD_CONTACT_BUTTON)

    def test_dept_page_notes(self):
        assert self.dept_details_dept_page.is_present(DeptDetailsAdminPage.DEPT_NOTE_EDIT_BUTTON)

    # EVALUATION SORTING

    def test_set_test_data(self):
        evaluation_utils.calculate_eval_dates(self.evaluations)

        done = next(filter(lambda e: (e.instructor.uid and e.dept_form and e.eval_type), self.evaluations))
        self.dept_details_dept_page.click_edit_evaluation(done)
        self.dept_details_dept_page.select_eval_status(done, EvaluationStatus.CONFIRMED)
        self.dept_details_dept_page.click_save_eval_changes(done)
        done.status = EvaluationStatus.CONFIRMED

        remaining = list(filter(lambda e: e.status == EvaluationStatus.UNMARKED, self.evaluations))
        to_do = remaining[0]
        self.dept_details_dept_page.click_edit_evaluation(to_do)
        self.dept_details_dept_page.select_eval_status(to_do, EvaluationStatus.FOR_REVIEW)
        self.dept_details_dept_page.click_save_eval_changes(to_do)
        to_do.status = EvaluationStatus.FOR_REVIEW

        ignore = remaining[1]
        self.dept_details_dept_page.click_edit_evaluation(ignore)
        self.dept_details_dept_page.select_eval_status(ignore, EvaluationStatus.IGNORED)
        self.dept_details_dept_page.click_save_eval_changes(ignore)
        ignore.status = EvaluationStatus.IGNORED

        change_date = remaining[2]
        new_start = change_date.eval_start_date - timedelta(days=1)
        self.dept_details_dept_page.click_edit_evaluation(change_date)
        self.dept_details_dept_page.change_eval_start_date(change_date, new_start)
        self.dept_details_dept_page.click_save_eval_changes(change_date)
        change_date.eval_start_date = new_start
        new_end = evaluation_utils.row_eval_end_from_eval_start(change_date.course_start_date, change_date.eval_start_date)
        change_date.eval_end_date = new_end

    def test_sort_default(self):
        self.homepage.load_page()
        self.dept_details_dept_page.sort_by_course(self.evaluations)
        self.dept_details_dept_page.wait_for_eval_rows()
        self.dept_details_dept_page.select_ignored_filter()
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_status_asc(self):
        self.dept_details_dept_page.sort_asc('Status')
        self.dept_details_dept_page.sort_by_status(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_status_desc(self):
        self.dept_details_dept_page.sort_desc('Status')
        self.dept_details_dept_page.sort_by_status(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    # TODO def test_sort_by_updated_asc(self):
    # TODO def test_sort_by_updated_desc(self):

    def test_sort_by_ccn_asc(self):
        self.dept_details_dept_page.sort_asc('Course Number')
        evals = self.dept_details_dept_page.sort_by_ccn(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        assert visible == expected

    def test_sort_by_ccn_desc(self):
        self.dept_details_dept_page.sort_desc('Course Number')
        evals = self.dept_details_dept_page.sort_by_ccn(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        assert visible == expected

    def test_sort_by_course_asc(self):
        self.dept_details_dept_page.sort_asc('Course Name')
        self.dept_details_dept_page.sort_by_course(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_course_desc(self):
        self.dept_details_dept_page.sort_desc('Course Name')
        self.dept_details_dept_page.sort_by_course(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_instr_asc(self):
        self.dept_details_dept_page.sort_asc('Instructor')
        self.dept_details_dept_page.sort_by_instructor(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_instr_desc(self):
        self.dept_details_dept_page.sort_desc('Instructor')
        self.dept_details_dept_page.sort_by_instructor(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_dept_form_asc(self):
        self.dept_details_dept_page.sort_asc('Department Form')
        self.dept_details_dept_page.sort_by_dept_form(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_dept_form_desc(self):
        self.dept_details_dept_page.sort_desc('Department Form')
        self.dept_details_dept_page.sort_by_dept_form(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_eval_type_asc(self):
        self.dept_details_dept_page.sort_asc('Evaluation Type')
        self.dept_details_dept_page.sort_by_eval_type(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_eval_type_desc(self):
        self.dept_details_dept_page.sort_desc('Evaluation Type')
        self.dept_details_dept_page.sort_by_eval_type(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_eval_start_asc(self):
        self.dept_details_dept_page.sort_asc('Evaluation Period')
        self.dept_details_dept_page.sort_by_eval_period(self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    def test_sort_by_eval_start_desc(self):
        self.dept_details_dept_page.sort_desc('Evaluation Period')
        self.dept_details_dept_page.sort_by_eval_period(self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(self.evaluations)
        assert visible == expected

    # TODO Filter testing

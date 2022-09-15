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
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
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
    dept = utils.get_dept('Ancient Greek and Roman Studies')
    utils.reset_test_data(term)
    evaluations = evaluation_utils.get_evaluations(term, dept)
    contact = next(filter(lambda u: (len(u.dept_roles) == 1), dept.users))

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    # TERM LOCK / UNLOCK

    def test_status_board_lock(self):
        self.status_board_admin_page.load_page()
        if not self.status_board_admin_page.is_current_term_locked():
            self.status_board_admin_page.lock_current_term()

    def test_verify_locked_admin_edits(self):
        self.status_board_admin_page.click_dept_link(self.dept)
        self.status_board_admin_page.wait_for_element(CourseDashboardEditsPage.ADD_SECTION_BUTTON, utils.get_medium_timeout())
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_verify_no_locked_dept_edits(self):
        self.status_board_admin_page.log_out()
        self.login_page.dev_auth(self.contact)
        self.dept_details_dept_page.wait_for_eval_rows()
        assert not self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_status_board_unlock(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.unlock_current_term()

    def test_verify_unlocked_admin_edits(self):
        self.status_board_admin_page.click_dept_link(self.dept)
        self.status_board_admin_page.wait_for_element(CourseDashboardEditsPage.ADD_SECTION_BUTTON, utils.get_short_timeout())
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_verify_unlocked_dept_edits(self):
        self.status_board_admin_page.log_out()
        self.login_page.dev_auth(self.contact)
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

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
        new_end = evaluation_utils.row_eval_end_from_eval_start(change_date.course_start_date, change_date.eval_start_date,
                                                                change_date.course_end_date)
        change_date.eval_end_date = new_end

    def test_sort_default(self):
        self.homepage.load_page()
        evals = self.dept_details_dept_page.sort_by_course(self.dept, self.evaluations)
        self.dept_details_dept_page.wait_for_eval_rows()
        self.dept_details_dept_page.select_ignored_filter()
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        missing = [x for x in expected if x not in visible]
        app.logger.info(f'Missing {missing}')
        unexpected = [x for x in visible if x not in expected]
        app.logger.info(f'Unexpected {unexpected}')
        assert visible == expected

    def test_sort_by_status_asc(self):
        self.dept_details_dept_page.sort_asc('Status')
        evals = self.dept_details_dept_page.sort_by_status(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_status_desc(self):
        self.dept_details_dept_page.sort_desc('Status')
        evals = self.dept_details_dept_page.sort_by_status(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    # TODO def test_sort_by_updated_asc(self):
    # TODO def test_sort_by_updated_desc(self):

    def test_sort_by_ccn_asc(self):
        self.dept_details_dept_page.sort_asc('Course Number')
        evals = self.dept_details_dept_page.sort_by_ccn(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_ccn_desc(self):
        self.dept_details_dept_page.sort_desc('Course Number')
        evals = self.dept_details_dept_page.sort_by_ccn(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_course_asc(self):
        self.dept_details_dept_page.sort_asc('Course Name')
        evals = self.dept_details_dept_page.sort_by_course(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_course_desc(self):
        self.dept_details_dept_page.sort_desc('Course Name')
        evals = self.dept_details_dept_page.sort_by_course(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_instr_asc(self):
        self.dept_details_dept_page.sort_asc('Instructor')
        evals = self.dept_details_dept_page.sort_by_instructor(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_instr_desc(self):
        self.dept_details_dept_page.sort_desc('Instructor')
        evals = self.dept_details_dept_page.sort_by_instructor(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_dept_form_asc(self):
        self.dept_details_dept_page.sort_asc('Department Form')
        evals = self.dept_details_dept_page.sort_by_dept_form(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_dept_form_desc(self):
        self.dept_details_dept_page.sort_desc('Department Form')
        evals = self.dept_details_dept_page.sort_by_dept_form(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_eval_type_asc(self):
        self.dept_details_dept_page.sort_asc('Evaluation Type')
        evals = self.dept_details_dept_page.sort_by_eval_type(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_eval_type_desc(self):
        self.dept_details_dept_page.sort_desc('Evaluation Type')
        evals = self.dept_details_dept_page.sort_by_eval_type(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_eval_start_asc(self):
        self.dept_details_dept_page.sort_asc('Evaluation Period')
        evals = self.dept_details_dept_page.sort_by_eval_period(self.dept, self.evaluations)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    def test_sort_by_eval_start_desc(self):
        self.dept_details_dept_page.sort_desc('Evaluation Period')
        evals = self.dept_details_dept_page.sort_by_eval_period(self.dept, self.evaluations, reverse=True)
        visible = self.dept_details_dept_page.visible_sorted_eval_data()
        expected = self.dept_details_dept_page.sorted_eval_data(evals)
        if visible != expected:
            app.logger.info(f'Visible {visible}')
            app.logger.info(f'Expected {expected}')
        assert visible == expected

    # EVALUATION FILTERING

    def test_filter_by_ccn(self):
        evaluation = next(filter(lambda e: not e.x_listing_ccns and not e.room_share_ccns, self.evaluations))
        self.dept_details_dept_page.filter_rows(evaluation.ccn)
        self.dept_details_dept_page.wait_for_eval_row(evaluation)
        app.logger.info(f'Visible eval rows {self.dept_details_dept_page.visible_evaluation_rows()}')
        assert len(self.dept_details_dept_page.visible_evaluation_rows()) == 1

    def test_filter_x_listing(self):
        evaluation = next(filter(lambda e: (e.x_listing_ccns or e.room_share_ccns), self.evaluations))
        listings = list(filter(lambda e: (evaluation.ccn in (e.x_listing_ccns or e.room_share_ccns)), self.evaluations))
        self.dept_details_dept_page.filter_rows(evaluation.ccn)
        self.dept_details_dept_page.wait_for_eval_row(evaluation)
        app.logger.info(f'Visible eval rows {self.dept_details_dept_page.visible_evaluation_rows()}')
        assert len(self.dept_details_dept_page.visible_evaluation_rows()) == (1 + len(listings))

    def test_filter_by_course_code(self):
        evaluation = next(filter(lambda e: (not e.x_listing_ccns and not e.room_share_ccns), self.evaluations))
        string = f'{evaluation.subject} {evaluation.catalog_id}'
        self.dept_details_dept_page.filter_rows(string)
        expected = list(filter(lambda e: string in f'{e.subject} {e.catalog_id}', self.evaluations))
        app.logger.info(f'Visible eval rows {self.dept_details_dept_page.visible_evaluation_rows()}')
        assert len(self.dept_details_dept_page.visible_evaluation_rows()) == len(expected)

    def test_filter_by_instr_name(self):
        evaluation = next(filter(lambda e: e.instructor.uid, self.evaluations))
        evaluations = list(filter(lambda e: e.instructor.uid == evaluation.instructor.uid, self.evaluations))
        string = f'{evaluation.instructor.first_name} {evaluation.instructor.last_name}'
        self.dept_details_dept_page.filter_rows(string)
        app.logger.info(f'Visible eval rows {self.dept_details_dept_page.visible_evaluation_rows()}')
        assert len(self.dept_details_dept_page.visible_evaluation_rows()) == len(evaluations)

    def test_filter_by_period(self):
        evaluation = next(filter(lambda e: e.eval_start_date, self.evaluations))
        evaluations = list(filter(lambda e: e.eval_start_date == evaluation.eval_start_date, self.evaluations))
        for ev in evaluations:
            app.logger.info(f'{ev.ccn} {ev.instructor.uid} {ev.eval_start_date}')
        string = f"{evaluation.eval_start_date.strftime('%m/%d')}"
        self.dept_details_dept_page.filter_rows(string)
        app.logger.info(f'Visible eval rows {self.dept_details_dept_page.visible_evaluation_rows()}')
        assert len(self.dept_details_dept_page.visible_evaluation_rows()) == len(evaluations)

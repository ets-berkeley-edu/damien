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
import time

from flask import current_app as app
from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvaluationManagement:
    term = utils.get_current_term()
    utils.reset_test_data(term)
    all_contacts = utils.get_all_users()

    dept_1 = utils.get_test_dept_1(all_contacts)
    dept_1.evaluations = evaluation_utils.get_evaluations(term, dept_1)
    dept_2 = utils.get_test_dept_2(all_contacts)
    dept_2.evaluations = evaluation_utils.get_evaluations(term, dept_2)

    instructor = utils.get_test_user()
    dept_forms = evaluation_utils.get_all_dept_forms()
    midterm_form = next(filter(lambda form: (form.name.endswith('_MID')), dept_forms))
    eval_types = evaluation_utils.get_all_eval_types()

    eval_sans_instr = next(filter(lambda row: (row.instructor.uid is None), dept_1.evaluations))
    eval_sans_form = next(filter(lambda row: (row.dept_form is None), dept_1.evaluations))
    eval_sans_type = next(filter(lambda row: (row.instructor.uid and row.eval_type is None), dept_1.evaluations))

    confirmed = []

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_list_mgmt_page(self):
        self.homepage.load_page()
        self.status_board_admin_page.click_list_mgmt()

    def test_ensure_no_midterm_form(self):
        self.midterm_form = DepartmentForm(f'{self.dept_forms[-1]}_MID')
        if self.midterm_form.name in self.list_mgmt_page.visible_dept_form_names():
            self.list_mgmt_page.delete_dept_form(self.midterm_form)

    def test_status_board_lock(self):
        self.status_board_admin_page.load_page()
        if not self.status_board_admin_page.is_current_term_locked():
            self.status_board_admin_page.lock_current_term()

    def test_verify_locked_admin_edits(self):
        self.status_board_admin_page.click_dept_link(self.dept_1)
        self.status_board_admin_page.wait_for_element(CourseDashboardEditsPage.ADD_SECTION_BUTTON, utils.get_medium_timeout())
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_verify_no_locked_dept_edits(self):
        self.status_board_admin_page.log_out()
        self.login_page.dev_auth(self.dept_1.users[0])
        self.dept_details_dept_page.wait_for_eval_rows()
        assert not self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_status_board_unlock(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.unlock_current_term()

    def test_verify_unlocked_admin_edits(self):
        self.status_board_admin_page.click_dept_link(self.dept_1)
        self.status_board_admin_page.wait_for_element(CourseDashboardEditsPage.ADD_SECTION_BUTTON, utils.get_short_timeout())
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_verify_unlocked_dept_edits(self):
        self.status_board_admin_page.log_out()
        self.login_page.dev_auth(self.dept_1.users[0])
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_details_dept_page.element(CourseDashboardEditsPage.ADD_SECTION_BUTTON).is_enabled()

    def test_admin_log_in(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_dept_link(self.dept_1)

    def test_add_instructor(self):
        instructor = utils.get_test_user()
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_instr)
        self.dept_details_admin_page.enter_instructor(self.eval_sans_instr, instructor)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_instr)
        self.eval_sans_instr.instructor = instructor
        self.dept_details_admin_page.wait_for_eval_rows()
        assert instructor.uid in self.dept_details_admin_page.eval_instructor(self.eval_sans_instr)

    def test_add_dept_form(self):
        form = self.dept_forms[1]
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_form)
        self.dept_details_admin_page.change_dept_form(self.eval_sans_form, form)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_form)
        self.eval_sans_form.dept_form = form.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert form.name in self.dept_details_admin_page.eval_dept_form(self.eval_sans_form)

    def test_revert_dept_form(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_form)
        self.dept_details_admin_page.change_dept_form(self.eval_sans_form)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_form)
        self.eval_sans_form.dept_form = None
        self.dept_details_admin_page.wait_for_eval_rows()
        assert not self.dept_details_admin_page.eval_dept_form(self.eval_sans_form)

    def test_change_dept_form(self):
        form = self.dept_forms[-1]
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_form)
        self.dept_details_admin_page.change_dept_form(self.eval_sans_form, form)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_form)
        self.eval_sans_form.dept_form = form.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert form.name in self.dept_details_admin_page.eval_dept_form(self.eval_sans_form)

    def test_eval_types_available(self):
        e = next(filter(lambda row: row.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        eval_names = list(map(lambda ev: ev.name, self.eval_types))
        eval_names.append('Revert')
        eval_names.sort()
        visible = self.dept_details_admin_page.visible_eval_type_options()
        visible.sort()
        assert visible == eval_names

    def test_add_eval_type(self):
        eval_type = self.eval_types[-1]
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_type)
        self.dept_details_admin_page.change_eval_type(self.eval_sans_type, eval_type)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_type)
        self.eval_sans_type.eval_type = eval_type.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(self.eval_sans_type)

    def test_revert_eval_type(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_type)
        self.dept_details_admin_page.change_eval_type(self.eval_sans_type)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_type)
        self.eval_sans_type.eval_type = None
        self.dept_details_admin_page.wait_for_eval_rows()
        assert not self.dept_details_admin_page.eval_type(self.eval_sans_type)

    def test_change_eval_type(self):
        eval_type = self.eval_types[1]
        self.dept_details_admin_page.click_edit_evaluation(self.eval_sans_type)
        self.dept_details_admin_page.change_eval_type(self.eval_sans_type, eval_type)
        self.dept_details_admin_page.click_save_eval_changes(self.eval_sans_type)
        self.eval_sans_type.eval_type = eval_type.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(self.eval_sans_type)

    def test_change_start_date(self):
        e = self.dept_1.evaluations[0]
        e.eval_start_date = e.eval_start_date - timedelta(days=1)
        e.eval_end_date = evaluation_utils.row_eval_end_from_eval_start(e.course_start_date, e.eval_start_date, e.course_end_date)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, e.eval_start_date)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        expected = f"{e.eval_start_date.strftime('%m/%d/%y')} - {e.eval_end_date.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_admin_page.eval_period_dates(e)

    def test_remove_start_date(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e)
        self.dept_details_admin_page.hit_escape()
        self.dept_details_admin_page.wait_for_element(CourseDashboardEditsPage.EVAL_CHANGE_START_REQ_MSG, utils.get_short_timeout())

    def test_duplicate_section_new_instructor_and_eval_type(self):
        instructor = utils.get_test_user()
        eval_type = next(filter(lambda t: t.name == 'WRIT', self.eval_types))
        e = next(filter(lambda ev: ev.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_cancel_eval_changes()
        e_dupe = self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations, instructor=instructor,
                                                                eval_type=eval_type)
        self.dept_details_admin_page.wait_for_eval_rows()
        els = self.dept_details_admin_page.rows_of_evaluation(e)
        assert len(els) == 1
        els = self.dept_details_admin_page.rows_of_evaluation(e_dupe)
        assert len(els) == 1

    def test_verify_no_midterm_if_no_form(self):
        e = next(filter(lambda ev: ev.dept_form == self.dept_forms[-1].name, self.dept_1.evaluations))
        self.dept_details_admin_page.click_eval_checkbox(e)
        self.dept_details_admin_page.wait_for_element_and_click(CourseDashboardEditsPage.DUPE_BUTTON)
        assert not self.dept_details_admin_page.is_present(CourseDashboardEditsPage.USE_MIDTERM_FORM_CBX)

    def test_ensure_dept_form(self):
        self.dept_details_admin_page.hit_escape()
        self.dept_details_admin_page.click_list_mgmt()
        if not self.midterm_form:
            self.midterm_form = DepartmentForm(f'{self.dept_forms[-1]}_MID')
            self.list_mgmt_page.add_dept_form(self.midterm_form)

    def test_duplicate_section_midterm(self):
        e = self.dept_1.evaluations[1]
        date = e.course_end_date - timedelta(days=3)
        form = next(filter(lambda f: (f.name == self.midterm_form.name.replace('_MID', '')), self.dept_forms))
        self.dept_details_admin_page.load_dept_page(self.dept_1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_dept_form(e, form)
        self.dept_details_admin_page.click_save_eval_changes(e)
        e.dept_form = form.name
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations, midterm=True, start_date=date)
        self.dept_details_admin_page.wait_for_eval_rows()
        els = self.dept_details_admin_page.rows_of_evaluation(e)
        assert len(els) == 2
        midterm_rows = list(filter(lambda el: (self.midterm_form.name in el.text), els))
        assert len(midterm_rows) == 1
        date_rows = list(filter(lambda el: (date.strftime('%m/%d/%y') in el.text), els))
        assert len(date_rows) == 1

    def test_add_existing_supp_section(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.click_add_section()
        self.dept_details_admin_page.enter_section(e.ccn)
        self.dept_details_admin_page.wait_for_validation_error('already present on page')

    def test_add_invalid_supp_section(self):
        self.dept_details_admin_page.click_cancel_lookup_section()
        self.dept_details_admin_page.click_add_section()
        self.dept_details_admin_page.look_up_section('99999')
        self.dept_details_admin_page.wait_for_validation_error('Invalid course number')
        self.dept_details_admin_page.wait_for_element(CourseDashboardEditsPage.SECTION_NOT_FOUND_MSG, utils.get_short_timeout())

    def test_add_supp_section(self):
        self.dept_details_admin_page.click_cancel_lookup_section()
        e = next(filter(lambda ev: ev.instructor.uid and ev.dept_form and ev.eval_type, self.dept_2.evaluations))
        self.dept_details_admin_page.click_add_section()
        self.dept_details_admin_page.look_up_section(e.ccn)
        self.dept_details_admin_page.click_confirm_add_section()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.wait_for_eval_row(e)
        self.dept_1.evaluations.append(e)

    def test_set_review_status_bulk(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_mark_for_review([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_review_status_single(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.FOR_REVIEW)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.FOR_REVIEW
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_confirmed_status_bulk(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_mark_as_confirmed([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_confirmed_status_single(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.CONFIRMED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.CONFIRMED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_ignored_status_bulk(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_ignore([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.select_ignored_filter()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_ignored_status_single(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.IGNORED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.select_ignored_filter()
        e.status = EvaluationStatus.IGNORED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_unmarked_status_bulk(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.FOR_REVIEW), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_unmark([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_unmarked_status_single(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.CONFIRMED), self.dept_1.evaluations))
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.UNMARKED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.UNMARKED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_filter_review_status_only(self):
        for_review = list(filter(lambda e: (e.status == EvaluationStatus.FOR_REVIEW), self.dept_1.evaluations))
        for_review = list(map(lambda e: e.ccn, for_review))
        self.dept_details_admin_page.select_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        visible = self.dept_details_admin_page.visible_eval_data()
        visible = list(map(lambda e: e['ccn'], visible))
        assert visible == for_review

    def test_filter_confirmed_status_only(self):
        confirmed = list(filter(lambda e: (e.status == EvaluationStatus.CONFIRMED), self.dept_1.evaluations))
        confirmed = list(map(lambda e: e.ccn, confirmed))
        self.dept_details_admin_page.select_confirmed_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        visible = self.dept_details_admin_page.visible_eval_data()
        visible = list(map(lambda e: e['ccn'], visible))
        assert visible == confirmed

    def test_filter_ignored_status_only(self):
        ignored = list(filter(lambda e: (e.status == EvaluationStatus.IGNORED), self.dept_1.evaluations))
        ignored = list(map(lambda e: e.ccn, ignored))
        self.dept_details_admin_page.select_ignored_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        visible = self.dept_details_admin_page.visible_eval_data()
        visible = list(map(lambda e: e['ccn'], visible))
        ignored.sort()
        visible.sort()
        assert visible == ignored

    def test_filter_unmarked_status_only(self):
        unmarked = list(filter(lambda e: (e.status == EvaluationStatus.UNMARKED), self.dept_1.evaluations))
        unmarked = list(map(lambda e: e.ccn, unmarked))
        unmarked.sort()
        app.logger.info(f'Expected UNMARKED {unmarked}')
        self.dept_details_admin_page.select_unmarked_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        visible = self.dept_details_admin_page.visible_eval_data()
        visible = list(map(lambda e: e['ccn'], visible))
        visible.sort()
        app.logger.info(f'Visible UNMARKED {visible}')
        assert visible == unmarked

    def test_confirm_complete_evals(self):
        evals = evaluation_utils.get_evaluations(self.term, self.dept_1)
        self.dept_details_admin_page.load_dept_page(self.dept_1)
        self.dept_details_admin_page.select_unmarked_filter()
        self.dept_details_admin_page.select_review_filter()
        self.dept_details_admin_page.select_confirmed_filter()
        self.dept_details_admin_page.select_ignored_filter()
        for row in evals:
            if row.instructor.uid and row.dept_form and row.eval_type:
                self.dept_details_admin_page.click_eval_checkbox(row)
        self.dept_details_admin_page.click_bulk_done_button()
        time.sleep(4)

    def test_publish(self):
        evals = evaluation_utils.get_evaluations(self.term, self.dept_1)
        confirmed = list(filter(lambda ev: (ev.status == EvaluationStatus.CONFIRMED), evals))
        self.confirmed.extend(confirmed)
        self.publish_page.load_page()
        self.publish_page.download_export_csvs()

    def test_courses(self):
        expected = utils.expected_courses(self.confirmed)
        actual = self.publish_page.parse_csv('courses')
        utils.verify_actual_matches_expected(actual, expected)

    def test_course_instructors(self):
        expected = utils.expected_course_instructors(self.confirmed)
        actual = self.publish_page.parse_csv('course_instructors')
        current_term_rows = list(filter(lambda r: (self.term.prefix in r['COURSE_ID']), actual))
        utils.verify_actual_matches_expected(current_term_rows, expected)

    def test_instructors(self):
        expected = utils.expected_instructors(self.confirmed)
        actual = self.publish_page.parse_csv('instructors')
        utils.verify_actual_matches_expected(actual, expected)

    def test_course_supervisors(self):
        expected = utils.expected_course_supervisors(self.confirmed, self.all_contacts)
        actual = self.publish_page.parse_csv('course_supervisors')
        utils.verify_actual_matches_expected(actual, expected)

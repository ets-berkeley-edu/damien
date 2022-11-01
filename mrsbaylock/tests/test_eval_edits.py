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

from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects', scope='class')
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

    dept_1.evaluations[2] = dept_1.evaluations[2]
    eval_sans_form = next(filter(lambda row: (row.dept_form is None), dept_1.evaluations))

    confirmed = []

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_ensure_no_midterm_form(self):
        self.homepage.load_page()
        self.status_board_admin_page.click_list_mgmt()
        self.midterm_form = DepartmentForm(f'{self.dept_forms[-1]}_MID')
        if self.midterm_form.name in self.list_mgmt_page.visible_dept_form_names():
            self.list_mgmt_page.delete_dept_form(self.midterm_form)

    def test_admin_dept_page(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.click_dept_link(self.dept_1)
        self.dept_details_admin_page.wait_for_eval_rows()

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
        form = next(filter(lambda f: '_MID' not in f.name, self.dept_forms))
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
        self.dept_details_admin_page.click_edit_evaluation(self.dept_1.evaluations[2])
        self.dept_details_admin_page.change_eval_type(self.dept_1.evaluations[2], eval_type)
        self.dept_details_admin_page.click_save_eval_changes(self.dept_1.evaluations[2])
        self.dept_1.evaluations[2].eval_type = eval_type.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(self.dept_1.evaluations[2])

    def test_change_eval_type(self):
        eval_type = self.eval_types[-2]
        self.dept_details_admin_page.click_edit_evaluation(self.dept_1.evaluations[2])
        self.dept_details_admin_page.change_eval_type(self.dept_1.evaluations[2], eval_type)
        self.dept_details_admin_page.click_save_eval_changes(self.dept_1.evaluations[2])
        self.dept_1.evaluations[2].eval_type = eval_type.name
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(self.dept_1.evaluations[2])

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

    def test_identical_duplicate_not_allowed(self):
        e = next(filter(lambda ev: ev.dept_form and ev.instructor.uid, self.dept_1.evaluations))
        self.dept_details_admin_page.click_cancel_eval_changes()
        self.dept_details_admin_page.click_eval_checkbox(e)
        self.dept_details_admin_page.wait_for_element_and_click(CourseDashboardEditsPage.DUPE_BUTTON)
        self.dept_details_admin_page.look_up_uid(e.instructor.uid, CourseDashboardEditsPage.DUPE_SECTION_INSTR_INPUT)
        self.dept_details_admin_page.click_look_up_result(e.instructor)
        time.sleep(1)
        self.dept_details_admin_page.wait_for_page_and_click_js(CourseDashboardEditsPage.ACTION_APPLY_BUTTON)
        self.dept_details_admin_page.await_error_and_accept()

    def test_duplicate_section_new_instructor_and_eval_type(self):
        instructor = utils.get_test_user()
        eval_type = next(filter(lambda t: t.name == 'WRIT', self.eval_types))
        e = next(filter(lambda ev: ev.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.cancel_dupe()
        self.dept_details_admin_page.click_eval_checkbox(e)
        e_dupe = self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations, instructor=instructor,
                                                                eval_type=eval_type)
        self.dept_details_admin_page.wait_for_eval_rows()
        els = self.dept_details_admin_page.rows_of_evaluation(e)
        assert len(els) == 1
        els = self.dept_details_admin_page.rows_of_evaluation(e_dupe)
        assert len(els) == 1

    def test_verify_no_midterm_if_no_form(self):
        e = next(filter(lambda ev: ev.dept_form == self.eval_sans_form.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_cancel_eval_changes()
        self.dept_details_admin_page.click_eval_checkbox(e)
        self.dept_details_admin_page.wait_for_page_and_click_js(CourseDashboardEditsPage.DUPE_BUTTON)
        time.sleep(1)
        assert not self.dept_details_admin_page.is_present(CourseDashboardEditsPage.USE_MIDTERM_FORM_CBX)

    def test_ensure_dept_form(self):
        self.dept_details_admin_page.hit_escape()
        self.dept_details_admin_page.click_list_mgmt()
        if not self.midterm_form:
            self.midterm_form = DepartmentForm(f'{self.dept_forms[-1]}_MID')
            self.list_mgmt_page.add_dept_form(self.midterm_form)

    def test_duplicate_section_midterm(self):
        date = self.dept_1.evaluations[1].eval_start_date - timedelta(days=3)
        form = next(filter(lambda f: (f.name == self.midterm_form.name.replace('_MID', '')), self.dept_forms))
        self.dept_details_admin_page.load_dept_page(self.dept_1)
        self.dept_details_admin_page.click_edit_evaluation(self.dept_1.evaluations[1])
        self.dept_details_admin_page.change_dept_form(self.dept_1.evaluations[1], form)
        self.dept_details_admin_page.click_save_eval_changes(self.dept_1.evaluations[1])
        self.dept_1.evaluations[1].dept_form = form.name
        self.dept_details_admin_page.wait_for_eval_rows()
        dupe = self.dept_details_admin_page.duplicate_section(self.dept_1.evaluations[1], self.dept_1.evaluations,
                                                              midterm=True, start_date=date)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert len(self.dept_details_admin_page.rows_of_evaluation(self.dept_1.evaluations[1])) == 1
        assert len(self.dept_details_admin_page.rows_of_evaluation(dupe)) == 1

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
        time.sleep(utils.get_short_timeout())

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
        assert all(x in actual for x in expected)

    def test_course_supervisors(self):
        expected = utils.expected_course_supervisors(self.confirmed, self.all_contacts)
        actual = self.publish_page.parse_csv('course_supervisors')
        utils.verify_actual_matches_expected(actual, expected)

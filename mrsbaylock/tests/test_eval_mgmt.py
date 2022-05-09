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

from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvaluationManagement:
    term = utils.get_current_term()
    dept_1 = utils.get_test_dept_1()
    utils.reset_test_data(term, dept_1)
    dept_1.evaluations = evaluation_utils.get_evaluations(term, dept_1)

    instructor = utils.get_test_user()
    dept_forms = evaluation_utils.get_all_dept_forms()
    midterm_form = next(filter(lambda form: (form.name.endswith('_MID')), dept_forms))
    eval_types = evaluation_utils.get_all_eval_types()

    dept_2 = utils.get_test_dept_2()
    dept_2.evaluations = evaluation_utils.get_evaluations(term, dept_2)

    def test_list_mgmt_page(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()

    def test_ensure_dept_form(self):
        if not self.midterm_form:
            self.midterm_form = DepartmentForm(f'{self.dept_forms[0]}_MID')
            self.list_mgmt_page.add_dept_form(self.midterm_form)

    def test_status_board(self):
        self.list_mgmt_page.click_status_board()
        self.status_board_admin_page.click_dept_link(self.dept_1)

    def test_no_changing_instructor(self):
        e = next(filter(lambda row: row.instructor.uid, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        # TODO verify no elements present to set or unset the instructor

    def test_add_dept_form(self):
        form = self.dept_forms[-1]
        e = next(filter(lambda row: (row.dept_form is None), self.dept_1.evaluations))
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_dept_form(e, form)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert form.name in self.dept_details_admin_page.eval_dept_form(e)

    def test_change_dept_form(self):
        form = self.dept_forms[1]
        e = next(filter(lambda row: row.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_dept_form(e, form)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert form.name in self.dept_details_admin_page.eval_dept_form(e)

    def test_revert_dept_form(self):
        e = next(filter(lambda row: row.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_dept_form(e)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.dept_form in self.dept_details_admin_page.eval_dept_form(e)

    def test_eval_types_available(self):
        e = next(filter(lambda row: row.dept_form, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        eval_names = list(map(lambda ev: ev.name, self.eval_types))
        eval_names.append('None')
        eval_names.sort()
        visible = self.dept_details_admin_page.visible_eval_type_options()
        visible.sort()
        assert visible == eval_names

    def test_add_eval_type(self):
        eval_type = self.eval_types[-1]
        e = next(filter(lambda row: (row.eval_type is None), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_type(e, eval_type)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(e)

    def test_change_eval_type(self):
        eval_type = self.eval_types[1]
        e = next(filter(lambda row: row.eval_type, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_type(e, eval_type)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert eval_type.name in self.dept_details_admin_page.eval_type(e)

    def test_revert_eval_type(self):
        e = next(filter(lambda row: row.eval_type, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_type(e)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.eval_type in self.dept_details_admin_page.eval_type(e)

    def test_change_start_date(self):
        e = self.dept_1.evaluations[0]
        e.eval_start_date = e.eval_start_date + timedelta(days=1)
        e.eval_end_date = evaluation_utils.row_eval_end_from_eval_start(e)
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

    def test_duplicate_section(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations)
        self.dept_details_admin_page.wait_for_eval_rows()
        els = self.dept_details_admin_page.rows_of_evaluation(e)
        assert len(els) == 2

    def test_duplicate_section_midterm(self):
        e = self.dept_1.evaluations[1]
        date = e.course_end_date - timedelta(days=30)
        form = next(filter(lambda f: f.name == self.midterm_form.name.replace('_MID', ''), self.dept_forms))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_dept_form(e, form)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations, True, date)
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
        e = self.dept_2.evaluations[0]
        self.dept_details_admin_page.click_add_section()
        self.dept_details_admin_page.look_up_section(e.ccn)
        self.dept_details_admin_page.click_confirm_add_section()
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.wait_for_eval_row(e)

    def test_set_review_status_bulk(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_mark_for_review([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_review_status_single(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.FOR_REVIEW)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.FOR_REVIEW
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_confirmed_status_bulk(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.mark_as_confirmed([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_confirmed_status_single(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.CONFIRMED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.CONFIRMED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_ignored_status_bulk(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_ignore([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.select_ignored_filter()
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_ignored_status_single(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.IGNORED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.IGNORED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_unmarked_status_bulk(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.FOR_REVIEW), self.dept_1.evaluations))
        self.dept_details_admin_page.bulk_unmark([e])
        self.dept_details_admin_page.wait_for_eval_rows()
        assert not self.dept_details_admin_page.eval_status(e)

    def test_set_unmarked_status_single(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.FOR_REVIEW), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.select_eval_status(e, EvaluationStatus.UNMARKED)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        e.status = EvaluationStatus.UNMARKED
        assert e.status.value['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_filter_review_status_only(self):
        self.dept_details_admin_page.select_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        # TODO - verify row

    def test_filter_confirmed_status_only(self):
        self.dept_details_admin_page.select_confirmed_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        # TODO - verify row

    def test_filter_ignored_status_only(self):
        self.dept_details_admin_page.select_ignored_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_unmarked_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        # TODO - verify row

    def test_filter_unmarked_status_only(self):
        self.dept_details_admin_page.select_unmarked_filter()
        self.dept_details_admin_page.deselect_review_filter()
        self.dept_details_admin_page.deselect_confirmed_filter()
        self.dept_details_admin_page.deselect_ignored_filter()
        # TODO - verify row

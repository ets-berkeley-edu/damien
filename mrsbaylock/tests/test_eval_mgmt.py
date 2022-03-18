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

from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboards import CourseDashboards
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvaluationManagement:
    term = utils.get_current_term()
    dept_1 = utils.get_test_dept_1()
    dept_1.evaluations = utils.get_evaluations(term, dept_1)

    instructor = utils.get_test_user()
    dept_forms = utils.get_dept_forms()
    # TODO ensure midterm form exists
    eval_types = utils.get_all_eval_types()

    dept_2 = utils.get_test_dept_2()
    dept_2.evaluations = utils.get_evaluations(term, dept_2)

    utils.reset_test_data(term, dept_1)

    def test_status_page(self):
        self.homepage.load_page()
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_dept_link(self.dept_1)

    def test_add_instructor(self):
        e = next(filter(lambda row: (row.instructor.uid is None), self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_instructor(e, self.instructor)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert self.instructor.uid in self.dept_details_admin_page.eval_instructor(e)
        assert f'{self.instructor.first_name} {self.instructor.last_name}' in self.dept_details_admin_page.eval_instructor(e)
        assert self.instructor.email in self.dept_details_admin_page.eval_instructor(e)

    def test_change_instructor(self):
        e = next(filter(lambda row: row.instructor.uid, self.dept_1.evaluations))
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_instructor(e, self.instructor)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert self.instructor.uid in self.dept_details_admin_page.eval_instructor(e)
        assert f'{self.instructor.first_name} {self.instructor.last_name}' in self.dept_details_admin_page.eval_instructor(e)
        assert self.instructor.email in self.dept_details_admin_page.eval_instructor(e)

    # TODO def test_remove_instructor(self):

    # TODO def test_add_dept_form(self):
    # TODO def test_change_dept_form(self):
    # TODO def test_remove_dept_form(self):

    # TODO def test_add_eval_type(self):
    # TODO def test_change_eval_type(self):
    # TODO def test_remove_eval_type(self):

    def test_change_start_date(self):
        e = self.dept_1.evaluations[0]
        date = e.start_date + timedelta(days=1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, date)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert date.strftime('%m/%d/%Y') in self.dept_details_admin_page.eval_course_start(e)
        e.start_date = date

    def test_remove_start_date(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_start_before_term(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        date = self.term.start_date - timedelta(days=1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, date)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_start_after_term(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        start = self.term.end_date + timedelta(days=1)
        end = self.term.end_date + timedelta(days=2)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, start)
        self.dept_details_admin_page.change_eval_end_date(e, end)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_change_end_date(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        date = e.end_date - timedelta(days=1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_end_date(e, date)
        self.dept_details_admin_page.click_save_eval_changes(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert date.strftime('%m/%d/%Y') in self.dept_details_admin_page.eval_course_end(e)
        e.end_date = date

    def test_remove_end_date(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_end_date(e)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_end_before_term(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        start = self.term.end_date - timedelta(days=2)
        end = self.term.end_date - timedelta(days=1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, start)
        self.dept_details_admin_page.change_eval_end_date(e, end)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_end_after_term(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        date = self.term.end_date + timedelta(days=1)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_end_date(e, date)
        self.dept_details_admin_page.wait_for_validation_error('Date must be within current term.')

    def test_end_before_start(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        start = self.term.start_date + timedelta(days=14)
        end = self.term.start_date + timedelta(days=7)
        self.dept_details_admin_page.click_edit_evaluation(e)
        self.dept_details_admin_page.change_eval_start_date(e, start)
        self.dept_details_admin_page.change_eval_end_date(e, end)
        self.dept_details_admin_page.wait_for_validation_error('End date must be after start date.')

    def test_duplicate_section(self):
        e = self.dept_1.evaluations[0]
        self.dept_details_admin_page.click_cancel_eval_changes(e)
        self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations)
        self.dept_details_admin_page.wait_for_eval_rows()
        # TODO - verify new row

    def test_duplicate_section_midterm(self):
        e = self.dept_1.evaluations[0]
        date = e.end_date - timedelta(days=30)
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.duplicate_section(e, self.dept_1.evaluations, True, date)
        self.dept_details_admin_page.wait_for_eval_rows()
        # TODO - verify new row

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
        self.dept_details_admin_page.wait_for_element(CourseDashboards.SECTION_NOT_FOUND_MSG, utils.get_short_timeout())

    def test_add_supp_section(self):
        self.dept_details_admin_page.click_cancel_lookup_section()
        e = self.dept_2.evaluations[0]
        self.dept_details_admin_page.click_add_section()
        self.dept_details_admin_page.look_up_section(e.ccn)
        self.dept_details_admin_page.click_confirm_add_section()
        # TODO - verify new row

    def test_set_review_status(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.mark_for_review(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_confirmed_status(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.mark_as_confirmed(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        assert e.status['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_ignored_status(self):
        e = next(filter(lambda row: (row.status is None), self.dept_1.evaluations))
        self.dept_details_admin_page.ignore(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.click_ignored_filter()
        assert e.status['ui'] in self.dept_details_admin_page.eval_status(e)

    def test_set_unmarked_status(self):
        e = next(filter(lambda row: (row.status == EvaluationStatus.CONFIRMED), self.dept_1.evaluations))
        self.dept_details_admin_page.unmark(e)
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.click_ignored_filter()
        assert not self.dept_details_admin_page.eval_status(e)

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

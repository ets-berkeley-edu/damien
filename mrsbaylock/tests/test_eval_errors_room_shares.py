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

from mrsbaylock.models.user import User
from mrsbaylock.pages.publish_page import PublishPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvalErrors:

    term = utils.get_current_term()
    all_contacts = utils.get_all_users()
    dept = utils.get_dept('Environmental Science, Policy and Management', all_contacts)
    evals = evaluation_utils.get_evaluations(term, dept)
    instructor_uid = utils.get_test_user().uid
    types = evaluation_utils.get_all_eval_types()
    eval_type_1 = types[-1]
    eval_type_2 = types[-2]
    forms = evaluation_utils.get_all_dept_forms()
    dept_form_1 = forms[-1]
    dept_form_2 = forms[-2]

    share_eval = next(filter(lambda s1: (s1.room_share_ccns and not s1.x_listing_ccns), evals))
    share_dept_1 = evaluation_utils.get_section_dept(term, share_eval.ccn, all_contacts)
    share_dept_2 = evaluation_utils.get_section_dept(term, share_eval.room_share_ccns[-1], all_contacts)

    utils.reset_test_data(term)

    evals = evaluation_utils.get_evaluations(term, dept)
    for e in evals:
        if e.ccn == share_eval.ccn:
            share_eval = e

    share_eval_has_instr = True if share_eval.instructor.uid else False
    share_contact_1 = share_dept_1.users[0]
    share_start_1 = term.end_date.date() - timedelta(days=22)
    share_end_1 = evaluation_utils.row_eval_end_from_eval_start(share_eval.course_start_date, share_start_1)
    share_contact_2 = share_dept_2.users[0]
    share_start_2 = term.end_date.date() - timedelta(days=21)
    share_end_2 = evaluation_utils.row_eval_end_from_eval_start(share_eval.course_start_date, share_start_2)

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_log_out(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.log_out()

    def test_share_unmarked_dept_1_perform_edits(self):
        self.login_page.dev_auth(self.share_contact_1, self.share_dept_1)
        self.dept_details_dept_page.click_edit_evaluation(self.share_eval)
        if not self.share_eval_has_instr:
            instr = User({'uid': self.instructor_uid})
            self.dept_details_dept_page.enter_instructor(self.share_eval, instr)
        self.dept_details_dept_page.change_dept_form(self.share_eval, self.dept_form_1)
        self.dept_details_dept_page.change_eval_type(self.share_eval, self.eval_type_1)
        self.dept_details_dept_page.change_eval_start_date(self.share_eval, self.share_start_1)
        self.dept_details_dept_page.save_eval_changes(self.share_eval)

    def test_share_unmarked_dept_1_verify_edits(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_1.name in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        assert self.eval_type_1.name in self.dept_details_dept_page.eval_type(self.share_eval)
        expected = f"{self.share_start_1.strftime('%m/%d/%y')} - {self.share_end_1.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.share_eval)

    def test_share_unmarked_dept_2_verify_edits(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth(self.share_contact_2, self.share_dept_2)
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_1.name in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        assert self.eval_type_1.name in self.dept_details_dept_page.eval_type(self.share_eval)
        expected = f"{self.share_start_1.strftime('%m/%d/%y')} - {self.share_end_1.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_type(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_period_dates(self.share_eval)

    def test_share_unmarked_sl_verify_no_errors(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.wait_for_depts()
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_1) == 0
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_2) == 0
        self.dept_details_admin_page.click_publish_link()
        self.publish_page.wait_for_no_sections()

    def test_share_dept_2_set_status_confirmed(self):
        self.publish_page.log_out()
        self.login_page.dev_auth(self.share_contact_2, self.share_dept_2)
        self.dept_details_dept_page.wait_for_eval_rows()
        self.dept_details_dept_page.bulk_mark_as_confirmed([self.share_eval])

    def test_share_confirmed_dept_2_verify_edits(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_1.name in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        assert self.eval_type_1.name in self.dept_details_dept_page.eval_type(self.share_eval)
        expected = f"{self.share_start_1.strftime('%m/%d/%y')} - {self.share_end_1.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_type(self.share_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_period_dates(self.share_eval)

    def test_share_confirmed_dept_2_attempt_edits(self):
        self.dept_details_dept_page.click_edit_evaluation(self.share_eval)
        self.dept_details_dept_page.change_dept_form(self.share_eval, self.dept_form_2)
        self.dept_details_dept_page.change_eval_type(self.share_eval, self.eval_type_2)
        self.dept_details_dept_page.change_eval_start_date(self.share_eval, self.share_start_2)
        self.dept_details_dept_page.click_save_eval_changes(self.share_eval)
        self.dept_details_dept_page.wait_for_validation_error('Could not confirm evaluations with conflicting information.')

    def test_share_dept_2_set_status_to_do(self):
        self.dept_details_dept_page.hit_escape()
        self.dept_details_dept_page.bulk_mark_for_review([self.share_eval])

    def test_share_confirmed_dept_2_perform_edits(self):
        self.dept_details_dept_page.click_edit_evaluation(self.share_eval)
        self.dept_details_dept_page.change_dept_form(self.share_eval, self.dept_form_2)
        self.dept_details_dept_page.change_eval_type(self.share_eval, self.eval_type_2)
        self.dept_details_dept_page.change_eval_start_date(self.share_eval, self.share_start_2)
        self.dept_details_dept_page.save_eval_changes(self.share_eval)

    def test_share_confirmed_dept_2_verify_form_conflict(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_2.name in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        conflict_form = f'Conflicts with value {self.dept_form_1.name} from {self.share_dept_1.name} department'
        assert conflict_form in self.dept_details_dept_page.eval_dept_form(self.share_eval)

    def test_share_confirmed_dept_2_verify_type_conflict(self):
        assert self.eval_type_2.name in self.dept_details_dept_page.eval_type(self.share_eval)
        conflict_type = f'Conflicts with value {self.eval_type_1.name} from {self.share_dept_1.name} department'
        assert conflict_type in self.dept_details_dept_page.eval_type(self.share_eval)

    def test_share_confirmed_dept_2_verify_period_conflict(self):
        pd_1 = self.share_start_1.strftime('%m/%d/%y')
        expected = f"{self.share_start_2.strftime('%m/%d/%y')} - {self.share_end_2.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.share_eval)
        conflict_date = f'Conflicts with period starting {pd_1} from {self.share_dept_1.name} department'
        assert conflict_date in self.dept_details_dept_page.eval_period_dates(self.share_eval)

    def test_share_confirmed_dept_1_verify_status(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth(self.share_contact_1, self.share_dept_1)
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.share_eval.status.value['ui'].upper() in self.dept_details_admin_page.eval_status(self.share_eval)

    def test_share_confirmed_dept_1_verify_form_conflict(self):
        assert self.dept_form_1.name in self.dept_details_dept_page.eval_dept_form(self.share_eval)
        conflict_form = f'Conflicts with value {self.dept_form_2.name} from {self.share_dept_2.name} department'
        assert conflict_form in self.dept_details_dept_page.eval_dept_form(self.share_eval)

    def test_share_confirmed_dept_1_verify_type_conflict(self):
        assert self.eval_type_1.name in self.dept_details_dept_page.eval_type(self.share_eval)
        conflict_type = f'Conflicts with value {self.eval_type_2.name} from {self.share_dept_2.name} department'
        assert conflict_type in self.dept_details_dept_page.eval_type(self.share_eval)

    def test_share_confirmed_dept_1_verify_period_conflict(self):
        pd_2 = self.share_start_2.strftime('%m/%d/%y')
        expected = f"{self.share_start_1.strftime('%m/%d/%y')} - {self.share_end_1.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.share_eval)
        conflict_date = f'Conflicts with period starting {pd_2} from {self.share_dept_2.name} department'
        assert conflict_date in self.dept_details_dept_page.eval_period_dates(self.share_eval)

    def test_share_confirmed_sl_verify_dept_2_errors(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.wait_for_depts()
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_1) == 1
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_2) == 1

    def test_share_confirmed_sl_verify_form_conflict(self):
        self.status_board_admin_page.click_publish_link()
        self.publish_page.wait_for_eval_rows()
        assert self.dept_form_2.name in self.publish_page.eval_dept_form(self.share_eval)
        conflict_form = f'Conflicts with value {self.dept_form_1.name} from {self.share_dept_1.name} department'
        assert conflict_form in self.publish_page.eval_dept_form(self.share_eval)

    def test_share_confirmed_sl_verify_type_conflict(self):
        assert self.eval_type_2.name in self.publish_page.eval_type(self.share_eval)
        conflict_type = f'Conflicts with value {self.eval_type_1.name} from {self.share_dept_1.name} department'
        assert conflict_type in self.publish_page.eval_type(self.share_eval)

    def test_share_confirmed_sl_verify_period_conflict(self):
        pd_1 = self.share_start_1.strftime('%m/%d/%y')
        expected = f"{self.share_start_2.strftime('%m/%d/%y')} - {self.share_end_2.strftime('%m/%d/%y')}"
        assert expected in self.publish_page.eval_period_dates(self.share_eval)
        conflict_date = f'Conflicts with period starting {pd_1} from {self.share_dept_1.name} department'
        assert conflict_date in self.publish_page.eval_period_dates(self.share_eval)

    def test_publish_ok_while_to_do_errors(self):
        assert self.publish_page.element(PublishPage.PUBLISH_BUTTON).is_enabled()

    def test_share_sl_resolve_conflict(self):
        self.status_board_admin_page.click_dept_link(self.share_dept_2)
        self.dept_details_admin_page.click_edit_evaluation(self.share_eval)
        self.dept_details_admin_page.change_dept_form(self.share_eval, self.dept_form_1)
        self.dept_details_admin_page.change_eval_type(self.share_eval, self.eval_type_1)
        self.dept_details_admin_page.change_eval_start_date(self.share_eval, self.share_start_1)
        self.dept_details_admin_page.save_eval_changes(self.share_eval)

    def test_share_sl_confirm(self):
        self.dept_details_admin_page.bulk_mark_as_confirmed([self.share_eval])

    def test_no_errors(self):
        self.dept_details_admin_page.click_status_board()
        self.status_board_admin_page.wait_for_depts()
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_1) == 0
        assert self.status_board_admin_page.dept_errors_count(self.share_dept_2) == 0
        self.dept_details_admin_page.click_publish_link()
        self.publish_page.wait_for_no_sections()

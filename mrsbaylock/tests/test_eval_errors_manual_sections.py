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

from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.models.user import User
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvalErrors:

    term = utils.get_current_term()
    all_contacts = utils.get_all_users()
    dept_1 = utils.get_dept('Environmental Science, Policy and Management', all_contacts)
    contact_1 = dept_1.users[0]
    dept_2 = utils.get_dept('English', all_contacts)
    contact_2 = list(set(dept_2.users) - set(dept_1.users))[0]
    dept_1_evals = evaluation_utils.get_evaluations(term, dept_1)
    dept_2_evals = evaluation_utils.get_evaluations(term, dept_2)
    instructor_uid = utils.get_test_user().uid
    types = evaluation_utils.get_all_eval_types()
    eval_type_1 = types[-1]
    eval_type_2 = types[-2]
    forms = evaluation_utils.get_all_dept_forms()
    dept_form_1 = forms[-1]
    dept_form_2 = forms[-2]

    no_listings_no_shares = list(filter(lambda c: (c.instructor.uid and not c.x_listing_ccns and not c.room_share_ccns), dept_2_evals))
    manual_eval = no_listings_no_shares[0]

    utils.reset_test_data(term)

    evals = evaluation_utils.get_evaluations(term, dept_1)
    for e in evals:
        if e.ccn == manual_eval.ccn:
            manual_eval = e

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_log_out(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.log_out()

    def test_manual_section_dept_1_adds(self):
        self.login_page.dev_auth(self.contact_1, self.dept_1)
        self.dept_details_dept_page.click_add_section()
        self.dept_details_dept_page.look_up_section(self.manual_eval.ccn)
        self.dept_details_dept_page.click_confirm_add_section()
        self.dept_details_dept_page.wait_for_eval_rows()
        self.dept_details_dept_page.wait_for_eval_row(self.manual_eval)

    def test_manual_section_dept_1_edits(self):
        self.dept_details_dept_page.click_edit_evaluation(self.manual_eval)
        if not self.manual_eval.instructor.uid:
            instr = User({'uid': self.instructor_uid})
            self.dept_details_dept_page.enter_instructor(self.manual_eval, instr)
        self.dept_details_dept_page.change_dept_form(self.manual_eval, self.dept_form_2)
        self.dept_details_dept_page.change_eval_type(self.manual_eval, self.eval_type_2)
        self.dept_details_dept_page.save_eval_changes(self.manual_eval)
        self.manual_eval.dept_form = self.dept_form_2.name
        self.manual_eval.eval_type = self.eval_type_2.name

    def test_manual_section_dept_1_verify_edits(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_2.name in self.dept_details_dept_page.eval_dept_form(self.manual_eval)
        assert self.eval_type_2.name in self.dept_details_dept_page.eval_type(self.manual_eval)

    def test_manual_section_dept_2_verify_edits(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth(self.contact_2, self.dept_2)
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dept_form_2.name in self.dept_details_dept_page.eval_dept_form(self.manual_eval)
        assert self.eval_type_2.name in self.dept_details_dept_page.eval_type(self.manual_eval)

    def test_manual_section_dept_2_edits(self):
        self.dept_details_dept_page.click_edit_evaluation(self.manual_eval)
        self.dept_details_dept_page.change_dept_form(self.manual_eval, self.dept_form_1)
        self.dept_details_dept_page.change_eval_type(self.manual_eval, self.eval_type_1)
        self.dept_details_dept_page.save_eval_changes(self.manual_eval)
        self.manual_eval.dept_form = self.dept_form_1.name
        self.manual_eval.eval_type = self.eval_type_1.name

    def test_manual_section_dept_2_verify_form_conflict(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        conflict_form = f'Conflicts with value {self.dept_form_2.name} from {self.dept_1.name} department'
        assert self.dept_form_1.name in self.dept_details_dept_page.eval_dept_form(self.manual_eval)
        assert conflict_form in self.dept_details_dept_page.eval_dept_form(self.manual_eval)

    def test_manual_section_dept_2_verify_type_conflict(self):
        conflict_type = f'Conflicts with value {self.eval_type_2.name} from {self.dept_1.name} department'
        assert self.eval_type_1.name in self.dept_details_dept_page.eval_type(self.manual_eval)
        assert conflict_type in self.dept_details_dept_page.eval_type(self.manual_eval)

    def test_manual_section_dept_2_no_confirming(self):
        self.dept_details_dept_page.click_edit_evaluation(self.manual_eval)
        self.dept_details_dept_page.select_eval_status(self.manual_eval, EvaluationStatus.CONFIRMED)
        self.dept_details_dept_page.click_save_eval_changes(self.manual_eval)
        self.dept_details_dept_page.wait_for_validation_error('Could not confirm evaluations with conflicting information')

    def test_manual_section_dept_2_resolve_conflict(self):
        self.dept_details_dept_page.hit_escape()
        self.dept_details_dept_page.change_dept_form(self.manual_eval, self.dept_form_2)
        self.dept_details_dept_page.change_eval_type(self.manual_eval, self.eval_type_2)
        self.dept_details_dept_page.save_eval_changes(self.manual_eval)
        self.manual_eval.dept_form = self.dept_form_2.name
        self.manual_eval.eval_type = self.eval_type_2.name

    def test_manual_section_dept_2_no_form_conflict(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        conflict_form = f'Conflicts with value {self.dept_form_2.name} from {self.dept_1.name} department'
        assert self.dept_form_2.name in self.dept_details_dept_page.eval_dept_form(self.manual_eval)
        assert conflict_form not in self.dept_details_dept_page.eval_dept_form(self.manual_eval)

    def test_manual_section_dept_2_no_type_conflict(self):
        conflict_type = f'Conflicts with value {self.eval_type_2.name} from {self.dept_1.name} department'
        assert self.eval_type_2.name in self.dept_details_dept_page.eval_type(self.manual_eval)
        assert conflict_type not in self.dept_details_dept_page.eval_type(self.manual_eval)

    def test_manual_section_dept_2_confirms(self):
        self.dept_details_dept_page.click_edit_evaluation(self.manual_eval)
        self.dept_details_dept_page.select_eval_status(self.manual_eval, EvaluationStatus.CONFIRMED)
        self.dept_details_dept_page.save_eval_changes(self.manual_eval)

    def test_no_errors(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.wait_for_depts()
        assert self.status_board_admin_page.dept_errors_count(self.dept_1) == 0
        assert self.status_board_admin_page.dept_errors_count(self.dept_2) == 0
        self.status_board_admin_page.click_publish_link()
        self.publish_page.wait_for_no_sections()

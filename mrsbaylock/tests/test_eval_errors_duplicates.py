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

import copy
from datetime import timedelta
import time

from flask import current_app as app
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvalErrors:

    term = utils.get_current_term()
    all_contacts = utils.get_all_users()
    dept = utils.get_dept('Environmental Science, Policy and Management', all_contacts)
    contact = dept.users[0]
    evals = evaluation_utils.get_evaluations(term, dept)
    types = evaluation_utils.get_all_eval_types()
    eval_type_1 = types[-1]
    eval_type_2 = types[-2]
    forms = evaluation_utils.get_all_dept_forms()
    dept_form_1 = forms[-1]
    dept_form_2 = forms[-2]
    no_listings_no_shares = list(
        filter(lambda c: (c.instructor.uid and not c.x_listing_ccns and not c.room_share_ccns), evals))
    duped_eval = no_listings_no_shares[1]

    utils.reset_test_data(term)
    evals = evaluation_utils.get_evaluations(term, dept)
    for e in evals:
        duped_eval = e
    dupe_eval = copy.deepcopy(duped_eval)

    app.logger.info(f'Department is {dept.name}, UID {contact.uid}')
    app.logger.info(f'Duplicated CCN is {duped_eval.ccn}')

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_log_out(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.log_out()

    def test_dupe_section(self):
        self.login_page.dev_auth(self.contact, self.dept)
        self.dept_details_dept_page.duplicate_section(self.duped_eval, self.evals)
        time.sleep(1)
        assert len(self.dept_details_dept_page.rows_of_evaluation(self.duped_eval)) == 2

    def test_dupe_section_edits(self):
        self.dept_details_dept_page.click_edit_evaluation(self.dupe_eval)
        form = next(filter(lambda f: self.dupe_eval.dept_form != f.name, self.forms))
        self.dept_details_dept_page.change_dept_form(self.dupe_eval, form)
        eval_type = next(filter(lambda t: not self.dupe_eval.eval_type, self.types))
        self.dept_details_dept_page.change_eval_type(self.dupe_eval, eval_type)
        pd_start = self.term.end_date.date() - timedelta(days=22)
        self.dept_details_dept_page.change_eval_start_date(self.dupe_eval, pd_start)
        self.dept_details_dept_page.save_eval_changes(self.dupe_eval)
        self.dupe_eval.dept_form = form.name
        self.dupe_eval.eval_type = eval_type.name
        self.dupe_eval.eval_start_date = pd_start
        self.dupe_eval.eval_end_date = evaluation_utils.row_eval_end_from_eval_start(self.dupe_eval.course_start_date,
                                                                                     pd_start, self.dupe_eval.course_end_date)

    def test_dupe_unmarked_verify_edits(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        assert self.dupe_eval.dept_form in self.dept_details_dept_page.eval_dept_form(self.dupe_eval)
        assert self.dupe_eval.eval_type in self.dept_details_dept_page.eval_type(self.dupe_eval)
        expected = f"{self.dupe_eval.eval_start_date.strftime('%m/%d/%y')} - {self.dupe_eval.eval_end_date.strftime('%m/%d/%y')}"
        assert expected in self.dept_details_dept_page.eval_period_dates(self.dupe_eval)

    def test_dupe_unmarked_no_conflicts(self):
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_dept_form(self.dupe_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_type(self.dupe_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_period_dates(self.dupe_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_dept_form(self.duped_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_type(self.duped_eval)
        assert 'Conflicts with' not in self.dept_details_dept_page.eval_period_dates(self.duped_eval)

    def test_dupe_set_status_review(self):
        self.dept_details_dept_page.bulk_mark_for_review([self.duped_eval])

    def test_dupe_to_do_verify_form_conflict(self):
        self.dept_details_dept_page.wait_for_eval_rows()
        conflict_form = f'Conflicts with value {self.dupe_eval.dept_form} from {self.dept.name} department'
        assert conflict_form in self.dept_details_dept_page.eval_dept_form(self.duped_eval)
        conflict_form = f'Conflicts with value {self.duped_eval.dept_form} from {self.dept.name} department'
        assert conflict_form in self.dept_details_dept_page.eval_dept_form(self.dupe_eval)

    def test_dupe_to_do_verify_type_conflict(self):
        conflict_type = f'Conflicts with value {self.dupe_eval.eval_type} from {self.dept.name} department'
        assert conflict_type in self.dept_details_dept_page.eval_type(self.duped_eval)
        conflict_type = f'Conflicts with value {self.duped_eval.eval_type} from {self.dept.name} department'
        assert conflict_type in self.dept_details_dept_page.eval_type(self.dupe_eval)

    def test_dupe_to_do_verify_date_conflict(self):
        start = self.dupe_eval.eval_start_date.strftime('%m/%d/%y')
        conflict_date = f'Conflicts with period starting {start} from {self.dept.name} department'
        assert conflict_date in self.dept_details_dept_page.eval_period_dates(self.duped_eval)
        start = self.duped_eval.eval_start_date.strftime('%m/%d/%y')
        conflict_date = f'Conflicts with period starting {start} from {self.dept.name} department'
        assert conflict_date in self.dept_details_dept_page.eval_period_dates(self.dupe_eval)

    def test_dupe_no_confirming(self):
        self.dept_details_dept_page.click_edit_evaluation(self.dupe_eval)
        self.dept_details_dept_page.select_eval_status(self.dupe_eval, EvaluationStatus.CONFIRMED)
        self.dept_details_dept_page.click_save_eval_changes(self.dupe_eval)
        self.dept_details_dept_page.wait_for_validation_error(
            'Could not confirm evaluations with conflicting information')

    def test_dupe_sl_resolve_conflict(self):
        self.dept_details_dept_page.log_out()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_publish_link()
        self.status_board_admin_page.click_dept_link(self.dept)
        self.dept_details_admin_page.click_edit_evaluation(self.dupe_eval)
        form = next(filter(lambda f: f.name == self.duped_eval.dept_form, self.dept_forms))
        eval_type = next(filter(lambda t: t.name == self.duped_eval.eval_type, self.types))
        self.dept_details_admin_page.change_dept_form(self.dupe_eval, form)
        self.dept_details_admin_page.change_eval_type(self.dupe_eval, eval_type)
        self.dept_details_admin_page.change_eval_start_date(self.dupe_eval, self.duped_eval.eval_start_date)
        self.dept_details_admin_page.save_eval_changes(self.dupe_eval)

    def test_dupe_sl_confirm(self):
        self.dept_details_admin_page.bulk_mark_as_confirmed([self.dupe_eval])

    def test_no_errors(self):
        self.dept_details_admin_page.click_status_board()
        self.status_board_admin_page.wait_for_depts()
        assert self.status_board_admin_page.dept_errors_count(self.dept) == 0
        self.dept_details_admin_page.click_publish_link()
        self.publish_page.wait_for_no_sections()

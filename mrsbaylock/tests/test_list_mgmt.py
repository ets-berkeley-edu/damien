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

from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.models.evaluation_type import EvaluationType
from mrsbaylock.models.user_dept_role import UserDeptRole
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestListManagement:

    # TODO - manual instructor

    test_id = f'{int(time.mktime(time.gmtime()))}'
    term = utils.get_current_term()
    all_contacts = utils.get_all_users()
    dept = utils.get_test_dept_1()
    utils.reset_test_data(term, dept)
    dept.evaluations = evaluation_utils.get_evaluations(term, dept)
    evaluations = list(filter(lambda e: e.instructor.uid, dept.evaluations))
    eval_unmarked = evaluations[0]
    eval_to_review = evaluations[1]
    eval_confirmed = evaluations[2]
    confirmed = []
    form = DepartmentForm(f'Form_{test_id}')
    eval_type = EvaluationType(f'Type_{test_id}')
    alert = (f'FOO {test_id} ' * 15).strip()

    role = UserDeptRole(dept.dept_id, receives_comms=True)
    instructor = utils.get_test_user(role)
    utils.hard_delete_user(instructor)

    utils.reset_test_data(term, dept)

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_list_mgmt_page(self):
        self.homepage.load_page()
        self.status_board_admin_page.click_list_mgmt()

    def test_add_dept_form(self):
        self.list_mgmt_page.add_dept_form(self.form)
        assert self.form.name in self.list_mgmt_page.visible_dept_form_names()

    def test_add_eval_type(self):
        self.list_mgmt_page.add_eval_type(self.eval_type)
        assert self.eval_type.name in self.list_mgmt_page.visible_eval_type_names()

    def test_unmarked_add_form_and_type(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        self.dept_details_admin_page.click_edit_evaluation(self.eval_unmarked)
        self.dept_details_admin_page.select_eval_status(self.eval_unmarked, EvaluationStatus.UNMARKED)
        self.dept_details_admin_page.change_dept_form(self.eval_unmarked, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_unmarked, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_unmarked)
        self.eval_unmarked.dept_form = self.form.name
        self.eval_unmarked.eval_type = self.eval_type.name
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.UNMARKED.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_unmarked)
        assert self.form.name in self.dept_details_admin_page.eval_dept_form(self.eval_unmarked)
        assert self.eval_type.name in self.dept_details_admin_page.eval_type(self.eval_unmarked)

    def test_for_review_add_form_and_type(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_to_review)
        self.dept_details_admin_page.select_eval_status(self.eval_to_review, EvaluationStatus.FOR_REVIEW)
        self.dept_details_admin_page.change_dept_form(self.eval_to_review, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_to_review, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_to_review)
        self.eval_to_review.dept_form = self.form.name
        self.eval_to_review.eval_type = self.eval_type.name
        self.eval_to_review.status = EvaluationStatus.FOR_REVIEW
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.FOR_REVIEW.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_to_review)
        assert self.form.name in self.dept_details_admin_page.eval_dept_form(self.eval_to_review)
        assert self.eval_type.name in self.dept_details_admin_page.eval_type(self.eval_to_review)

    def test_confirmed_add_form_and_type(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_confirmed)
        self.dept_details_admin_page.select_eval_status(self.eval_confirmed, EvaluationStatus.CONFIRMED)
        self.dept_details_admin_page.change_dept_form(self.eval_confirmed, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_confirmed, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_confirmed)
        self.eval_confirmed.dept_form = self.form.name
        self.eval_confirmed.eval_type = self.eval_type.name
        self.eval_confirmed.status = EvaluationStatus.FOR_REVIEW
        self.dept_details_admin_page.wait_for_eval_rows()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.CONFIRMED.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_confirmed)
        assert self.form.name in self.dept_details_admin_page.eval_dept_form(self.eval_confirmed)
        assert self.eval_type.name in self.dept_details_admin_page.eval_type(self.eval_confirmed)

    def test_delete_dept_form(self):
        self.dept_details_admin_page.click_list_mgmt()
        self.list_mgmt_page.delete_dept_form(self.form)
        assert self.form.name not in self.list_mgmt_page.visible_dept_form_names()

    def test_delete_eval_type(self):
        self.list_mgmt_page.delete_eval_type(self.eval_type)
        assert self.eval_type.name not in self.list_mgmt_page.visible_eval_type_names()

    def test_unmarked_form_and_type_deleted(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        assert self.dept_details_admin_page.eval_dept_form(self.eval_unmarked) == self.form.name
        assert self.dept_details_admin_page.eval_type(self.eval_unmarked) == self.eval_type.name

    def test_for_review_form_and_type_deleted(self):
        assert self.dept_details_admin_page.eval_dept_form(self.eval_to_review) == self.form.name
        assert self.dept_details_admin_page.eval_type(self.eval_to_review) == self.eval_type.name

    def test_confirmed_form_and_type_deleted(self):
        assert self.dept_details_admin_page.eval_dept_form(self.eval_confirmed) == self.form.name
        assert self.dept_details_admin_page.eval_type(self.eval_confirmed) == self.eval_type.name

    def test_deleted_form_not_available(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_unmarked)
        self.dept_details_admin_page.click_dept_form_input()
        assert self.form.name not in self.dept_details_admin_page.visible_dept_form_options()

    def test_deleted_type_not_available(self):
        assert self.eval_type.name not in self.dept_details_admin_page.visible_eval_type_options()

    # PUBLISH WITH DELETED FORM AND TYPE

    def test_publish(self):
        evals = evaluation_utils.get_evaluations(self.term, self.dept)
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

    def test_course_supervisors(self):
        expected = utils.expected_course_supervisors(self.confirmed, self.all_contacts)
        actual = self.publish_page.parse_csv('course_supervisors')
        utils.verify_actual_matches_expected(actual, expected)

    # SERVICE ALERTS

    def test_save_unposted_alert(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.click_list_mgmt()
        self.list_mgmt_page.enter_service_alert(self.alert)
        if self.list_mgmt_page.is_service_alert_posted():
            self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert not self.list_mgmt_page.service_alert()

    def test_post_alert(self):
        self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert self.list_mgmt_page.service_alert() == self.alert

    def test_edit_posted_alert(self):
        self.list_mgmt_page.enter_service_alert(f'EDITED {self.alert}')
        self.list_mgmt_page.save_service_alert()
        assert self.list_mgmt_page.service_alert() == f'EDITED {self.alert}'

    def test_unpost_alert(self):
        self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert not self.list_mgmt_page.service_alert()

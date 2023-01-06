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
import datetime
import time

from flask import current_app as app
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestEvalExports:

    term = utils.get_current_term()
    utils.reset_test_data(term)
    all_contacts = utils.get_all_users()
    all_depts = utils.get_participating_depts()
    dept, ev = evaluation_utils.get_dept_eval_with_foreign_x_listings(term, all_depts)
    evals = []
    confirmed = []
    expected_courses = []
    expected_course_students = []
    expected_course_instructors = []
    expected_instructors = []
    expected_course_supervisors = []
    expected_supervisors = []
    expected_x_listed_supervisors = []
    csv_instructors = []
    csv_course_instructors = []

    def test_refresh_loch(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()
        self.evals.extend(evaluation_utils.get_evaluations(self.term, self.dept))

    def test_complete_eval_instructors(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        no_teach = [e for e in self.evals if not e.instructor.uid]
        if no_teach:
            new_teach = utils.get_test_user()
            for row in no_teach:
                self.dept_details_admin_page.click_eval_checkbox(row)
            self.dept_details_admin_page.click_bulk_edit()
            self.dept_details_admin_page.look_up_and_select_dupe_instr(new_teach)
            self.dept_details_admin_page.click_bulk_edit_save()
            self.dept_details_admin_page.wait_for_bulk_update()
            for row in no_teach:
                row.instructor = new_teach

    def test_complete_eval_forms_and_types(self):
        no_form_or_type = [e for e in self.evals if (not e.dept_form) or (not e.eval_type)]
        if no_form_or_type:
            new_form = [e.dept_form for e in self.evals if e.dept_form][0]
            new_type = 'F'
            for row in no_form_or_type:
                self.dept_details_admin_page.click_eval_checkbox(row)
            self.dept_details_admin_page.click_bulk_edit()
            self.dept_details_dept_page.select_bulk_dept_form(new_form)
            self.dept_details_dept_page.select_bulk_eval_type(new_type)
            self.dept_details_admin_page.click_bulk_edit_save()
            self.dept_details_admin_page.wait_for_bulk_update()
            for row in no_form_or_type:
                row.dept_form = new_form
                row.eval_type = new_type

    def test_confirm_complete_evals(self):
        for row in self.evals:
            if row.instructor.uid and row.dept_form and row.eval_type:
                self.dept_details_admin_page.click_eval_checkbox(row)
                self.confirmed.append(row)
        self.dept_details_admin_page.click_bulk_done_button()

    def test_confirm_confirmed_count(self):
        time.sleep(utils.get_short_timeout())
        self.dept_details_admin_page.click_status_board()
        self.status_board_admin_page.wait_for_depts()
        if len(self.confirmed) == len(self.evals):
            assert self.status_board_admin_page.dept_confirmed_all(self.dept)
        else:
            assert self.status_board_admin_page.dept_confirmed_count(self.dept)[0] == len(self.confirmed)
            assert self.status_board_admin_page.dept_confirmed_count(self.dept)[1] == len(self.evals)

    def test_confirm_updated_date(self):
        assert self.status_board_admin_page.dept_last_update_date(self.dept) == datetime.date.today()

    def test_publish(self):
        self.publish_page.load_page()
        self.publish_page.download_export_csvs()

    def test_calculate_course_ids(self):
        utils.calculate_course_ids(self.confirmed)

    def test_courses(self):
        self.expected_courses.extend(utils.expected_courses(self.confirmed))
        csv_courses = self.publish_page.parse_csv('courses')
        utils.verify_actual_matches_expected(csv_courses, self.expected_courses)

    def test_course_students(self):
        self.expected_course_students.extend(utils.expected_course_students(self.confirmed))
        csv_course_students = self.publish_page.parse_csv('course_students')
        utils.verify_actual_matches_expected(csv_course_students, self.expected_course_students)

    def test_students(self):
        csv_students = self.publish_page.parse_csv('students')
        csv_uids = list(map(lambda d: d['LDAP_UID'], csv_students))
        expected_uids = [u for u in set(list(map(lambda d: d['LDAP_UID'], self.expected_course_students)))]
        utils.verify_actual_matches_expected(csv_uids, expected_uids)

        csv_sids = list(map(lambda d: d['SIS_ID'], csv_students))
        assert len(list(filter(None, csv_sids))) == len(expected_uids)

        csv_first_names = list(map(lambda d: d['FIRST_NAME'], csv_students))
        assert len(list(filter(None, csv_first_names))) == len(expected_uids)

        csv_last_names = list(map(lambda d: d['LAST_NAME'], csv_students))
        assert len(list(filter(None, csv_last_names))) == len(expected_uids)

        csv_emails = list(map(lambda d: d['EMAIL_ADDRESS'], csv_students))
        assert len(list(filter(None, csv_emails))) > 0

    def test_course_instructors_past_term(self):
        self.csv_course_instructors.extend(self.publish_page.parse_csv('course_instructors'))
        past_term_rows = list(filter(lambda r: (self.term.prefix not in r['COURSE_ID']), self.csv_course_instructors))
        assert past_term_rows

    def test_course_instructors(self):
        self.expected_course_instructors.extend(utils.expected_course_instructors(self.confirmed))
        current_term_rows = list(filter(lambda r: (self.term.prefix in r['COURSE_ID']), self.csv_course_instructors))
        utils.verify_actual_matches_expected(current_term_rows, self.expected_course_instructors)

    def test_instructors_past_term(self):
        self.expected_instructors.extend(utils.expected_instructors(self.confirmed))
        self.csv_instructors.extend(self.publish_page.parse_csv('instructors'))
        assert len(self.expected_instructors) < len(self.csv_instructors)
        csv_uids = list(map(lambda u: u['LDAP_UID'], self.csv_instructors))
        csv_uids.sort()
        unique = list(set(csv_uids))
        unique.sort()
        assert unique == csv_uids

    def test_instructors(self):
        csv_instructors = self.publish_page.parse_csv('instructors')
        for x in self.expected_instructors:
            app.logger.info(f'Verifying {x} in instructors.csv')
            assert x in csv_instructors

    def test_course_supervisors(self):
        self.expected_course_supervisors.extend(utils.expected_course_supervisors(self.confirmed, self.all_contacts))
        csv_course_supervisors = self.publish_page.parse_csv('course_supervisors')
        utils.verify_actual_matches_expected(csv_course_supervisors, self.expected_course_supervisors)

    def test_supervisors(self):
        self.expected_supervisors.extend(utils.expected_supervisors())
        csv_course_supervisors = self.publish_page.parse_supervisors_csv()
        utils.verify_actual_matches_expected(csv_course_supervisors, self.expected_supervisors)

    def test_x_listed_course_supervisors(self):
        self.expected_x_listed_supervisors.extend(utils.expected_x_listed_course_supervisors(self.term, self.confirmed, self.all_contacts))
        csv_x_listed_supervisors = self.publish_page.parse_csv('xlisted_course_supervisors')
        utils.verify_actual_matches_expected(csv_x_listed_supervisors, self.expected_x_listed_supervisors)

    def test_dept_hierarchy(self):
        expected_dept_hierarchy = utils.expected_dept_hierarchy()
        csv_dept_hierarchy = self.publish_page.parse_csv('department_hierarchy')
        utils.verify_actual_matches_expected(csv_dept_hierarchy, expected_dept_hierarchy)

    def test_report_viewers(self):
        expected_viewers = utils.expected_report_viewers()
        csv_viewers = self.publish_page.parse_csv('report_viewer_hierarchy')
        utils.verify_actual_matches_expected(csv_viewers, expected_viewers)

    # SIS DATA CHANGES

    def test_section_deleted(self):
        evaluation = self.confirmed[0]
        evaluation_utils.set_section_deleted(evaluation)

    def test_section_enrollment_zero(self):
        evaluation = self.confirmed[1]
        evaluation_utils.set_enrollment_count_zero(evaluation)
        self.confirmed.remove(evaluation)

    def test_instructor_removed(self):
        evaluation = copy.deepcopy(self.confirmed[3])
        evaluation.instructor.uid = None
        evaluation.instructor.role_code = None
        evaluation_utils.set_section_instructor(evaluation)

    def test_instructor_changed(self):
        evaluation = copy.deepcopy(self.confirmed[4])
        evaluation.instructor = self.confirmed[5].instructor
        evaluation_utils.set_section_instructor(evaluation)

    def test_publish_sis_changes(self):
        self.publish_page.load_page()
        self.publish_page.download_export_csvs()

    def test_courses_updates(self):
        expected = utils.expected_courses(self.confirmed)
        csv_courses = self.publish_page.parse_csv('courses')
        utils.verify_actual_matches_expected(csv_courses, expected)

    def test_course_instructors_updates(self):
        expected = utils.expected_course_instructors(self.confirmed)
        csv_course_instructors = self.publish_page.parse_csv('course_instructors')
        current_term_rows = list(filter(lambda r: (self.term.prefix in r['COURSE_ID']), csv_course_instructors))
        utils.verify_actual_matches_expected(current_term_rows, expected)

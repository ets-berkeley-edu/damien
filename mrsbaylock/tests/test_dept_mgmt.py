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

from mrsbaylock.pages.dept_details_admin_page import DeptDetailsAdminPage
from mrsbaylock.test_utils import utils
import pytest
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait

term = utils.get_current_term()
depts = utils.get_participating_depts()
utils.get_all_users()

test_dept = utils.get_dept('Astronomy')
test_user = utils.get_test_user()
utils.hard_delete_user(test_user)
utils.delete_dept_note(term, test_dept)


@pytest.mark.usefixtures('page_objects')
class TestDeptMgmt:

    def test_status_page(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.group_mgmt_page.click_group_mgmt()

    def test_dept_link(self):
        self.group_mgmt_page.click_dept_link(test_dept)

    # NOTE

    def test_edit_note_cancel(self):
        note = f'{test_dept.name} note {self.test_id}'
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.cxl_dept_note()
        self.dept_details_admin_page.verify_dept_note(test_dept)

    def test_edit_note_save(self):
        note = f'{test_dept.name} note {self.test_id}'
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.save_dept_note()
        test_dept.note = note
        self.dept_details_admin_page.verify_dept_note(test_dept)

    def test_delete_note(self):
        self.dept_details_admin_page.delete_dept_note()

    # CONTACTS

    @pytest.mark.parametrize('user', test_dept.users, scope='function', ids=[user.uid for user in test_dept.users])
    def test_dept_user_details(self, user):
        dept_role = utils.get_user_dept_role(user, test_dept)
        self.dept_details_admin_page.wait_for_contact(user)
        assert self.dept_details_admin_page.dept_contact_name(user) == f'{user.first_name} {user.last_name}'
        expected_comms = 'Does receive notifications' if dept_role.receives_comms else 'Does not receive notifications'
        assert self.dept_details_admin_page.dept_contact_comms_perms(user) == expected_comms
        expected_blue = user.blue_permissions.value['description']
        assert self.dept_details_admin_page.dept_contact_blue_perms(user) == expected_blue

    def test_add_contact_cancel(self):
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.click_cancel_contact()

    def test_add_contact_uid_lookup(self):
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        assert self.dept_details_admin_page.value(DeptDetailsAdminPage.ADD_CONTACT_EMAIL) == test_user.email

    def test_add_contact_name_lookup(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_name(f'{test_user.first_name} {test_user.last_name}')
        # TODO (not implemented) self.dept_details_admin_page.click_look_up_result(test_user)

    def test_add_contact_bad_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_contact_email('foo.com')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_INVALID_MSG))

    def test_add_contact_no_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_contact_email('')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_REQUIRED_MSG))

    def test_add_contact_modify_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_contact_email(utils.get_test_email_account())

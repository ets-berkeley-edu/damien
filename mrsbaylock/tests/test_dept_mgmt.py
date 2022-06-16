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

from mrsbaylock.models.email import Email
from mrsbaylock.models.term import Term
from mrsbaylock.models.user_dept_role import UserDeptRole
from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.pages.dept_details_admin_page import DeptDetailsAdminPage
from mrsbaylock.test_utils import utils
import pytest
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait

term = utils.get_current_term()
previous_term = Term(utils.get_previous_term_code(term.term_id), None)
depts = utils.get_participating_depts()
all_users = utils.get_all_users()

test_dept = utils.get_dept('Astronomy', all_users)
role = UserDeptRole(test_dept.dept_id, receives_comms=True)
test_user = utils.get_test_user(role)
test_email = Email(subject=None, body=None)
utils.hard_delete_user(test_user)
utils.delete_dept_note(term, test_dept)
test_dept.users = utils.get_dept_users(test_dept)


@pytest.mark.usefixtures('page_objects')
class TestDeptMgmt:

    def test_create_old_note(self):
        utils.create_dept_note(previous_term, test_dept, f'Past note {self.test_id}')

    def test_status_page(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.group_mgmt_page.click_group_mgmt()

    def test_dept_link(self):
        self.group_mgmt_page.click_dept_link(test_dept)

    # NOTE

    def test_edit_note_cancel(self):
        note = f'{test_dept.name} note {self.test_id} ' * 30
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.cxl_dept_note()
        self.dept_details_admin_page.verify_dept_note()

    def test_edit_note_save(self):
        note = f'{test_dept.name} note {self.test_id}'
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.save_dept_note()
        self.dept_details_admin_page.verify_dept_note(note)

    def test_delete_note(self):
        self.dept_details_admin_page.delete_dept_note()

    def test_previous_term_note(self):
        self.dept_details_admin_page.select_term(previous_term)
        self.dept_details_admin_page.wait_for_note()
        disabled = self.dept_details_admin_page.element(DeptDetailsAdminPage.DEPT_NOTE_EDIT_BUTTON).get_attribute('disabled')
        assert disabled == 'true'

    # CONTACTS

    def test_expand_contacts(self):
        self.dept_details_admin_page.expand_dept_contact_list()

    @pytest.mark.parametrize('user', test_dept.users, scope='function', ids=[user.uid for user in test_dept.users])
    def test_dept_user_details(self, user):
        dept_role = utils.get_user_dept_role(user, test_dept)
        self.dept_details_admin_page.expand_dept_contact(user)
        self.dept_details_admin_page.wait_for_contact(user)
        expected_comms = 'Does receive notifications' if dept_role.receives_comms else 'Does not receive notifications'
        assert self.dept_details_admin_page.dept_contact_comms_perms(user) == expected_comms
        expected_blue = user.blue_permissions.value['description']
        assert self.dept_details_admin_page.dept_contact_blue_perms(user) == expected_blue
        expected_forms = list(map(lambda f: f.name, user.dept_forms))
        actual_forms = list(map(lambda f: f.name, self.dept_details_admin_page.dept_contact_dept_forms(user)))
        assert actual_forms == expected_forms

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
        self.dept_details_admin_page.look_up_contact_name(test_user.first_name)
        self.dept_details_admin_page.click_look_up_result(test_user)
        assert self.dept_details_admin_page.value(DeptDetailsAdminPage.ADD_CONTACT_EMAIL) == test_user.email

    def test_add_contact_bad_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_new_contact_email('foo.com')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_INVALID_MSG))

    def test_add_contact_no_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_new_contact_email('')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_REQUIRED_MSG))

    def test_add_contact_modify_email(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.enter_new_contact_email(utils.get_test_email_account())

    def test_add_contact_add_dept_forms(self):
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_contact_uid(test_user.uid)
        self.dept_details_admin_page.click_look_up_result(test_user)
        self.dept_details_admin_page.select_dept_forms(test_user.dept_forms)

    def test_add_contact_remove_dept_forms(self):
        self.dept_details_admin_page.remove_dept_forms(test_user.dept_forms)

    def test_add_contact_save(self):
        self.dept_details_admin_page.hit_escape()
        self.dept_details_admin_page.click_cancel_contact()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.add_contact(test_user, test_dept)

    def test_edit_contact_bad_email(self):
        self.dept_details_admin_page.expand_dept_contact(test_user)
        self.dept_details_admin_page.click_edit_contact(test_user)
        self.dept_details_admin_page.enter_dept_contact_email_edit(test_user, 'foo.com')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_INVALID_MSG))

    def test_edit_contact_no_email(self):
        self.dept_details_admin_page.enter_dept_contact_email_edit(test_user, '')
        Wait(self.driver, 2).until(ec.visibility_of_element_located(DeptDetailsAdminPage.EMAIL_REQUIRED_MSG))

    def test_edit_contact_save(self):
        new_role = UserDeptRole(test_dept.dept_id, receives_comms=False)
        test_user.dept_roles = [new_role]
        test_user.blue_permissions = 'response_rates'
        self.dept_details_admin_page.click_cancel_contact_edits(test_user)
        self.dept_details_admin_page.edit_contact(test_user, test_dept)

    # NOTIFICATIONS - DEPT

    def test_send_notif_cancel(self):
        self.dept_details_admin_page.open_notif_form()
        self.dept_details_admin_page.click_notif_cxl()

    def test_notif_no_subj_no_body(self):
        self.dept_details_admin_page.open_notif_form()
        assert not self.dept_details_admin_page.element(DamienPages.NOTIF_SEND_BUTTON).is_enabled()

    def test_notif_subj_no_body(self):
        self.dept_details_admin_page.enter_notif_subj('foo')
        assert not self.dept_details_admin_page.element(DamienPages.NOTIF_SEND_BUTTON).is_enabled()

    def test_notif_body_no_subj(self):
        self.dept_details_admin_page.enter_notif_subj('')
        self.dept_details_admin_page.enter_notif_body('foo')
        assert not self.dept_details_admin_page.element(DamienPages.NOTIF_SEND_BUTTON).is_enabled()

    def test_notif_default_recipients(self):
        test_dept.users = utils.get_dept_users(test_dept, all_users)
        test_email.recipients = []
        for user in test_dept.users:
            dept_role = next(filter(lambda r: (r.dept_id == test_dept.dept_id), user.dept_roles))
            if dept_role.receives_comms:
                test_email.recipients.append(user)
        expected = list(map(lambda u: u.email, test_email.recipients))
        expected.sort()
        self.dept_details_admin_page.notif_expand_dept_recipient_members(test_dept)
        visible = self.dept_details_admin_page.notif_dept_recipient_emails(test_dept)
        visible.sort()
        assert visible == expected

    def test_notif_remove_all(self):
        for u in test_email.recipients:
            self.dept_details_admin_page.notif_remove_recipient(test_dept, u)
        assert not self.dept_details_admin_page.element(DamienPages.NOTIF_SEND_BUTTON).is_enabled()

    def test_notif_send_to_all(self):
        test_email.subject = f'Test subject to all contacts {self.test_id}'
        test_email.body = f'Test body to all contacts {self.test_id}'
        self.dept_details_admin_page.click_notif_cxl()
        self.dept_details_admin_page.send_notif_to_dept(test_dept, test_email)

    def test_notif_send_to_some(self):
        test_email.subject = f'Test subject to some contacts {self.test_id}'
        test_email.body = f'Test body to some contacts {self.test_id}'
        self.dept_details_admin_page.send_notif_to_dept(test_dept, test_email, test_email.recipients[0:1])

    # NOTIFICATIONS - DEPT

    def test_bulk_notif_send_to_some(self):
        self.status_board_admin_page.load_page()
        test_email.subject = f'Bulk test subject to some departments, all contacts {self.test_id}'
        test_email.body = f'Bulk test body to some departments, all contacts {self.test_id}'
        for d in depts[3:4]:
            self.status_board_admin_page.check_dept_notif_cbx(d)
        self.status_board_admin_page.send_notif_to_depts(test_email)

    def test_bulk_notif_remove_some(self):
        test_email.subject = f'Bulk test subject to some departments, some contacts {self.test_id}'
        test_email.body = f'Bulk test body to some departments, some contacts {self.test_id}'
        recips_to_exclude = []
        for d in depts[5:6]:
            d.users = utils.get_dept_users(d, all_users)
            recips_to_exclude.append({'user': d.users[-1], 'dept': d})
            self.status_board_admin_page.check_dept_notif_cbx(d)
        self.status_board_admin_page.send_notif_to_depts(test_email, recips_to_exclude)

    def test_bulk_notif_send_to_all(self):
        test_email.subject = f'Bulk test subject to all departments, all contacts {self.test_id}'
        test_email.body = f'Bulk test body to all departments, all contacts {self.test_id}'
        self.status_board_admin_page.check_all_dept_notif_cbx()
        self.status_board_admin_page.send_notif_to_depts(test_email)

    # CONTACT - DELETE

    def test_delete_contact_cancel(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.click_dept_link(test_dept)
        self.dept_details_admin_page.wait_for_contact(test_user)
        self.dept_details_admin_page.expand_dept_contact_list()
        self.dept_details_admin_page.expand_dept_contact(test_user)
        self.dept_details_admin_page.click_delete_contact(test_user)
        self.dept_details_admin_page.cancel_delete_contact()

    def test_delete_contact_confirm(self):
        self.dept_details_admin_page.click_delete_contact(test_user)
        self.dept_details_admin_page.confirm_delete_contact(test_user)
        assert not self.dept_details_admin_page.is_present(DeptDetailsAdminPage.dept_contact_xpath(test_user))
        test_dept.users.remove(test_user)

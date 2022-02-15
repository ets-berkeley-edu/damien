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

from mrsbaylock.test_utils import utils
import pytest

dept = utils.get_dept('History')
utils.delete_dept_note(dept)


@pytest.mark.usefixtures('page_objects')
class TestDeptMgmt:

    def test_status_page(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_status_board()

    def test_dept_link(self):
        self.status_board_admin_page.click_dept_link(dept)

    @pytest.mark.parametrize('user', dept.users, scope='function', ids=[user.uid for user in dept.users])
    def test_dept_user_details(self, user):
        self.dept_details_admin_page.wait_for_contact(user)
        assert self.dept_details_admin_page.dept_contact_name(user) == f'{user.first_name} {user.last_name}'
        expected_comms = 'Does receive notifications' if user.receives_comms else 'Does not receive notifications'
        assert self.dept_details_admin_page.dept_contact_comms_perms(user) == expected_comms
        expected_resp = 'Can view response rates' if user.views_response_rates else 'Cannot view response rates'
        assert self.dept_details_admin_page.dept_contact_blue_perms(user) == expected_resp

    def test_edit_note_cancel(self):
        note = f'{dept.name} note {self.test_id}'
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.cxl_dept_note()
        self.dept_details_admin_page.verify_dept_note(dept)

    def test_edit_note_save(self):
        note = f'{dept.name} note {self.test_id}'
        self.dept_details_admin_page.edit_dept_note(note)
        self.dept_details_admin_page.save_dept_note()
        dept.note = note
        self.dept_details_admin_page.verify_dept_note(dept)

    def test_delete_note(self):
        self.dept_details_admin_page.delete_dept_note()

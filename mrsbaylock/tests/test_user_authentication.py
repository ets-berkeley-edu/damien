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

from mrsbaylock.pages.login_page import LoginPage
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestUserAuthentication:

    user = utils.get_user(utils.get_admin_uid())
    username = utils.get_admin_username()
    password = utils.get_admin_password()

    def test_hard_delete_user(self):
        utils.hard_delete_user(self.user)

    def test_no_user_no_login(self):
        self.login_page.load_page()
        self.login_page.click_sign_in()
        self.calnet_page.log_in(self.username, self.password)
        self.login_page.wait_for_element(LoginPage.SIGN_IN_BUTTON, utils.get_medium_timeout())
        # TODO - wait for proper messaging

    def test_add_user(self):
        utils.create_admin_user(self.user)

    def test_added_user_login(self):
        self.login_page.load_page()
        self.login_page.click_sign_in()
        self.status_board_admin_page.wait_for_admin_login()

    def test_restored_user_log_out(self):
        self.status_board_admin_page.log_out()

    def test_soft_delete_user(self):
        utils.soft_delete_user(self.user)

    def test_deleted_user_no_login(self):
        self.login_page.load_page()
        self.login_page.click_sign_in()
        self.calnet_page.log_in(self.username, self.password)
        self.login_page.wait_for_element(LoginPage.SIGN_IN_BUTTON, utils.get_medium_timeout())
        # TODO - wait for proper messaging

    def test_undelete_user(self):
        utils.restore_user(self.user)

    def test_restored_user_login(self):
        self.login_page.load_page()
        self.login_page.click_sign_in()
        self.status_board_admin_page.wait_for_admin_login()

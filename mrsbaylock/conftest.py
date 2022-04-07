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

from datetime import datetime
import os

from damien.factory import create_app
from mrsbaylock.pages.calnet_page import CalNetPage
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.pages.course_errors_page import CourseErrorsPage
from mrsbaylock.pages.dept_details_admin_page import DeptDetailsAdminPage
from mrsbaylock.pages.group_mgmt_page import GroupMgmtPage
from mrsbaylock.pages.homepage import Homepage
from mrsbaylock.pages.list_mgmt_page import ListMgmtPage
from mrsbaylock.pages.login_page import LoginPage
from mrsbaylock.pages.status_board_admin_page import StatusBoardAdminPage
from mrsbaylock.test_utils.webdriver_utils import WebDriverManager
import pytest


os.environ['DAMIEN_ENV'] = 'mrsbaylock'  # noqa

_app = create_app()

ctx = _app.app_context()
ctx.push()


@pytest.fixture(scope='session')
def page_objects(request):
    driver = WebDriverManager.launch_browser()
    test_id = datetime.strftime(datetime.now(), '%s')

    # Define page objects
    calnet_page = CalNetPage(driver)
    course_errors_page = CourseErrorsPage(driver)
    dept_details_admin_page = DeptDetailsAdminPage(driver)
    dept_details_dept_page = CourseDashboardEditsPage(driver)
    group_mgmt_page = GroupMgmtPage(driver)
    homepage = Homepage(driver)
    list_mgmt_page = ListMgmtPage(driver)
    login_page = LoginPage(driver)
    status_board_admin_page = StatusBoardAdminPage(driver)

    session = request.node
    try:
        for item in session.items:
            cls = item.getparent(pytest.Class)
            setattr(cls.obj, 'driver', driver)
            setattr(cls.obj, 'test_id', test_id)
            setattr(cls.obj, 'calnet_page', calnet_page)
            setattr(cls.obj, 'course_errors_page', course_errors_page)
            setattr(cls.obj, 'dept_details_admin_page', dept_details_admin_page)
            setattr(cls.obj, 'dept_details_dept_page', dept_details_dept_page)
            setattr(cls.obj, 'group_mgmt_page', group_mgmt_page)
            setattr(cls.obj, 'homepage', homepage)
            setattr(cls.obj, 'list_mgmt_page', list_mgmt_page)
            setattr(cls.obj, 'login_page', login_page)
            setattr(cls.obj, 'status_board_admin_page', status_board_admin_page)
        yield
    finally:
        WebDriverManager.quit_browser(driver)

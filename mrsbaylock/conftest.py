"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from flask import current_app as app
from mrsbaylock.pages.api_page import ApiPage
from mrsbaylock.pages.calnet_page import CalNetPage
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.pages.dept_details_admin_page import DeptDetailsAdminPage
from mrsbaylock.pages.group_mgmt_page import GroupMgmtPage
from mrsbaylock.pages.homepage import Homepage
from mrsbaylock.pages.list_mgmt_page import ListMgmtPage
from mrsbaylock.pages.login_page import LoginPage
from mrsbaylock.pages.publish_page import PublishPage
from mrsbaylock.pages.status_board_admin_page import StatusBoardAdminPage
from mrsbaylock.test_utils.webdriver_utils import WebDriverManager
import pytest


os.environ['DAMIEN_ENV'] = 'mrsbaylock'  # noqa

_app = create_app()

ctx = _app.app_context()
ctx.push()


def pytest_addoption(parser):
    parser.addoption('--browser', action='store', default=app.config['BROWSER'])
    parser.addoption('--headless', action='store')


@pytest.fixture(scope='session')
def page_objects(request):
    browser = request.config.getoption('--browser')
    headless = request.config.getoption('--headless')
    driver = WebDriverManager.launch_browser(browser=browser, headless=headless)
    test_id = datetime.strftime(datetime.now(), '%s')

    # Define page objects
    api_page = ApiPage(driver, headless)
    calnet_page = CalNetPage(driver, headless)
    dept_details_admin_page = DeptDetailsAdminPage(driver, headless)
    dept_details_dept_page = CourseDashboardEditsPage(driver, headless)
    group_mgmt_page = GroupMgmtPage(driver, headless)
    homepage = Homepage(driver, headless)
    list_mgmt_page = ListMgmtPage(driver, headless)
    login_page = LoginPage(driver, headless)
    publish_page = PublishPage(driver, headless)
    status_board_admin_page = StatusBoardAdminPage(driver, headless)

    session = request.node
    try:
        for item in session.items:
            cls = item.getparent(pytest.Class)
            setattr(cls.obj, 'driver', driver)
            setattr(cls.obj, 'test_id', test_id)
            setattr(cls.obj, 'api_page', api_page)
            setattr(cls.obj, 'calnet_page', calnet_page)
            setattr(cls.obj, 'dept_details_admin_page', dept_details_admin_page)
            setattr(cls.obj, 'dept_details_dept_page', dept_details_dept_page)
            setattr(cls.obj, 'group_mgmt_page', group_mgmt_page)
            setattr(cls.obj, 'homepage', homepage)
            setattr(cls.obj, 'list_mgmt_page', list_mgmt_page)
            setattr(cls.obj, 'login_page', login_page)
            setattr(cls.obj, 'publish_page', publish_page)
            setattr(cls.obj, 'status_board_admin_page', status_board_admin_page)
        yield
    finally:
        WebDriverManager.quit_browser(driver)

"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import logging
import os

ADMIN_UID = '123456'
ADMIN_USERNAME = 'secret'
ADMIN_PASSWORD = 'secret'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE_URL = 'https://manage-dev.course-evaluations.berkeley.edu'
BASE_URL_API = 'https://manage-dev.course-evaluations.berkeley.edu'

BROWSER = 'chrome'
BROWSER_BINARY_PATH = '/path/to/chrome'
BROWSER_HEADLESS = False

CLICK_SLEEP = 0.5

CURRENT_TERM_BEGIN = '2022-01-18'
CURRENT_TERM_END = '2022-05-06'
CURRENT_TERM_NAME = 'Spring 2022'
CURRENT_TERM_PREFIX = '2022-B'

INDEX_HTML = f'{BASE_DIR}/tests/static/test-index.html'

LOGGING_LEVEL = logging.INFO

TEST_DEPT_1 = 'Astronomy'
TEST_DEPT_2 = 'Theology'
TEST_DEPT_CONTACT_UID = '123456'
TEST_DEPT_CONTACT_CSID = '654321'
TEST_DEPT_CONTACT_FIRST_NAME = 'Father'
TEST_DEPT_CONTACT_LAST_NAME = 'Spiletto'
TEST_DEPT_CONTACT_EMAIL = 'foo@bar.com'
TEST_DEPT_CONTACT_FORMS = 'HISTORY,YIDDISH'

TEST_EMAIL = 'damien@court_of_st_james.org'

TEST_EVAL_DEPTS = [1, 2, 3]

TESTING = True

TIMEOUT_SHORT = 20
TIMEOUT_MEDIUM = 120
TIMEOUT_LONG = 500

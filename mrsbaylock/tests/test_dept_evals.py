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

from flask import current_app as app
from mrsbaylock.models.term import Term
from mrsbaylock.test_utils import utils
import pytest

term = Term()
depts = utils.get_participating_depts()


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('dept', depts, scope='class', ids=[dept.dept_id for dept in depts])
class TestDeptEvaluations:

    def test_status_page(self, dept):
        self.homepage.load_page()
        if 'Welcome' in self.homepage.title():
            self.login_page.load_page()
            self.login_page.dev_auth()
        time.sleep(1)
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.click_dept_link(dept)

    def test_evals(self, dept):
        evaluations = utils.get_evaluations(term, dept)
        expected = [f'{i.ccn}-{"" if i.uid is None else i.uid}' for i in evaluations]
        expected = list(dict.fromkeys(expected))
        expected.sort()
        actual = self.dept_details_admin_page.visible_eval_identifiers()
        actual.sort()
        app.logger.info(f'Missing: {[x for x in expected if x not in actual]}')
        app.logger.info(f'Unexpected: {[x for x in actual if x not in expected]}')
        assert actual == expected

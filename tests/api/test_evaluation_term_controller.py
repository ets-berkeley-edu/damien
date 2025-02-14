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

import json


non_admin_uid = '100'
admin_uid = '200'


def _api_get_evaluation_term(client, term_id='2222', expected_status_code=200):
    response = client.get(f'/api/evaluation_term/{term_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetEvaluationTerm:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_evaluation_term(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Returns a valid response to non-admin user."""
        fake_auth.login(non_admin_uid)
        fall = _api_get_evaluation_term(client, term_id='2218')
        assert fall['isLocked'] is True
        spring = _api_get_evaluation_term(client)
        assert spring['isLocked'] is False

    def test_bad_term(self, client, fake_auth):
        """Rejects invalid term id."""
        fake_auth.login(admin_uid)
        _api_get_evaluation_term(client, term_id='1666', expected_status_code=400)


def _api_lock_evaluation_term(client, term_id='2222', expected_status_code=200):
    response = client.post(
        '/api/evaluation_term/lock',
        data=json.dumps({term_id: term_id}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestLockEvaluationTerm:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_lock_evaluation_term(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_lock_evaluation_term(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Authorized user can lock an evaluation term."""
        fake_auth.login(admin_uid)
        term = _api_lock_evaluation_term(client)
        assert term['isLocked'] is True
        assert term['termId'] == '2222'
        assert term['updatedBy'] == admin_uid


def _api_unlock_evaluation_term(client, term_id='2222', expected_status_code=200):
    response = client.post(
        '/api/evaluation_term/unlock',
        data=json.dumps({term_id: term_id}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestUnlockEvaluationTerm:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_unlock_evaluation_term(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_unlock_evaluation_term(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Authorized user can unlock an evaluation term."""
        fake_auth.login(admin_uid)
        term = _api_unlock_evaluation_term(client)
        assert term['isLocked'] is False
        assert term['termId'] == '2222'
        assert term['updatedBy'] == admin_uid

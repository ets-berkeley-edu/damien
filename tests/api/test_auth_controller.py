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
from unittest import mock

import cas
from damien import std_commit
from damien.models.user import User
from tests.util import override_config

authorized_uid = '100'
unauthorized_uid = '666'


class TestDevAuth:
    """DevAuth handling."""

    @staticmethod
    def _api_dev_auth_login(client, params, expected_status_code=200):
        response = client.post(
            '/api/auth/dev_auth_login',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': authorized_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=404,
            )

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': authorized_uid,
                    'password': 'Daggers of Megiddo',
                },
                expected_status_code=401,
            )

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': unauthorized_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=403,
            )

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            api_json = self._api_dev_auth_login(
                client,
                params={
                    'uid': authorized_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
            )
            assert api_json['uid'] == authorized_uid
            assert client.get('/api/auth/logout').status_code == 200

            std_commit(allow_test_environment=True)
            user = User.find_by_uid(authorized_uid)
            assert user.login_at


class TestCasAuth:
    """CAS login URL generation and redirects."""

    def test_cas_login_url(self, client):
        """Returns berkeley.edu URL of CAS login page."""
        response = client.get('/api/auth/cas_login_url')
        assert response.status_code == 200
        assert 'berkeley.edu/cas/login' in response.json.get('casLoginUrl')

    def test_cas_callback_with_invalid_ticket(self, client):
        """Fails if CAS can not verify the ticket."""
        response = client.get('/cas/callback?ticket=is_invalid')
        assert response.status_code == 302
        assert 'error' in response.location

    @mock.patch.object(cas.CASClientV3, 'verify_ticket', autospec=True)
    def test_cas_callback_with_valid_ticket(self, mock_verify_ticket, client):
        """Given a valid ticket, logs user in."""
        mock_verify_ticket.return_value = (authorized_uid, {}, 'is_valid')
        response = client.get('/cas/callback?ticket=is_valid')
        assert response.status_code == 302

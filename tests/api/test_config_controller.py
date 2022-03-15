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

from tests.util import override_config

authorized_uid = '100'


class TestConfigController:
    """Config API."""

    def test_anonymous(self, client):
        """Returns a well-formed response to anonymous user."""
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.json
        assert data['damienEnv'] == 'test'
        assert data['devAuthEnabled'] is False
        assert data['ebEnvironment'] is None
        assert data['timezone'] == 'America/Los_Angeles'

    def test_authorized_user(self, app, client, fake_auth):
        """Returns a well-formed response to authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            fake_auth.login(authorized_uid)
            response = client.get('/api/config')
            assert response.status_code == 200
            data = response.json
            assert data['damienEnv'] == 'test'
            assert data['devAuthEnabled'] is True
            assert data['ebEnvironment'] is None
            assert data['timezone'] == 'America/Los_Angeles'

    def test_available_terms(self, app, client, fake_auth):
        fake_auth.login(authorized_uid)
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.json
        assert len(data['availableTerms']) == 2
        assert data['availableTerms'][0] == {'id': '2218', 'name': 'Fall 2021'}
        assert data['availableTerms'][1] == {'id': '2222', 'name': 'Spring 2022'}

    def test_current_term(self, app, client, fake_auth):
        fake_auth.login(authorized_uid)
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.json
        assert data['currentTermId'] == '2222'
        assert data['currentTermDates']['begin'] == '2022-01-01'
        assert data['currentTermDates']['end'] == '2022-05-31'

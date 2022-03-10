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

import json


admin_uid = '200'
non_admin_uid = '100'


def _api_my_profile(client, expected_status_code=200):
    response = client.get('/api/user/my_profile')
    assert response.status_code == expected_status_code
    return response.json


class TestMyProfile:

    def test_anonymous(self, client):
        """Returns a well-formed response to anonymous user."""
        _api_my_profile(client)

    def test_authenticated(self, client, fake_auth):
        """Returns authenticated user profile."""
        fake_auth.login(non_admin_uid)
        api_json = _api_my_profile(client)
        assert api_json['uid'] == non_admin_uid


def _api_search(client, snippet='123', expected_status_code=200):
    response = client.post(
        '/api/user/search',
        data=json.dumps({'snippet': snippet}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestSearch:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_search(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_search(client, expected_status_code=401)

    def test_authenticated_uid_search(self, client, fake_auth):
        """Returns UID matches."""
        fake_auth.login(admin_uid)
        results = _api_search(client, snippet='500')
        assert '500' in [r['uid'] for r in results]

    def test_authenticated_name_search(self, client, fake_auth):
        """Returns name matches."""
        fake_auth.login(admin_uid)
        results = _api_search(client, snippet='THO R')
        assert results[0]['firstName'] == 'Robert'
        assert results[0]['lastName'] == 'Thorn'

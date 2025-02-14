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


admin_uid = '200'
non_admin_uid = '100'
default_instructor = {
    'uid': '12345',
    'csid': '67890',
    'firstName': 'Lesya',
    'lastName': 'Ukrainka',
    'emailAddress': 'lisova.pisnya@berkeley.edu',
}


def _api_add_instructor(client, params={}, expected_status_code=200):
    instructor = {**default_instructor, **params}
    response = client.post(
        '/api/instructor',
        data=json.dumps(instructor),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_delete_instructor(client, uid, expected_status_code=200):
    response = client.delete(f'/api/instructor/{uid}')
    assert response.status_code == expected_status_code
    return response.json


def _api_get_instructors(client, expected_status_code=200):
    response = client.get('/api/instructors')
    assert response.status_code == expected_status_code
    return response.json


def _api_search_instructors(client, snippet='123', expected_status_code=200):
    response = client.post(
        '/api/instructor/search',
        data=json.dumps({'snippet': snippet}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestAddInstructor:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_add_instructor(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_add_instructor(client, expected_status_code=401)

    def test_bad_uid(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'uid': 'NOPE'}, expected_status_code=400)

    def test_missing_uid(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'uid': None}, expected_status_code=400)

    def test_bad_csid(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'csid': 'NOPE'}, expected_status_code=400)

    def test_missing_name(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'lastName': None}, expected_status_code=400)

    def test_bad_email(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'emailAddress': 'NOPE'}, expected_status_code=400)

    def test_missing_email(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client, {'emailAddress': None}, expected_status_code=400)

    def test_authorized_create(self, client, fake_auth):
        fake_auth.login(admin_uid)
        instructor = _api_add_instructor(client)
        assert instructor['uid'] == default_instructor['uid']
        assert instructor['csid'] == default_instructor['csid']
        assert instructor['firstName'] == default_instructor['firstName']
        assert instructor['lastName'] == default_instructor['lastName']
        assert instructor['email'] == default_instructor['emailAddress']


class TestDeleteInstructor:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_delete_instructor(client, default_instructor['uid'], expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_delete_instructor(client, default_instructor['uid'], expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        instructor = _api_add_instructor(client)
        _api_delete_instructor(client, instructor['uid'])

    def test_invalid_uid(self, client, fake_auth):
        """Fails silently when instructor does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_instructor(client, uid='987654')


class TestGetInstructors:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_instructors(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        """Denies anonymous user."""

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client)
        instructors = _api_get_instructors(client)
        assert len(instructors) == 1
        assert instructors[0]['uid'] == default_instructor['uid']
        assert instructors[0]['csid'] == default_instructor['csid']
        assert instructors[0]['firstName'] == default_instructor['firstName']
        assert instructors[0]['lastName'] == default_instructor['lastName']
        assert instructors[0]['email'] == default_instructor['emailAddress']


class TestSearchInstructors:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_search_instructors(client, expected_status_code=401)

    def test_search_by_uid(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='713')
        assert len(results) == 1
        assert results[0]['uid'] == '713836'
        assert results[0]['csid'] == '6856470'
        assert results[0]['firstName'] == 'Mlskagctr'
        assert results[0]['lastName'] == 'Wondwzckm'
        assert results[0]['email'] == 'wdjmytek@berkeley.edu'

    def test_search_by_name(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='Mlskagctr Wo')
        assert len(results) == 1
        assert results[0]['uid'] == '713836'
        assert results[0]['csid'] == '6856470'
        assert results[0]['firstName'] == 'Mlskagctr'
        assert results[0]['lastName'] == 'Wondwzckm'
        assert results[0]['email'] == 'wdjmytek@berkeley.edu'

    def test_search_by_name_containing_space(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='Herman P.')
        assert len(results) == 1
        assert results[0]['uid'] == '486858'

    def test_search_by_name_containing_hyphen(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='kiser-go')
        assert len(results) == 1
        assert results[0]['uid'] == '87828'

    def test_search_by_name_containing_apostrophe(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet="O'BLIVION")
        assert len(results) == 1
        assert results[0]['uid'] == '351096'

    def test_search_manually_added_instructor(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_add_instructor(client)
        fake_auth.login(non_admin_uid)
        instructors = _api_search_instructors(client, snippet='1234')
        assert len(instructors) == 1
        assert instructors[0]['uid'] == default_instructor['uid']
        assert instructors[0]['csid'] == default_instructor['csid']
        assert instructors[0]['firstName'] == default_instructor['firstName']
        assert instructors[0]['lastName'] == default_instructor['lastName']
        assert instructors[0]['email'] == default_instructor['emailAddress']

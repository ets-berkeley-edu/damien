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

from damien.models.department import Department


non_admin_uid = '100'
admin_uid = '200'


def _api_enrolled_departments(client, expected_status_code=200):
    response = client.get('/api/departments/enrolled')
    assert response.status_code == expected_status_code
    return response.json


class TestEnrolledDepartments:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_enrolled_departments(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_enrolled_departments(client, expected_status_code=403)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        departments = _api_enrolled_departments(client)
        assert len(departments) == 82
        for d in departments:
            assert d['deptName']
            assert d['isEnrolled']
            assert d['createdAt']
            assert d['updatedAt']
        agrs = next(d for d in departments if d['deptName'] == 'Ancient Greek and Roman Studies')
        assert agrs['catalogListings'] == {
            'AGRS': ['*'],
            'CLASSIC': ['*'],
            'GREEK': ['*'],
            'LATIN': ['*'],
        }
        calteach = next(d for d in departments if d['deptName'] == 'CalTeach')
        assert calteach['catalogListings'] == {
            'CALTEACH': ['*'],
            'EDSTEM': ['*'],
            'EDUC': ['130', '131AC'],
            'HISTORY': ['138T', '180T', '182AT'],
            'UGIS': ['82', '187', '188', '189', '303'],
        }


def _api_get_department(client, expected_status_code=200):
    dept = Department.find_by_name('Philosophy')
    response = client.get(f'/api/department/{dept.id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetDepartment:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_department(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Returns a contactless response to non-admin user."""
        fake_auth.login(non_admin_uid)
        department = _api_get_department(client)
        assert department['catalogListings'] == {'PHILOS': ['*']}
        assert department['deptName'] == 'Philosophy'
        assert department['isEnrolled'] is True
        assert department['note'] is None
        assert 'contacts' not in department

    def test_admin_authorized(self, client, fake_auth):
        """Returns response including dept contacts to admin user."""
        fake_auth.login(admin_uid)
        department = _api_get_department(client)
        assert department['catalogListings'] == {'PHILOS': ['*']}
        assert department['contacts'][0]['csid'] == '100100100'
        assert department['contacts'][0]['uid'] == '100'
        assert department['contacts'][0]['firstName'] == 'Father'
        assert department['contacts'][0]['lastName'] == 'Brennan'
        assert department['contacts'][0]['email'] == 'fatherbrennan@berkeley.edu'
        assert department['deptName'] == 'Philosophy'
        assert department['isEnrolled'] is True
        assert department['note'] is None


def _api_update_department(client, params={}, expected_status_code=200):
    dept = Department.find_by_name('Philosophy')
    response = client.post(
        f'/api/department/{dept.id}',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestUpdateDepartment:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_department(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_update_department(client, expected_status_code=403)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        assert department.note is None

        note = """It is the greatest mystery of all because no human being will ever solve it.
            It is the highest suspense because no man can bear it.
            It is the greatest fear because it is the ancient fear of the unknown.
            It is a warning foretold for thousands of years. It is our final warning.
            It is The Omen."""
        department = _api_update_department(client, {'note': note})
        assert department['note'] == note

        department = _api_update_department(client)
        assert department['note'] is None

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

from damien import std_commit
from damien.models.department import Department
from damien.models.user import User


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


def _api_get_department(client, term_id=None, expected_status_code=200):
    dept = Department.find_by_name('Philosophy')
    if term_id:
        response = client.get(f'/api/department/{dept.id}?term_id={term_id}')
    else:
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

    def test_bad_term(self, client, fake_auth):
        """Rejects invalid term id."""
        fake_auth.login(admin_uid)
        _api_get_department(client, term_id='1666', expected_status_code=400)

    def test_good_term(self, client, fake_auth):
        """Accepts valid term ids."""
        fake_auth.login(admin_uid)
        _api_get_department(client, term_id='2218')
        _api_get_department(client, term_id='2222')


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


def _api_update_contact(client, dept_id=None, params={}, expected_status_code=200):
    if dept_id is None:
        dept = Department.find_by_name('Philosophy')
        dept_id = dept.id
    response = client.post(
        f'/api/department/{dept_id}/contact',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestUpdateDepartmentContact:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_contact(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_update_contact(client, expected_status_code=403)

    def test_unknown_dept(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_update_contact(client, dept_id=0, expected_status_code=404)

    def test_unknown_user(self, client, fake_auth):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        original_count = len(department.members)
        params = {
            'email': 'spooky@boo.edu',
            'firstName': 'Spooky',
            'lastName': 'Ghost',
            'uid': 0,
            'userId': 0,
        }
        _api_update_contact(client, params=params, expected_status_code=404)

        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count

    def test_authorized(self, client, fake_auth, app):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        original_count = len(department.members)
        User.create(
            csid='126000',
            uid='4200',
            email='am@berkeley.edu',
            first_name='Ansel',
            last_name='Manchester',
        )
        std_commit(allow_test_environment=True)
        user = User.find_by_uid('4200')
        params = {
            'canViewResponseRates': True,
            'csid': user.csid,
            'email': 'ansel@angelfire.net',
            'firstName': user.first_name,
            'lastName': user.last_name,
            'uid': user.uid,
            'userId': user.id,
        }

        contact = _api_update_contact(client, dept_id=department.id, params=params)

        assert contact['departmentId'] == str(department.id)
        assert contact['userId'] == user.id
        assert contact['canViewResponseRates'] is True
        assert contact['uid'] == user.uid
        assert contact['email'] == params['email']
        assert contact['firstName'] == user.first_name
        assert contact['lastName'] == user.last_name
        assert contact['csid'] == user.csid

        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count + 1

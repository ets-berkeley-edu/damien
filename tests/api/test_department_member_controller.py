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
from damien.models.department_member import DepartmentMember
from damien.models.user import User


non_admin_uid = '100'
admin_uid = '200'


def _api_delete_contact(client, dept_id=None, user_id=None, expected_status_code=200):
    if not dept_id:
        dept = Department.find_by_name('Philosophy')
        dept_id = dept.id
    if not user_id:
        user_id = dept.members[0].user_id
    response = client.delete(f'/api/department/{dept_id}/contact/{user_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestDeleteDepartmentContact:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_delete_contact(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_delete_contact(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth, app):
        department = Department.find_by_name('Philosophy')
        user = User.create(
            csid='14400',
            uid='40',
            email='dt@b.e',
            first_name='Dake',
            last_name='Traphagen',
        )
        DepartmentMember.create(department.id, user.id)
        std_commit(allow_test_environment=True)
        original_count = len(department.members)

        fake_auth.login(admin_uid)
        response = _api_delete_contact(client, user_id=user.id)
        assert response['message']

        std_commit(allow_test_environment=True)
        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count - 1

    def test_invalid_dept_id(self, client, fake_auth):
        """Fails silently when department does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_contact(client, dept_id=0)

    def test_invalid_user_id(self, client, fake_auth):
        """Fails silently when user does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_contact(client, user_id=0)


def _api_notify_contacts(client, recipient=None, expected_status_code=200):
    if not recipient:
        user = User.find_by_uid(non_admin_uid)
        recipient = [m.to_api_json() for m in user.department_memberships]
    params = {
        'message': 'OUR FINAL WARNING',
        'recipient': recipient,
        'subject': 'Good morning. You are one day closer to the end of the world. You have been warned.',
    }
    response = client.post(
        '/api/department/contacts/notify',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestNotifyContacts:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_notify_contacts(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_notify_contacts(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Authorized user can send an email."""
        fake_auth.login(admin_uid)
        dept = Department.find_by_name('Freshman and Sophomore Seminars')
        recipient = [m.to_api_json() for m in dept.members]
        intended_recipient = [r['email'] for r in recipient if r['canReceiveCommunications']]

        response = _api_notify_contacts(client, recipient=recipient)
        assert response['message'] == f'Email sent to {intended_recipient}'


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
        _api_update_contact(client, expected_status_code=401)

    def test_unknown_dept(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_update_contact(client, dept_id=0, expected_status_code=404)

    def test_unknown_user(self, client, fake_auth):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        original_count = len(department.members)
        params = {
            'canReceiveCommunications': True,
            'canViewReports': True,
            'canViewResponseRates': False,
            'csid': None,
            'email': 'spooky@boo.edu',
            'firstName': 'Spooky',
            'lastName': 'Ghost',
            'uid': '0',
        }
        _api_update_contact(client, params=params)
        std_commit(allow_test_environment=True)

        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count + 1
        new_user = User.find_by_uid('0')
        assert new_user

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
            'canReceiveCommunications': False,
            'canViewReports': True,
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
        assert contact['canReceiveCommunications'] is False
        assert contact['canViewReports'] is True
        assert contact['canViewResponseRates'] is True
        assert contact['uid'] == user.uid
        assert contact['email'] == params['email']
        assert contact['firstName'] == user.first_name
        assert contact['lastName'] == user.last_name
        assert contact['csid'] == user.csid

        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count + 1


def _api_update_department_note(client, params={}, expected_status_code=200):
    dept = Department.find_by_name('Philosophy')
    response = client.post(
        f'/api/department/{dept.id}/note',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestUpdateDepartmentNote:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_department_note(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_update_department_note(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        assert department.notes == []

        note = """It is the greatest mystery of all because no human being will ever solve it.
            It is the highest suspense because no man can bear it.
            It is the greatest fear because it is the ancient fear of the unknown.
            It is a warning foretold for thousands of years. It is our final warning.
            It is The Omen."""
        department_note = _api_update_department_note(client, {'note': note})
        assert department_note['note'] == note

        department_note = _api_update_department_note(client)
        assert department_note['note'] is None
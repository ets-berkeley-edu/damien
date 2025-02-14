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

from damien import std_commit
from damien.models.department import Department
from damien.models.department_form import DepartmentForm
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
        user = User.create_or_restore(
            csid='14400',
            uid='40',
            email='dt@b.e',
            first_name='Dake',
            last_name='Traphagen',
        )
        user_id = user.id
        DepartmentMember.create(department.id, user_id)
        std_commit(allow_test_environment=True)
        original_count = len(department.members)

        fake_auth.login(admin_uid)
        response = _api_delete_contact(client, user_id=user_id)
        assert response['message']

        std_commit(allow_test_environment=True)
        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count - 1

        user = User.query.filter_by(id=user_id).first()
        assert user.deleted_at is not None

    def test_invalid_dept_id(self, client, fake_auth):
        """Fails silently when department does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_contact(client, dept_id=0)

    def test_invalid_user_id(self, client, fake_auth):
        """Fails silently when user does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_contact(client, user_id=0)


def _api_notify_contacts(client, department_ids, expected_status_code=200):
    depts = [Department.find_by_id(_id) for _id in department_ids]
    recipient = [
        {
            'deptName': dept.dept_name,
            'deptId': dept.id,
            'recipients': [m.to_api_json() for m in dept.members],
        } for dept in depts
    ]
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

    def test_anonymous(self, client, history_id):
        """Denies anonymous user."""
        _api_notify_contacts(client, [history_id], expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, history_id):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_notify_contacts(client, [history_id], expected_status_code=401)

    def test_authorized(self, client, fake_auth, history_id):
        """Authorized user can send an email."""
        fake_auth.login(admin_uid)
        history_dept = Department.find_by_id(history_id)
        history_contacts = [m.to_api_json() for m in history_dept.members]
        intended_recipient = {
            history_dept.dept_name: [c['email'] for c in history_contacts if c['canReceiveCommunications']],
        }

        response = _api_notify_contacts(client, [history_id])
        assert response['message'] == f'Email sent to {intended_recipient}'

    def test_bulk_notification(self, client, fake_auth, history_id, melc_id):
        """Bulk option sends one email per department."""
        fake_auth.login(admin_uid)
        history_dept = Department.find_by_id(history_id)
        history_contacts = [m.to_api_json() for m in history_dept.members]
        melc_dept = Department.find_by_id(melc_id)
        melc_contacts = [m.to_api_json() for m in melc_dept.members]
        intended_recipient = {
            history_dept.dept_name: [c['email'] for c in history_contacts if c['canReceiveCommunications']],
            melc_dept.dept_name: [c['email'] for c in melc_contacts if c['canReceiveCommunications']],
        }

        response = _api_notify_contacts(client, [history_id, melc_id])
        assert response['message'] == f'Email sent to {intended_recipient}'

    def test_deleted_contact(self, client, fake_auth, history_id):
        """A deleted contact does not receive notifications."""
        fake_auth.login(admin_uid)
        history_dept = Department.find_by_id(history_id)

        deleted_contact = history_dept.members[0]
        deleted_email = deleted_contact.user.email
        DepartmentMember.delete(department_id=history_id, user_id=deleted_contact.user.id)
        std_commit(allow_test_environment=True)

        history_contacts = [m.to_api_json() for m in history_dept.members]
        assert deleted_email not in [m['email'] for m in history_contacts]

        intended_recipient = {
            history_dept.dept_name: [c['email'] for c in history_contacts if c['canReceiveCommunications']],
        }

        response = _api_notify_contacts(client, [history_id])
        assert response['message'] == f'Email sent to {intended_recipient}'
        assert deleted_email not in response['message']


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
        _api_delete_contact(client, user_id=new_user.id)
        std_commit(allow_test_environment=True)

    def test_authorized(self, client, fake_auth, app):
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        original_count = len(department.members)
        User.create_or_restore(
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

    def test_add_remove_dept_forms(self, client, fake_auth, history_id, form_history_id, form_melc_id):
        fake_auth.login(admin_uid)
        department = Department.find_by_id(history_id)
        User.create_or_restore(
            csid='294982',
            uid='23948',
            email='sb@berkeley.edu',
            first_name='Smedley',
            last_name='Bretile',
        )
        std_commit(allow_test_environment=True)
        user = User.find_by_uid('23948')

        # Add HISTORY
        history_form = DepartmentForm.find_by_id(form_history_id)
        params = {
            'csid': user.csid,
            'canReceiveCommunications': False,
            'departmentForms': [history_form.to_api_json()],
            'email': user.email,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'uid': user.uid,
            'userId': user.id,
        }
        contact = _api_update_contact(client, dept_id=department.id, params=params)
        assert contact['departmentId'] == str(department.id)
        assert contact['userId'] == user.id
        assert len(contact['departmentForms']) == 1
        assert contact['departmentForms'][0]['name'] == 'HISTORY'

        # Remove HISTORY and add MELC
        melc_form = DepartmentForm.find_by_id(form_melc_id)
        params['departmentForms'] = [melc_form.to_api_json()]
        contact = _api_update_contact(client, dept_id=department.id, params=params)
        # assert contact['departmentId'] == str(department.id)
        assert contact['userId'] == user.id
        assert len(contact['departmentForms']) == 1
        assert contact['departmentForms'][0]['name'] == 'MELC'

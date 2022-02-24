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


def _api_enrolled_departments(client, include_contacts=False, include_sections=False, expected_status_code=200):
    response = client.get(f'/api/departments/enrolled?c={int(include_contacts)}&s={int(include_sections)}')
    assert response.status_code == expected_status_code
    return response.json


class TestEnrolledDepartments:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_enrolled_departments(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_enrolled_departments(client, expected_status_code=401)

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

    def test_include_contacts_and_sections(self, client, fake_auth):
        fake_auth.login(admin_uid)
        departments = _api_enrolled_departments(client, include_contacts=True, include_sections=True)
        assert len(departments) == 82
        for d in departments:
            assert 'contacts' in d
            assert 'totalSections' in d
            assert d['isEnrolled']


def _api_get_melc(client, expected_status_code=200):
    dept = Department.find_by_name('Middle Eastern Languages and Cultures')
    response = client.get(f'/api/department/{dept.id}')
    assert response.status_code == expected_status_code
    return response.json


def _api_get_philosophy(client, term_id=None, expected_status_code=200):
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
        _api_get_philosophy(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Returns a contactless response to non-admin user."""
        fake_auth.login(non_admin_uid)
        department = _api_get_philosophy(client)
        assert department['catalogListings'] == {'PHILOS': ['*']}
        assert department['deptName'] == 'Philosophy'
        assert department['isEnrolled'] is True
        assert department['note'] is None
        assert 'contacts' not in department

    def test_admin_authorized(self, client, fake_auth):
        """Returns response including dept contacts to admin user."""
        fake_auth.login(admin_uid)
        department = _api_get_philosophy(client)
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
        _api_get_philosophy(client, term_id='1666', expected_status_code=400)

    def test_good_term(self, client, fake_auth):
        """Accepts valid term ids."""
        fake_auth.login(admin_uid)
        _api_get_philosophy(client, term_id='2218')
        _api_get_philosophy(client, term_id='2222')

    def test_default_evaluations(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 39
        for e in department['evaluations']:
            assert e['subjectArea'] in ('MELC', 'CUNEIF')
        elementary_sumerian = next(e for e in department['evaluations'] if e['subjectArea'] == 'CUNEIF' and e['catalogId'] == '102B')
        assert elementary_sumerian['termId'] == '2222'
        assert elementary_sumerian['courseNumber'] == '30659'
        assert elementary_sumerian['instructionFormat'] == 'LEC'
        assert elementary_sumerian['sectionNumber'] == '001'
        assert elementary_sumerian['courseTitle'] == 'Elementary Sumerian'
        assert elementary_sumerian['status'] is None
        assert elementary_sumerian['departmentForm']['name'] == 'CUNEIF'
        assert elementary_sumerian['evaluationType']['name'] == 'F'
        assert elementary_sumerian['instructor'] == {
            'uid': '637739',
            'sisId': '360000',
            'firstName': 'Ishtar',
            'lastName': 'Uruk',
            'emailAddress': 'ishtar@berkeley.edu',
            'affiliations': 'EMPLOYEE-TYPE-ACADEMIC',
        }
        assert elementary_sumerian['id'] == '_2222_30659_637739'


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
        _api_update_department(client, expected_status_code=401)

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
        _api_update_contact(client, expected_status_code=401)

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
        assert contact['canViewReports'] is True
        assert contact['canViewResponseRates'] is True
        assert contact['uid'] == user.uid
        assert contact['email'] == params['email']
        assert contact['firstName'] == user.first_name
        assert contact['lastName'] == user.last_name
        assert contact['csid'] == user.csid

        department = Department.find_by_name('Philosophy')
        assert len(department.members) == original_count + 1


def _api_update_evaluation(client, dept_id=None, params={}, expected_status_code=200):
    if dept_id is None:
        dept = Department.find_by_name('Middle Eastern Languages and Cultures')
        dept_id = dept.id
    response = client.post(
        f'/api/department/{dept_id}/evaluations',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestUpdateEvaluationStatus:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_evaluation(client, expected_status_code=401)

    def test_unknown_dept(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, dept_id=0, expected_status_code=404)

    def test_no_action(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739']}, expected_status_code=400)

    def test_bad_action(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'xxxxx'}, expected_status_code=400)

    def test_no_evaluation_ids(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'action': 'confirm'}, expected_status_code=400)

    def test_bad_evaluation_ids(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'evaluationIds': ['xxxx'], 'action': 'confirm'}, expected_status_code=400)

    def test_confirm(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'confirm'})
        assert len(response) == 1
        assert response[0]['termId'] == '2222'
        assert response[0]['courseNumber'] == '30659'
        assert response[0]['courseTitle'] == 'Elementary Sumerian'
        assert response[0]['instructor']['uid'] == '637739'
        assert response[0]['status'] == 'confirmed'
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'

    def test_mark(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'mark'})
        assert len(response) == 1
        assert response[0]['termId'] == '2222'
        assert response[0]['courseNumber'] == '30659'
        assert response[0]['courseTitle'] == 'Elementary Sumerian'
        assert response[0]['instructor']['uid'] == '637739'
        assert response[0]['status'] == 'review'
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'


class TestDuplicateEvaluation:

    def test_duplicate(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'duplicate'})
        assert len(response) == 2
        assert response[0]['id'] != response[1]['id']
        for r in response:
            assert r['termId'] == '2222'
            assert r['courseNumber'] == '30659'
            assert r['courseTitle'] == 'Elementary Sumerian'
            assert r['instructor']['uid'] == '637739'
            assert r['transientId'] == '_2222_30659_637739'
            assert r['id'] == int(r['id'])


class TestEditEvaluation:

    def test_no_fields(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'edit'}, expected_status_code=400)

    def test_bad_fields(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'ill': 'communication'},
        }, expected_status_code=400)

    def test_bad_dept_form(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'departmentFormId': 'zyzzyva'},
        }, expected_status_code=400)

    def test_nonexistent_dept_form(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'departmentFormId': 99999},
        }, expected_status_code=400)

    def test_edit_department_form(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'departmentFormId': '13'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'
        assert response[0]['departmentForm']['id'] == 13

    def test_bad_eval_type(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'evaluationTypeId': 'zyzzyva'},
        }, expected_status_code=400)

    def test_nonexistent_eval_type(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'evaluationTypeId': 99999},
        }, expected_status_code=400)

    def test_edit_evaluation_type(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'evaluationTypeId': '3'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'
        assert response[0]['evaluationType']['id'] == 3

    def test_bad_date(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'startDate': 'ill', 'endDate': 'communication'},
        }, expected_status_code=400)

    def test_edit_dates(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'startDate': '2022-02-14', 'endDate': '2022-05-01'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'
        assert response[0]['startDate'] == '2022-02-14'
        assert response[0]['endDate'] == '2022-05-01'

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
from damien.models.evaluation import Evaluation
from tests.util import override_config


non_admin_uid = '100'
admin_uid = '200'


def _api_enrolled_departments(client, include_contacts=False, include_sections=False, include_status=False, expected_status_code=200):
    response = client.get(f'/api/departments/enrolled?c={int(include_contacts)}&s={int(include_sections)}&t={int(include_status)}')
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
        assert len(departments) == 84
        for d in departments:
            assert d['deptName']
            assert d['enrolledTerms']
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
        assert agrs['enrolledTerms'] == ['2218', '2222']
        calteach = next(d for d in departments if d['deptName'] == 'CalTeach')
        assert calteach['catalogListings'] == {
            'CALTEACH': ['*'],
            'EDSTEM': ['*'],
            'EDUC': ['130', '131AC'],
            'HISTORY': ['138T', '180T', '182AT'],
            'UGIS': ['82', '187', '188', '189', '303'],
        }
        assert calteach['enrolledTerms'] == ['2218', '2222']

    def test_include_contacts_sections_and_status(self, client, fake_auth):
        fake_auth.login(admin_uid)
        departments = _api_enrolled_departments(client, include_contacts=True, include_sections=True, include_status=True)
        assert len(departments) == 84
        for d in departments:
            assert 'contacts' in d
            assert 'enrolledTerms' in d
            assert 'lastUpdated' in d
            assert 'totalBlockers' in d
            assert 'totalConfirmed' in d
            assert 'totalEvaluations' in d
            assert 'totalInError' in d
            assert 'totalSections' in d
            assert d['isEnrolled']


def _api_get_history(client, expected_status_code=200):
    dept = Department.find_by_name('History')
    response = client.get(f'/api/department/{dept.id}')
    assert response.status_code == expected_status_code
    return response.json


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
        assert 'contacts' in department

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
        assert department['contacts'][0]['departmentForms'][0]['name'] == 'PHILOS'
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
        fall = _api_get_philosophy(client, term_id='2218')
        assert fall['evaluationTerm']['isLocked'] is True
        spring = _api_get_philosophy(client, term_id='2222')
        assert spring['evaluationTerm']['isLocked'] is False

    def test_default_evaluations(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 44
        for e in department['evaluations']:
            assert (e['subjectArea'] in ('MELC', 'CUNEIF')) or e.get('crossListedWith') or e.get('roomSharedWith')
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

    def test_default_dates(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        for e in department['evaluations']:
            assert e['startDate'] == '2022-04-18'
            assert e['endDate'] == '2022-05-08'

    def test_uid_not_in_sis_instructors(self, client, fake_auth):
        """When a sis_section has no matching sis_instructor, returns only the instructor UID."""
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        persian = next(e for e in department['evaluations'] if e['subjectArea'] == 'MELC' and e['catalogId'] == 'R1B')
        assert persian['instructor'] == {
            'uid': '999999',
            'sisId': None,
            'firstName': None,
            'lastName': None,
            'emailAddress': None,
        }

    def test_include_cross_listing(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        cross_listings = [e for e in department['evaluations'] if e['subjectArea'] == 'HISTORY' and e['catalogId'] == 'C188C']
        assert len(cross_listings) == 2
        for cl in cross_listings:
            assert cl['courseNumber'] == '30643'
            assert cl['crossListedWith'] == ['30470']
            assert cl['departmentForm'] is None
        home_dept_rows = [e for e in department['evaluations'] if e['courseNumber'] == '30470']
        for hdr in home_dept_rows:
            assert hdr['crossListedWith'] == ['30643']
            assert hdr['departmentForm'] is None

    def test_custom_evaluation_types(self, client, fake_auth):
        """Refrain from supplying default evaluation types for catalog listings using custom evaluation types."""
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        for e in department['evaluations']:
            if e['subjectArea'] == 'HISTORY':
                assert e['evaluationType'] is None
            elif e.get('instructor', {}).get('affiliations'):
                assert e['evaluationType']

    def test_include_room_share(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        room_share = next(e for e in department['evaluations'] if e['subjectArea'] == 'JEWISH' and e['catalogId'] == '120A')
        assert room_share['courseNumber'] == '32159'
        assert room_share['roomSharedWith'] == ['30462']
        assert room_share['departmentForm'] is None
        home_dept_row = next(e for e in department['evaluations'] if e['courseNumber'] == '30462')
        assert home_dept_row['roomSharedWith'] == ['32159']
        assert home_dept_row['departmentForm'] is None

    def test_cross_list_and_room_share(self, client, fake_auth):
        """Cross-listings take precedence over room shares."""
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        xlist_1 = next(e for e in department['evaluations'] if e['courseNumber'] == '31742')
        xlist_2 = next(e for e in department['evaluations'] if e['courseNumber'] == '31120')
        room_share = next(e for e in department['evaluations'] if e['courseNumber'] == '30455')
        assert xlist_1['crossListedWith'] == ['31120']
        assert 'roomSharedWith' not in xlist_1
        assert xlist_2['crossListedWith'] == ['31742']
        assert 'roomSharedWith' not in xlist_2
        assert 'crossListedWith' not in room_share
        assert room_share['roomSharedWith'] == ['31120', '31742']

    def test_single_section_feed(self, client, fake_auth, melc_id):
        """Sorts section evalutions by type, then form, then instructor, then start date."""
        fake_auth.login(non_admin_uid)
        response = client.get(f'/api/department/{melc_id}/section_evaluations/30666')
        assert response.status_code == 200
        feed = response.json
        assert len(feed) == 5
        assert feed[0]['courseNumber'] == '30666'
        assert feed[0]['evaluationType']['name'] == 'F'
        assert feed[0]['departmentForm']['name'] == 'MELC'
        assert feed[0]['instructor']['lastName'] == 'Riddle'
        assert feed[0]['startDate'] == '2022-04-18'
        assert feed[1]['courseNumber'] == '30666'
        assert feed[1]['evaluationType']['name'] == 'F'
        assert feed[1]['departmentForm']['name'] == 'MELC'
        assert feed[1]['instructor']['lastName'] == 'Wade'
        assert feed[1]['startDate'] == '2022-04-18'
        assert feed[2]['courseNumber'] == '30666'
        assert feed[2]['evaluationType']['name'] == 'G'
        assert feed[2]['departmentForm']['name'] == 'MELC'
        assert feed[2]['instructor']['lastName'] == 'Bachelor'
        assert feed[2]['startDate'] == '2022-03-31'
        assert feed[3]['courseNumber'] == '30666'
        assert feed[3]['evaluationType']['name'] == 'G'
        assert feed[3]['departmentForm']['name'] == 'MELC'
        assert feed[3]['instructor']['lastName'] == 'O\'Blivion'
        assert feed[3]['startDate'] == '2022-02-21'
        assert feed[4]['courseNumber'] == '30666'
        assert feed[4]['evaluationType']['name'] == 'G'
        assert feed[4]['departmentForm']['name'] == 'MELC'
        assert feed[4]['instructor']['lastName'] == 'Waterman'
        assert feed[4]['startDate'] == '2022-04-18'

    def test_nonstandard_default_dept_form(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        dept = Department.find_by_name('Real Estate Development and Design')
        response = client.get(f'/api/department/{dept.id}')
        assert response.status_code == 200
        ldarch_254 = next(e for e in response.json['evaluations'] if e['subjectArea'] == 'LDARCH' and e['catalogId'] == '254')
        assert (ldarch_254['departmentForm']['name'] == 'RDEV')
        assert (ldarch_254['defaultDepartmentForm']['name'] == 'RDEV')

    def test_no_default_dept_form(self, client, fake_auth, app):
        with override_config(app, 'CURRENT_TERM_ID', '2235'):
            fake_auth.login(non_admin_uid)
            dept = Department.find_by_name('Summer Sessions Online')
            response = client.get(f'/api/department/{dept.id}?term_id=2235')
            assert response.status_code == 200
            assert len(response.json['evaluations']) == 0


def _api_update_evaluation(client, dept_id=None, params=None, term_id='2222', expected_status_code=200):
    if dept_id is None:
        dept = Department.find_by_name('Middle Eastern Languages and Cultures')
        dept_id = dept.id
    response = client.post(
        f'/api/department/{dept_id}/evaluations?term_id={term_id}',
        data=json.dumps(params or {}),
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

    def test_invalid_term_id(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        params = {'evaluationIds': ['_2222_30659_637739'], 'action': 'confirm'}
        _api_update_evaluation(client, params=params, term_id='abc', expected_status_code=400)
        _api_update_evaluation(client, params=params, term_id='1234', expected_status_code=400)

    def test_confirm_invalid(self, client, fake_auth):
        # First, create an evaluation with missing instructor, department form and evaluation type
        dept = Department.find_by_name('Middle Eastern Languages and Cultures')
        Evaluation.create(term_id='2222', course_number='12345', department_id=dept.id)
        std_commit(allow_test_environment=True)
        incomplete_eval = Evaluation.fetch_by_course_numbers('2222', ['12345'])['12345'][0]
        incomplete_eval.valid = False
        std_commit(allow_test_environment=True)
        incomplete_eval = Evaluation.fetch_by_course_numbers('2222', ['12345'])['12345'][0]
        assert incomplete_eval.department_form_id is None
        assert incomplete_eval.evaluation_type_id is None
        assert incomplete_eval.instructor_uid is None
        assert incomplete_eval.status is None

        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={'evaluationIds': [incomplete_eval.id], 'action': 'confirm'}, expected_status_code=400)

    def test_update_status_confirm_conflicts(self, client, fake_auth, history_id, form_melc_id, form_history_id, type_f_id, type_g_id):
        """Prevents duplicate evaluations for the same instructor from being confirmed with conflicting fields."""
        # First, create two evaluations with the same course and instructor but conflicting department form, evaluation type, and start date
        dept = Department.find_by_id(history_id)
        course_number = '30123'
        instructor_uid = '326054'
        Evaluation.create(
            term_id='2222',
            course_number=course_number,
            department_id=dept.id,
            instructor_uid=instructor_uid,
            department_form_id=form_melc_id,
            evaluation_type_id=type_f_id,
            start_date='2022-03-15',
        )
        Evaluation.create(
            term_id='2222',
            course_number=course_number,
            department_id=dept.id,
            instructor_uid=instructor_uid,
            department_form_id=form_history_id,
            evaluation_type_id=type_g_id,
            start_date='2022-04-15',
        )
        std_commit(allow_test_environment=True)

        evals = Evaluation.fetch_by_course_numbers('2222', [course_number])[course_number]
        evaluation_ids = [e.id for e in sorted(evals, key=lambda e: e.start_date)]
        assert len(evals) == 2

        fake_auth.login(non_admin_uid)

        # Try to confirm the two conflicting rows
        _api_update_evaluation(client, dept_id=dept.id, params={'evaluationIds': evaluation_ids, 'action': 'confirm'}, expected_status_code=400)

        # Confirm the first row, then try to confirm the second row
        _api_update_evaluation(client, dept_id=dept.id, params={'evaluationIds': [evaluation_ids[0]], 'action': 'confirm'})
        _api_update_evaluation(client, dept_id=dept.id, params={'evaluationIds': [evaluation_ids[1]], 'action': 'confirm'}, expected_status_code=400)

        # Try to confirm the second row while resolving some but not all conflicts
        _api_update_evaluation(client, dept_id=dept.id, params={
            'evaluationIds': [evaluation_ids[1]],
            'fields': {'departmentFormId': form_melc_id, 'status': 'confirmed'},
            'action': 'edit',
        }, expected_status_code=400)
        _api_update_evaluation(client, dept_id=dept.id, params={
            'evaluationIds': [evaluation_ids[1]],
            'fields': {'startDate': '2022-03-15', 'status': 'confirmed'},
            'action': 'edit',
        }, expected_status_code=400)
        _api_update_evaluation(client, dept_id=dept.id, params={
            'evaluationIds': [evaluation_ids[1]],
            'fields': {'evaluationTypeId': type_f_id, 'status': 'confirmed'},
            'action': 'edit',
        }, expected_status_code=400)

        # Mark the first row Ignore, then confirm the second row
        _api_update_evaluation(client, dept_id=dept.id, params={'evaluationIds': [evaluation_ids[0]], 'action': 'ignore'})
        _api_update_evaluation(client, dept_id=dept.id, params={'evaluationIds': [evaluation_ids[1]], 'action': 'confirm'})

        # Resolve all conflicts and confirm succeeds
        _api_update_evaluation(client, dept_id=dept.id, params={
            'evaluationIds': [evaluation_ids[1]],
            'fields': {'departmentFormId': form_melc_id, 'evaluationTypeId': type_f_id, 'startDate': '2022-03-15', 'status': 'confirmed'},
            'action': 'edit',
        })

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
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30659_637739'
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.department_form is not None
        assert updated.department_form.name == 'CUNEIF'
        assert updated.evaluation_type is not None
        assert updated.evaluation_type.name == 'F'
        assert updated.start_date is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid

    def test_mark_unmark(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={'evaluationIds': ['_2222_30659_637739'], 'action': 'review'})
        assert len(response) == 1
        assert response[0]['termId'] == '2222'
        assert response[0]['courseNumber'] == '30659'
        assert response[0]['courseTitle'] == 'Elementary Sumerian'
        assert response[0]['instructor']['uid'] == '637739'
        assert response[0]['status'] == 'review'
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30659_637739'
        evaluation_id = response[0]['id']
        updated = Evaluation.find_by_id(evaluation_id)
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid
        response = _api_update_evaluation(client, params={'evaluationIds': [evaluation_id], 'action': 'unmark'})
        assert response[0]['courseNumber'] == '30659'
        assert response[0]['id'] == evaluation_id
        assert response[0]['lastUpdated'] is not None
        assert response[0]['status'] is None
        updated = Evaluation.find_by_id(evaluation_id)
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid


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
            assert r['lastUpdated'] is not None
            assert r['startDate'] == '2022-04-18'
            updated = Evaluation.find_by_id(r['id'])
            assert updated.created_by == non_admin_uid
            assert updated.updated_at is not None
            assert updated.updated_by == non_admin_uid

    def test_duplicate_for_midterm(self, client, fake_auth):
        from tests.api.test_department_form_controller import _api_add_department_form
        fake_auth.login(admin_uid)
        _api_add_department_form(client, 'CUNEIF_MID')

        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(
            client,
            params={
                'evaluationIds': ['_2222_30659_637739'],
                'action': 'duplicate',
                'fields': {'midterm': 'true', 'startDate': '2022-03-01'},
            },
        )
        assert len(response) == 2

        midterm_eval = next(r for r in response if r['startDate'] == '2022-03-01')
        assert midterm_eval['courseNumber'] == '30659'
        assert midterm_eval['courseTitle'] == 'Elementary Sumerian'
        assert midterm_eval['departmentForm']['name'] == 'CUNEIF_MID'
        assert midterm_eval['instructor']['uid'] == '637739'
        assert midterm_eval['lastUpdated'] is not None
        duplicate = Evaluation.find_by_id(midterm_eval['id'])
        assert duplicate.created_by == non_admin_uid
        assert duplicate.updated_at is not None
        assert duplicate.updated_by == non_admin_uid

        final_eval = next(r for r in response if r['startDate'] == '2022-04-18')
        assert final_eval['courseNumber'] == '30659'
        assert final_eval['courseTitle'] == 'Elementary Sumerian'
        assert final_eval['departmentForm']['name'] == 'CUNEIF'
        assert final_eval['instructor']['uid'] == '637739'
        assert final_eval['lastUpdated'] is not None
        original = Evaluation.find_by_id(final_eval['id'])
        assert original.created_by == non_admin_uid
        assert original.updated_at is not None
        assert original.updated_by == non_admin_uid

        response = _api_update_evaluation(client, params={'evaluationIds': [midterm_eval['id'], final_eval['id']], 'action': 'review'})
        assert len(response) == 2
        for r in response:
            assert r['valid'] is True
            assert r['conflicts'] == {}

    def test_duplicate_midterm_crosslisted(self, client, fake_auth, form_melc_id):
        from tests.api.test_department_form_controller import _api_add_department_form
        fake_auth.login(admin_uid)
        form_melc_mid_id = _api_add_department_form(client, 'MELC_MID')['id']

        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(
            client,
            params={
                'evaluationIds': ['_2222_30470_326054'],
                'action': 'duplicate',
                'fields': {'midterm': 'true', 'startDate': '2022-03-01'},
            },
        )
        midterm_eval_id = next(r['id'] for r in response if r['startDate'] == '2022-03-01')
        final_eval_id = next(r['id'] for r in response if r['startDate'] == '2022-04-18')
        _api_update_evaluation(client, params={
            'evaluationIds': [midterm_eval_id],
            'action': 'edit',
            'fields': {'departmentFormId': form_melc_mid_id},
        })
        _api_update_evaluation(client, params={
            'evaluationIds': [final_eval_id],
            'action': 'edit',
            'fields': {'departmentFormId': form_melc_id},
        })

        fake_auth.login(non_admin_uid)
        melc_dept = _api_get_melc(client)
        melc_dept_listings = [e for e in melc_dept['evaluations'] if e['subjectArea'] == 'MELC'
                              and e['catalogId'] == 'C188' and e['instructor']['uid'] == '326054']
        assert len(melc_dept_listings) == 2
        assert next(dl for dl in melc_dept_listings if dl['departmentForm']['name'] == 'MELC_MID'
                    and dl['startDate'] == '2022-03-01' and dl['transientId'] == '_2222_30470_326054_midterm')
        assert next(dl for dl in melc_dept_listings if dl['departmentForm']['name'] == 'MELC'
                    and dl['startDate'] == '2022-04-18' and dl['transientId'] == '_2222_30470_326054_final')

        hist_dept = _api_get_history(client)
        hist_dept_listings = [e for e in hist_dept['evaluations'] if e['subjectArea'] == 'MELC'
                              and e['catalogId'] == 'C188' and e['instructor']['uid'] == '326054']
        assert len(hist_dept_listings) == 1
        assert next(dl for dl in hist_dept_listings if dl['departmentForm']['name'] == 'MELC'
                    and dl['startDate'] == '2022-04-18' and dl['transientId'] == '_2222_30470_326054')

    def test_duplicate_create_conflict(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(
            client,
            params={
                'evaluationIds': ['_2222_30457_824122'],
                'action': 'duplicate',
                'fields': {'startDate': '2022-04-20'},
            },
        )
        assert len(response) == 2
        assert response[0]['id'] != response[1]['id']
        assert response[0]['startDate'] == '2022-04-18'
        assert response[1]['startDate'] == '2022-04-20'
        for r in response:
            assert r['termId'] == '2222'
            assert r['courseNumber'] == '30457'
            assert r['courseTitle'] == 'Introduction to Ancient Egypt'
            assert r['instructor']['uid'] == '824122'
            assert r['transientId'] == '_2222_30457_824122'
            assert r['id'] == int(r['id'])
            assert r['lastUpdated'] is not None
            assert r['valid'] is True
            updated = Evaluation.find_by_id(r['id'])
            assert updated.created_by == non_admin_uid
            assert updated.updated_at is not None
            assert updated.updated_by == non_admin_uid

        # mark the two conflicting rows for review
        response = _api_update_evaluation(
            client,
            params={
                'evaluationIds': [response[0]['id'], response[1]['id']],
                'action': 'review',
                'fields': None,
            },
        )
        assert response[0]['conflicts']['evaluationPeriod'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': '2022-04-20'}]
        assert response[1]['conflicts']['evaluationPeriod'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': '2022-04-18'}]
        for r in response:
            assert r['status'] == 'review'
            assert r['valid'] is False


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
        department = _api_get_melc(client)
        # Department form for crosslisted course starts at None
        evaluation = next(e for e in department['evaluations'] if e['courseNumber'] == '30643' and e['instructor']['uid'] == '326054')
        assert evaluation['departmentForm'] is None
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30643_326054'],
            'action': 'edit',
            'fields': {'departmentFormId': '13'},
        })
        assert len(response) == 1
        assert response[0]['departmentForm']['id'] == 13
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30643_326054'
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid
        # Unset department form, reverting to None
        response = _api_update_evaluation(client, params={
            'evaluationIds': [response[0]['id']],
            'action': 'edit',
            'fields': {'departmentFormId': None},
        })
        assert len(response) == 1
        assert response[0]['departmentForm'] is None
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30643_326054'
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid

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
        department = _api_get_melc(client)
        # Initial id for evaluation type F
        evaluation = next(e for e in department['evaluations'] if e['courseNumber'] == '30659' and e['instructor']['uid'] == '637739')
        assert evaluation['evaluationType']['name'] == 'F'
        initial_evaluation_type_id = evaluation['evaluationType']['id']
        # Update evaluation type
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'evaluationTypeId': '3'},
        })
        assert len(response) == 1
        assert response[0]['evaluationType']['id'] == 3
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30659_637739'
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid
        # Unset evaluation type, reverting to initial value
        response = _api_update_evaluation(client, params={
            'evaluationIds': [response[0]['id']],
            'action': 'edit',
            'fields': {'evaluationTypeId': None},
        })
        assert len(response) == 1
        assert response[0]['evaluationType']['id'] == initial_evaluation_type_id
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['lastUpdated'] is not None
        assert response[0]['transientId'] == '_2222_30659_637739'
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid

    def test_bad_instructor_uid(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'instructorUid': 'Not A. Number III'},
        }, expected_status_code=400)

    def test_edit_instructor_uid(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'instructorUid': '434444'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_434444'
        assert response[0]['instructor']['uid'] == '434444'
        assert response[0]['instructor']['sisId'] == '6526140'
        assert response[0]['instructor']['firstName'] == 'Lxqtbhzei'
        assert response[0]['instructor']['lastName'] == 'Ybaehymnl'
        assert response[0]['instructor']['emailAddress'] == 'puejolbi@berkeley.edu'
        assert response[0]['lastUpdated'] is not None
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid

    def test_bad_date(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'startDate': 'ill communication'},
        }, expected_status_code=400)

    def test_date_before_term(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'startDate': '2021-12-25'},
        }, expected_status_code=400)

    def test_date_after_term(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'startDate': '2022-07-14'},
        }, expected_status_code=400)

    def test_edit_dates(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'startDate': '2022-04-01'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'
        assert response[0]['startDate'] == '2022-04-01'
        assert response[0]['endDate'] == '2022-04-21'
        assert response[0]['lastUpdated'] is not None
        updated = Evaluation.find_by_id(response[0]['id'])
        assert updated.created_at is not None
        assert updated.updated_at is not None
        assert updated.updated_by == non_admin_uid

    def test_edit_confirm_conflicts(self, client, fake_auth, history_id, form_melc_id, form_history_id, type_f_id, type_g_id):
        """Prevents duplicate evaluations for the same instructor from being confirmed with conflicting fields."""
        # First, create two identical evaluations in confirmed status
        dept = Department.find_by_id(history_id)
        course_number = '31234'
        instructor_uid = '326054'
        Evaluation.create(
            term_id='2222',
            course_number=course_number,
            department_id=dept.id,
            instructor_uid=instructor_uid,
            status='confirmed',
            department_form_id=form_melc_id,
            evaluation_type_id=type_f_id,
            start_date='2022-03-15',
        )
        Evaluation.create(
            term_id='2222',
            course_number=course_number,
            department_id=dept.id,
            instructor_uid=instructor_uid,
            status='confirmed',
            department_form_id=form_melc_id,
            evaluation_type_id=type_f_id,
            start_date='2022-03-15',
        )
        std_commit(allow_test_environment=True)
        evals = Evaluation.fetch_by_course_numbers('2222', [course_number])[course_number]
        evaluation_ids = [e.id for e in evals]
        assert len(evals) == 2

        fake_auth.login(non_admin_uid)
        # Try to update one of the rows with fields that would conflict with the other row
        params = {
            'action': 'edit',
            'evaluationIds': [evaluation_ids[0]],
            'fields': {
                'departmentFormId': form_history_id,
                'evaluationTypeId': type_g_id,
                'instructorUid': instructor_uid,
                'status': 'confirmed',
                'startDate': '2022-04-01',
            },
        }
        _api_update_evaluation(client, dept_id=dept.id, params=params, expected_status_code=400)

    def test_complete_and_confirm(self, client, fake_auth, type_f_id, form_melc_id):
        # First, create an evaluation with missing department form and evaluation type
        dept = Department.find_by_name('German')
        Evaluation.create(term_id='2222', course_number='12345', department_id=dept.id)
        std_commit(allow_test_environment=True)
        incomplete_eval = Evaluation.fetch_by_course_numbers('2222', ['12345'])['12345'][0]
        assert incomplete_eval.department_form_id is None
        assert incomplete_eval.evaluation_type_id is None
        assert incomplete_eval.status is None

        fake_auth.login(non_admin_uid)
        params = {
            'action': 'edit',
            'evaluationIds': [incomplete_eval.id],
            'fields': {
                'departmentFormId': form_melc_id,
                'evaluationTypeId': type_f_id,
                'instructorUid': '124434',
                'status': 'confirmed',
                'startDate': '2022-04-01',
            },
        }
        _api_update_evaluation(client, params=params)

        edited_eval = Evaluation.find_by_id(incomplete_eval.id)
        assert edited_eval.course_number == '12345'
        assert edited_eval.department_form_id == form_melc_id
        assert edited_eval.evaluation_type_id == type_f_id
        assert edited_eval.status == 'confirmed'
        assert edited_eval.updated_at is not None
        assert edited_eval.updated_at is not None
        assert edited_eval.updated_by == non_admin_uid


def _api_get_evaluation(client, dept_id, course_number, instructor_uid):
    response = client.get(f'/api/department/{dept_id}')
    return next((e for e in response.json['evaluations'] if e['courseNumber'] == course_number and e['instructor']['uid'] == instructor_uid), None)


def _api_update_history_evaluation(client, history_id, dept_form_id, eval_type_id):
    fields = {'startDate': '2022-04-27'}
    if dept_form_id:
        fields['departmentFormId'] = dept_form_id
    if eval_type_id:
        fields['evaluationTypeId'] = eval_type_id
    _api_update_evaluation(client, history_id, params={
        'evaluationIds': ['_2222_30643_326054'],
        'action': 'edit',
        'fields': fields,
    })


def _api_update_melc_evaluation(client, melc_id, dept_form_id, eval_type_id):
    fields = {'startDate': '2022-04-26'}
    if dept_form_id:
        fields['departmentFormId'] = dept_form_id
    if eval_type_id:
        fields['evaluationTypeId'] = eval_type_id
    _api_update_evaluation(client, melc_id, params={
        'evaluationIds': ['_2222_30643_326054'],
        'action': 'edit',
        'fields': fields,
    })


class TestEditEvaluationMultipleDepartments:

    def test_confirmed_status_shared_between_depts(self, client, fake_auth, melc_id, history_id):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, melc_id, params={'evaluationIds': ['_2222_30643_326054'], 'action': 'confirm'})
        assert _api_get_evaluation(client, melc_id, '30643', '326054')['status'] == 'confirmed'
        assert _api_get_evaluation(client, history_id, '30643', '326054')['status'] == 'confirmed'

    def test_ignore_status_not_shared_between_depts(self, client, fake_auth, melc_id, history_id):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, melc_id, params={'evaluationIds': ['_2222_30643_326054'], 'action': 'ignore'})
        assert _api_get_evaluation(client, melc_id, '30643', '326054')['status'] == 'ignore'
        assert _api_get_evaluation(client, history_id, '30643', '326054')['status'] is None

    def test_evaluation_edits_shared_between_depts(self, client, fake_auth, melc_id, history_id):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, melc_id, params={
            'evaluationIds': ['_2222_30643_326054'],
            'action': 'edit',
            'fields': {'departmentFormId': '13', 'evaluationTypeId': '3', 'startDate': '2022-04-27'},
        })
        melc_eval = _api_get_evaluation(client, melc_id, '30643', '326054')
        assert melc_eval['status'] is None
        assert melc_eval['departmentForm']['id'] == 13
        assert melc_eval['evaluationType']['id'] == 3
        assert melc_eval['lastUpdated'] is not None
        assert melc_eval['startDate'] == '2022-04-27'
        updated_melc = Evaluation.find_by_id(melc_eval['id'])
        assert updated_melc.created_at is not None
        assert updated_melc.updated_at is not None
        assert updated_melc.updated_by == non_admin_uid
        history_eval = _api_get_evaluation(client, history_id, '30643', '326054')
        assert history_eval['status'] is None
        assert history_eval['departmentForm']['id'] == 13
        assert history_eval['evaluationType']['id'] == 3
        assert history_eval['lastUpdated'] is not None
        assert history_eval['startDate'] == '2022-04-27'
        fake_auth.login(admin_uid)
        _api_update_evaluation(client, dept_id=history_id, params={'evaluationIds': ['_2222_30643_326054'], 'action': 'confirm'})
        history_eval_confirmed = _api_get_evaluation(client, history_id, '30643', '326054')
        assert history_eval_confirmed['status'] == 'confirmed'
        assert history_eval_confirmed['conflicts'] == {}
        assert history_eval_confirmed['departmentForm']['id'] == 13
        assert history_eval_confirmed['evaluationType']['id'] == 3
        assert history_eval_confirmed['startDate'] == '2022-04-27'
        assert history_eval_confirmed['lastUpdated'] is not None
        history_eval_row = Evaluation.find_by_id(history_eval_confirmed['id'])
        assert history_eval_row.created_at is not None
        assert history_eval_row.department_form is not None
        assert history_eval_row.department_form.id == 13
        assert history_eval_row.evaluation_type is not None
        assert history_eval_row.evaluation_type.id == 3
        assert history_eval_row.start_date is not None
        assert history_eval_row.updated_at is not None
        assert history_eval_row.updated_by == admin_uid
        melc_eval_confirmed = _api_get_evaluation(client, melc_id, '30643', '326054')
        assert melc_eval_confirmed['status'] == 'confirmed'
        assert melc_eval_confirmed['conflicts'] == {}
        assert melc_eval_confirmed['departmentForm']['id'] == 13
        assert melc_eval_confirmed['evaluationType']['id'] == 3
        assert melc_eval_confirmed['startDate'] is not None
        assert melc_eval_confirmed['lastUpdated'] is not None
        melc_eval_row = Evaluation.find_by_id(history_eval_confirmed['id'])
        assert melc_eval_row.created_at is not None
        assert melc_eval_row.department_form is not None
        assert melc_eval_row.department_form.id == 13
        assert melc_eval_row.evaluation_type is not None
        assert melc_eval_row.evaluation_type.id == 3
        assert melc_eval_row.start_date is not None
        assert melc_eval_row.updated_at is not None
        assert melc_eval_row.updated_by == admin_uid

    def test_evaluation_edits_show_conflicts(
        self,
        client,
        fake_auth,
        melc_id,
        history_id,
        form_melc_id,
        form_history_id,
        type_f_id,
        type_g_id,
    ):
        fake_auth.login(non_admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_g_id)
        _api_update_melc_evaluation(client, melc_id, form_melc_id, type_f_id)
        melc_eval = _api_get_evaluation(client, melc_id, '30643', '326054')
        history_eval = _api_get_evaluation(client, history_id, '30643', '326054')

        assert melc_eval['status'] is None
        assert history_eval['status'] is None
        assert melc_eval['conflicts']['departmentForm'] == [{'department': 'History', 'value': 'HISTORY'}]
        assert melc_eval['conflicts']['evaluationType'] == [{'department': 'History', 'value': 'G'}]
        assert melc_eval['conflicts']['evaluationPeriod'] == [{'department': 'History', 'value': '2022-04-27'}]
        assert history_eval['conflicts']['departmentForm'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': 'MELC'}]
        assert history_eval['conflicts']['evaluationType'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': 'F'}]
        assert history_eval['conflicts']['evaluationPeriod'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': '2022-04-26'}]


def _api_add_section(client, dept_id=None, params={}, expected_status_code=200):
    if dept_id is None:
        dept = Department.find_by_name('Middle Eastern Languages and Cultures')
        dept_id = dept.id
    response = client.post(
        f'/api/department/{dept_id}/section',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestAddSection:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_add_section(client, expected_status_code=401)

    def test_unknown_dept(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_add_section(client, dept_id=0, expected_status_code=404)

    def test_no_course_number(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_add_section(client, params={'not': 'me'}, expected_status_code=400)

    def test_bad_course_number(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_add_section(client, params={'courseNumber': '8675309'}, expected_status_code=400)

    def test_add_screened_out_course(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 44
        for e in department['evaluations']:
            assert e['instructionFormat'] != 'IND'

        _api_add_section(client, params={'courseNumber': '32940'})
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 45
        new_section = next(e for e in department['evaluations'] if e['courseNumber'] == '32940')
        assert new_section['courseTitle'] == 'Special Studies: Cuneiform'
        assert new_section['instructionFormat'] == 'IND'
        assert new_section['lastUpdated'] is not None

    def test_add_foreign_course(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 44
        for e in department['evaluations']:
            assert e['subjectArea'] != 'LGBT'

        _api_add_section(client, params={'courseNumber': '30481'})
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 45
        new_section = next(e for e in department['evaluations'] if e['courseNumber'] == '30481')
        assert new_section['courseTitle'] == 'Alternative Sexual Identities and Communities in Contemporary American Society'
        assert new_section['subjectArea'] == 'LGBT'
        assert new_section['lastUpdated'] is not None


def _api_update_department_note(client, dept=None, params={}, expected_status_code=200):
    if not dept:
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
        """Non-admin user cannot update another department's note."""
        fake_auth.login(non_admin_uid)
        department = Department.find_by_name('History')
        _api_update_department_note(client, department, expected_status_code=401)

    def test_department_member(self, client, fake_auth):
        """Non-admin user can update their own department's note."""
        fake_auth.login(non_admin_uid)
        department = Department.find_by_name('Philosophy')
        assert department.notes == []

        note = """Look, he's a perfectly healthy boy. I mean, we have nothing to worry about with him.
            Not physically or... or otherwise. He just... had a bad moment. You know, like a fright."""
        department_note = _api_update_department_note(client, department, {'note': note})
        assert department_note['note'] == note

        department_note = _api_update_department_note(client, department)
        assert department_note['note'] is None

    def test_admin(self, client, fake_auth):
        """Admin user can update the note."""
        fake_auth.login(admin_uid)
        department = Department.find_by_name('Philosophy')
        assert department.notes == []

        note = """It is the greatest mystery of all because no human being will ever solve it.
            It is the highest suspense because no man can bear it.
            It is the greatest fear because it is the ancient fear of the unknown.
            It is a warning foretold for thousands of years. It is our final warning.
            It is The Omen."""
        department_note = _api_update_department_note(client, department, {'note': note})
        assert department_note['note'] == note

        department_note = _api_update_department_note(client, department)
        assert department_note['note'] is None

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
        assert department['notes'] == {}
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
        assert department['notes'] == {}

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
        assert len(department['evaluations']) == 42
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

    def test_include_cross_listing(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        cross_listings = [e for e in department['evaluations'] if e['subjectArea'] == 'HISTORY' and e['catalogId'] == 'C188C']
        assert len(cross_listings) == 2
        for cl in cross_listings:
            assert cl['courseNumber'] == '30643'
            assert cl['crossListedWith'] == '30470'
            assert cl['departmentForm'] is None
        home_dept_rows = [e for e in department['evaluations'] if e['courseNumber'] == '30470']
        for hdr in home_dept_rows:
            assert hdr['crossListedWith'] == '30643'
            assert hdr['departmentForm'] is None

    def test_include_room_share(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        room_share = next(e for e in department['evaluations'] if e['subjectArea'] == 'JEWISH' and e['catalogId'] == '120A')
        assert room_share['courseNumber'] == '32159'
        assert room_share['roomSharedWith'] == '30462'
        assert room_share['departmentForm'] is None
        home_dept_row = next(e for e in department['evaluations'] if e['courseNumber'] == '30462')
        assert home_dept_row['roomSharedWith'] == '32159'
        assert home_dept_row['departmentForm'] is None


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

    def test_mark_unmark(self, client, fake_auth):
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
        evaluation_id = response[0]['id']
        response = _api_update_evaluation(client, params={'evaluationIds': [evaluation_id], 'action': 'unmark'})
        assert response[0]['courseNumber'] == '30659'
        assert response[0]['id'] == evaluation_id
        assert response[0]['status'] is None


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
                'fields': {'midterm': 'true', 'endDate': '2022-03-01'},
            },
        )
        assert len(response) == 2

        midterm_eval = next(r for r in response if r['endDate'] == '2022-03-01')
        assert midterm_eval['courseNumber'] == '30659'
        assert midterm_eval['courseTitle'] == 'Elementary Sumerian'
        assert midterm_eval['instructor']['uid'] == '637739'
        assert midterm_eval['departmentForm']['name'] == 'CUNEIF_MID'

        final_eval = next(r for r in response if r['endDate'] == '2022-05-06')
        assert final_eval['courseNumber'] == '30659'
        assert final_eval['courseTitle'] == 'Elementary Sumerian'
        assert final_eval['instructor']['uid'] == '637739'
        assert final_eval['departmentForm']['name'] == 'CUNEIF'


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

    def test_bad_date(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'endDate': 'ill communication'},
        }, expected_status_code=400)

    def test_date_before_term(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'endDate': '2021-12-25'},
        }, expected_status_code=400)

    def test_date_after_term(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'fields': {'endDate': '2022-07-14'},
        }, expected_status_code=400)

    def test_edit_dates(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        response = _api_update_evaluation(client, params={
            'evaluationIds': ['_2222_30659_637739'],
            'action': 'edit',
            'fields': {'endDate': '2022-05-01'},
        })
        assert len(response) == 1
        assert response[0]['id'] == int(response[0]['id'])
        assert response[0]['transientId'] == '_2222_30659_637739'
        assert response[0]['startDate'] == '2022-01-18'
        assert response[0]['endDate'] == '2022-05-01'


def _api_get_evaluation(client, dept_id, course_number, instructor_uid):
    response = client.get(f'/api/department/{dept_id}')
    return next((e for e in response.json['evaluations'] if e['courseNumber'] == course_number and e['instructor']['uid'] == instructor_uid), None)


def _api_update_history_evaluation(client, history_id, dept_form_id, eval_type_id):
    fields = {'endDate': '2022-05-02'}
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
    fields = {'endDate': '2022-05-01'}
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

    def test_evaluation_edits_shared_between_depts_after_marked(self, client, fake_auth, melc_id, history_id):
        fake_auth.login(non_admin_uid)
        _api_update_evaluation(client, melc_id, params={
            'evaluationIds': ['_2222_30643_326054'],
            'action': 'edit',
            'fields': {'departmentFormId': '13', 'evaluationTypeId': '3', 'endDate': '2022-05-01'},
        })
        melc_eval = _api_get_evaluation(client, melc_id, '30643', '326054')
        assert melc_eval['status'] is None
        assert melc_eval['departmentForm']['id'] == 13
        assert melc_eval['evaluationType']['id'] == 3
        assert melc_eval['endDate'] == '2022-05-01'
        history_eval = _api_get_evaluation(client, history_id, '30643', '326054')
        assert history_eval['status'] is None
        assert history_eval['departmentForm'] is None
        assert history_eval['evaluationType']['id'] != 3
        assert history_eval['endDate'] != '2022-05-01'
        _api_update_evaluation(client, melc_id, params={'evaluationIds': [melc_eval['id']], 'action': 'mark'})
        history_eval = _api_get_evaluation(client, history_id, '30643', '326054')
        assert history_eval['status'] == 'review'
        assert history_eval['departmentForm']['id'] == 13
        assert history_eval['evaluationType']['id'] == 3
        assert history_eval['endDate'] == '2022-05-01'

    def test_evaluation_edits_show_conflicts_if_conflicting_eval_marked(
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
        assert not melc_eval['conflicts']
        assert not history_eval['conflicts']

        _api_update_evaluation(client, melc_id, params={'evaluationIds': [melc_eval['id']], 'action': 'mark'})
        melc_eval = _api_get_evaluation(client, melc_id, '30643', '326054')
        history_eval = _api_get_evaluation(client, history_id, '30643', '326054')
        assert melc_eval['status'] == 'review'
        assert history_eval['status'] == 'review'
        assert melc_eval['conflicts']['departmentForm'] == [{'department': 'History', 'value': 'HISTORY'}]
        assert melc_eval['conflicts']['evaluationType'] == [{'department': 'History', 'value': 'G'}]
        assert melc_eval['conflicts']['evaluationPeriod'] == [{'department': 'History', 'value': '2022-04-12'}]
        assert history_eval['conflicts']['departmentForm'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': 'MELC'}]
        assert history_eval['conflicts']['evaluationType'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': 'F'}]
        assert history_eval['conflicts']['evaluationPeriod'] == [{'department': 'Middle Eastern Languages and Cultures', 'value': '2022-04-11'}]


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
        assert len(department['evaluations']) == 42
        for e in department['evaluations']:
            assert e['instructionFormat'] != 'IND'

        _api_add_section(client, params={'courseNumber': '32940'})
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 43
        new_section = next(e for e in department['evaluations'] if e['courseNumber'] == '32940')
        assert new_section['instructionFormat'] == 'IND'
        assert new_section['courseTitle'] == 'Special Studies: Cuneiform'

    def test_add_foreign_course(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 42
        for e in department['evaluations']:
            assert e['subjectArea'] != 'LGBT'

        _api_add_section(client, params={'courseNumber': '30481'})
        department = _api_get_melc(client)
        assert len(department['evaluations']) == 43
        new_section = next(e for e in department['evaluations'] if e['courseNumber'] == '30481')
        assert new_section['subjectArea'] == 'LGBT'
        assert new_section['courseTitle'] == 'Alternative Sexual Identities and Communities in Contemporary American Society'

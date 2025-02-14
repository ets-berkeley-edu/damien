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

import re

from damien import std_commit
from damien.models.export import Export
from moto import mock_s3
from tests.api.test_department_controller import \
    _api_get_evaluation, _api_update_evaluation, _api_update_history_evaluation, _api_update_melc_evaluation
from tests.util import mock_s3_bucket


non_admin_uid = '100'
admin_uid = '200'


def _api_get_export_status(client, expected_status_code=200):
    response = client.get('/api/evaluations/export/status')
    assert response.status_code == expected_status_code
    return response.json


class TestGetExportStatus:

    def test_anonymous(self, client):
        _api_get_export_status(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_get_export_status(client, expected_status_code=401)

    def test_nonexistent_export(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = _api_get_export_status(client)
        assert response == {}

    def test_export_in_progress(self, client, fake_auth):
        Export.create('2222', 'exports/2222/2022_04_29_17_33_44')
        std_commit(allow_test_environment=True)

        fake_auth.login(admin_uid)
        response = _api_get_export_status(client)
        assert response['s3Path'] == 'exports/2222/2022_04_29_17_33_44'
        assert response['status'] == 'started'
        assert response['termId'] == '2222'

    def test_export_complete(self, client, fake_auth):
        export = Export.create('2218', 'exports/2218/2021_12_21_03_03_03')
        export.update_status('exports/2218/2021_12_21_03_03_03', 'success')
        std_commit(allow_test_environment=True)

        fake_auth.login(admin_uid)
        response = _api_get_export_status(client)
        assert response['s3Path'] == 'exports/2218/2021_12_21_03_03_03'
        assert response['status'] == 'success'
        assert response['termId'] == '2218'


def _api_get_validations(client, expected_status_code=200):
    response = client.get('/api/evaluations/validate')
    assert response.status_code == expected_status_code
    return response.json


class TestGetValidations:

    def test_anonymous(self, client):
        _api_get_validations(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_get_validations(client, expected_status_code=401)

    def test_empty_feed(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = _api_get_validations(client)
        assert response == []

    def test_forms_not_marked(
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
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_f_id)
        _api_update_melc_evaluation(client, melc_id, form_melc_id, type_g_id)
        response = _api_get_validations(client)
        assert response == []

    def test_no_conflicts(self, client, fake_auth, history_id, form_history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_f_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        response = _api_get_validations(client)
        assert response == []

    def test_missing_data(self, client, fake_auth, history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, None, None, type_f_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        response = _api_get_validations(client)
        assert len(response) == 2
        for r in response:
            assert r['courseNumber'] == '30643'
            assert r['instructor']['uid'] == '326054'
            assert r['departmentForm'] is None
            assert r['valid'] is False

    def test_validation_conflicts(
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
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_f_id)
        _api_update_melc_evaluation(client, melc_id, form_melc_id, type_g_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'review'})
        client.get(f'/api/department/{melc_id}')
        response = _api_get_validations(client)
        assert len(response) == 2
        for r in response:
            assert r['courseNumber'] == '30643'
            assert r['instructor']['uid'] == '326054'
            assert r['conflicts']['departmentForm']
            assert r['conflicts']['evaluationType']
            assert r['valid'] is False


def _api_get_confirmed(client, expected_status_code=200):
    response = client.get('/api/evaluations/confirmed')
    assert response.status_code == expected_status_code
    return response.json


class TestGetConfirmed:

    def test_anonymous(self, client):
        _api_get_confirmed(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_get_confirmed(client, expected_status_code=401)

    def test_confirmed_course(self, client, app, fake_auth):
        fake_auth.login(admin_uid)
        response = _api_get_confirmed(client)
        assert len(response) == 1
        assert response[0]['deptName'] == 'History'
        assert response[0]['count'] == 2


def _api_export_evaluations(client, expected_status_code=200):
    response = client.post('/api/evaluations/export')
    assert response.status_code == expected_status_code
    return response.json


def _api_get_exports(client, expected_status_code=200):
    response = client.get('/api/evaluations/exports')
    assert response.status_code == expected_status_code
    return response.json


def _read_csv(objects, key):
    obj = next(o for o in objects if o.key.endswith(key))
    object_data = obj.get()['Body'].read()
    rows = object_data.decode('utf-8').split('\r\n')
    if rows[-1] == '':
        rows.pop()
    return rows


class TestExportEvaluations:

    def test_anonymous(self, client):
        _api_export_evaluations(client, expected_status_code=401)
        _api_get_exports(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_export_evaluations(client, expected_status_code=401)
        _api_get_exports(client, expected_status_code=401)

    def test_validation_errors(self, client, fake_auth, history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, None, None, type_f_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        _api_export_evaluations(client, expected_status_code=400)
        assert _api_get_exports(client) == []

    @mock_s3
    def test_nothing_confirmed_headers_only(self, client, app, fake_auth):
        fake_auth.login(admin_uid)
        assert _api_get_exports(client) == []

        with mock_s3_bucket(app) as s3:
            eval_response = _api_export_evaluations(client)
            assert eval_response['termId'] == '2222'
            assert re.match('^exports/2222/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}$', eval_response['s3Path'])
            assert eval_response['createdAt']

            exported_objects = [o for o in s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all() if o.key.startswith('exports/2222')]
            assert len(exported_objects) == 10

            courses = _read_csv(exported_objects, '/courses.csv')
            assert len(courses) == 1
            assert courses[0] == ('COURSE_ID,COURSE_ID_2,COURSE_NAME,CROSS_LISTED_FLAG,CROSS_LISTED_NAME,DEPT_NAME,CATALOG_ID,INSTRUCTION_FORMAT,'
                                  'SECTION_NUM,PRIMARY_SECONDARY_CD,EVALUATE,DEPT_FORM,EVALUATION_TYPE,MODULAR_COURSE,START_DATE,END_DATE,'
                                  'CANVAS_COURSE_ID,QB_MAPPING')

            course_instructors = _read_csv(exported_objects, '/course_instructors.csv')
            assert len(course_instructors) == 3
            assert course_instructors[0] == 'COURSE_ID,LDAP_UID,ROLE'
            assert course_instructors[1] == '2021-D-12345,666,Faculty'
            assert course_instructors[2] == '2021-D-12345,8675309,GSI'

            course_students = _read_csv(exported_objects, '/course_students.csv')
            assert len(course_students) == 1
            assert course_students[0] == 'COURSE_ID,LDAP_UID'

            course_supervisors = _read_csv(exported_objects, '/course_supervisors.csv')
            assert len(course_supervisors) == 1
            assert course_supervisors[0] == 'COURSE_ID,LDAP_UID,DEPT_NAME'

            instructors = _read_csv(exported_objects, '/instructors.csv')
            assert len(instructors) == 1
            assert instructors[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS,BLUE_ROLE'

            students = _read_csv(exported_objects, '/students.csv')
            assert len(students) == 1
            assert students[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS'

            export_response = _api_get_exports(client)
            assert len(export_response) == 1
            assert export_response[0] == eval_response

    @mock_s3
    def test_confirmed_course(self, client, app, fake_auth, history_id, form_history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_f_id)
        std_commit(allow_test_environment=True)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        std_commit(allow_test_environment=True)

        with mock_s3_bucket(app) as s3:
            _api_export_evaluations(client)
            exported_objects = [o for o in s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all() if o.key.startswith('exports/2222')]
            assert len(exported_objects) == 10

            courses = _read_csv(exported_objects, '/courses.csv')
            assert len(courses) == 2
            assert courses[0] == ('COURSE_ID,COURSE_ID_2,COURSE_NAME,CROSS_LISTED_FLAG,CROSS_LISTED_NAME,DEPT_NAME,CATALOG_ID,INSTRUCTION_FORMAT,'
                                  'SECTION_NUM,PRIMARY_SECONDARY_CD,EVALUATE,DEPT_FORM,EVALUATION_TYPE,MODULAR_COURSE,START_DATE,END_DATE,'
                                  'CANVAS_COURSE_ID,QB_MAPPING')
            assert courses[1] == ('2022-B-30643,2022-B-30643,"HISTORY C188C LEC 001 Magic, Religion, and Science: The Ancient and Medieval Worlds",'
                                  'Y,30470-30643,HISTORY,C188C,LEC,001,P,Y,HISTORY,F,,4/27/22,5/17/22,,HISTORY-F')

            course_instructors = _read_csv(exported_objects, '/course_instructors.csv')
            assert len(course_instructors) == 4
            assert course_instructors[0] == 'COURSE_ID,LDAP_UID,ROLE'
            assert course_instructors[1] == '2021-D-12345,666,Faculty'
            assert course_instructors[2] == '2021-D-12345,8675309,GSI'
            assert course_instructors[3] == '2022-B-30643,326054,Faculty'

            instructors = _read_csv(exported_objects, '/instructors.csv')
            assert len(instructors) == 2
            assert instructors[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS,BLUE_ROLE'
            assert instructors[1] == '326054,4159446,Donald,Smeet,ietkoqrg@berkeley.edu,23'

            course_students = _read_csv(exported_objects, '/course_students.csv')
            assert len(course_students) == 4
            assert course_students[0] == 'COURSE_ID,LDAP_UID'
            assert course_students[1] == '2022-B-30643,77777'
            assert course_students[2] == '2022-B-30643,88888'
            assert course_students[3] == '2022-B-30643,99999'

            course_supervisors = _read_csv(exported_objects, '/course_supervisors.csv')
            assert len(course_supervisors) == 3
            assert course_supervisors[0] == 'COURSE_ID,LDAP_UID,DEPT_NAME'
            assert course_supervisors[1] == '2022-B-30643,5013530,HISTORY'
            assert course_supervisors[2] == '2022-B-30643,6982398,HISTORY'

            students = _read_csv(exported_objects, '/students.csv')
            assert len(students) == 4
            assert students[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS'
            assert students[1] == '77777,12377777,Sutherland,Northen,snorthen@berkeley.edu'
            assert students[2] == '88888,12388888,Archy,Goforth,agoforth1@berkeley.edu'
            assert students[3] == '99999,12399999,Georgi,Prudence,gprudence2@berkeley.edu'

            xlisted_course_supervisors = _read_csv(exported_objects, '/xlisted_course_supervisors.csv')
            assert len(xlisted_course_supervisors) == 4
            assert xlisted_course_supervisors[0] == 'COURSE_ID,LDAP_UID'
            # Dept admins for cross-listed MELC department.
            assert xlisted_course_supervisors[1] == '2022-B-30643,1007025'
            # Dept admins for home history department.
            assert xlisted_course_supervisors[2] == '2022-B-30643,5013530'
            assert xlisted_course_supervisors[3] == '2022-B-30643,6982398'

    @mock_s3
    def test_confirmed_course_gsi(self, client, app, fake_auth, history_id, form_history_id, type_g_id):
        fake_auth.login(admin_uid)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={
            'evaluationIds': [evaluation['id']],
            'action': 'edit',
            'fields': {'departmentFormId': form_history_id, 'evaluationTypeId': type_g_id, 'startDate': '2022-04-27'},
        })
        std_commit(allow_test_environment=True)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        std_commit(allow_test_environment=True)

        with mock_s3_bucket(app) as s3:
            _api_export_evaluations(client)
            exported_objects = [o for o in s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all() if o.key.startswith('exports/2222')]
            assert len(exported_objects) == 10

            courses = _read_csv(exported_objects, '/courses.csv')
            assert len(courses) == 2
            assert courses[0] == ('COURSE_ID,COURSE_ID_2,COURSE_NAME,CROSS_LISTED_FLAG,CROSS_LISTED_NAME,DEPT_NAME,CATALOG_ID,INSTRUCTION_FORMAT,'
                                  'SECTION_NUM,PRIMARY_SECONDARY_CD,EVALUATE,DEPT_FORM,EVALUATION_TYPE,MODULAR_COURSE,START_DATE,END_DATE,'
                                  'CANVAS_COURSE_ID,QB_MAPPING')
            assert courses[1] == ('2022-B-30643_GSI,2022-B-30643_GSI,"HISTORY C188C LEC 001 Magic, Religion, and Science: The Ancient and '
                                  'Medieval Worlds (EVAL FOR GSI)",Y,30470-30643,HISTORY,C188C,LEC,001,P,Y,HISTORY,G,,4/27/22,5/17/22,,HISTORY-G')

            course_instructors = _read_csv(exported_objects, '/course_instructors.csv')
            assert course_instructors[3] == '2022-B-30643_GSI,326054,GSI'

            course_students = _read_csv(exported_objects, '/course_students.csv')
            for row in course_students[1:]:
                assert row.startswith('2022-B-30643_GSI')

            course_supervisors = _read_csv(exported_objects, '/course_supervisors.csv')
            for row in course_supervisors[1:]:
                assert row.startswith('2022-B-30643_GSI')

            xlisted_course_supervisors = _read_csv(exported_objects, '/xlisted_course_supervisors.csv')
            for row in xlisted_course_supervisors[1:]:
                assert row.startswith('2022-B-30643_GSI')

    @mock_s3
    def test_supervisors_export(self, client, app, fake_auth, history_id, form_history_id, type_f_id):
        fake_auth.login(admin_uid)

        with mock_s3_bucket(app) as s3:
            _api_export_evaluations(client)
            exported_objects = list(s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all())

            supervisors = _read_csv(exported_objects, '/supervisors.csv')
            assert len(supervisors) == 4
            assert supervisors[0] == ('LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS,SUPERVISOR_GROUP,PRIMARY_ADMIN,SECONDARY_ADMIN')
            assert supervisors[1] == '5013530,931203945,Jazz,Gunn,jazz.gunn@berkeley.edu,DEPT_ADMIN,Y,'
            assert (supervisors[2]
                    == '6982398,263809005,Alistair,Mctaggert,alistair.mctaggert@berkeley.edu,DEPT_ADMIN,,')
            assert supervisors[3] == '8971283,294078726,Finn,Wolfhard,finn.wolfhard@berkeley.edu,DEPT_ADMIN,,'

            xlisted_course_supervisors = _read_csv(exported_objects, '/xlisted_course_supervisors.csv')
            assert len(xlisted_course_supervisors) == 4
            assert xlisted_course_supervisors[0] == 'COURSE_ID,LDAP_UID'
            # Dept admins for cross-listed MELC department.
            assert xlisted_course_supervisors[1] == '2022-B-30643_GSI,1007025'
            # Dept admins for home history department.
            assert xlisted_course_supervisors[2] == '2022-B-30643_GSI,5013530'
            assert xlisted_course_supervisors[3] == '2022-B-30643_GSI,6982398'

            department_hierarchy = _read_csv(exported_objects, '/department_hierarchy.csv')
            assert len(department_hierarchy) > 100
            assert department_hierarchy[0] == 'NODE_ID,NODE_CAPTION,PARENT_NODE_ID,PARENT_NODE_CAPTION,LEVEL'
            assert department_hierarchy[1] == 'UC Berkeley,UC Berkeley,,,1'
            assert 'HISTORY,HISTORY,UC Berkeley,UC Berkeley,2' in department_hierarchy
            # Include deleted forms.
            assert 'ANCIENT_HISTORY,ANCIENT_HISTORY,UC Berkeley,UC Berkeley,2' in department_hierarchy

            report_viewer_hierarchy = _read_csv(exported_objects, '/report_viewer_hierarchy.csv')
            assert len(report_viewer_hierarchy) == 7
            assert report_viewer_hierarchy[0] == 'SOURCE,TARGET,ROLE_ID'
            assert 'PHILOS,100,DEPT_ADMIN' in report_viewer_hierarchy
            assert 'HISTORY,5013530,DEPT_ADMIN' in report_viewer_hierarchy
            assert 'HISTORY,6982398,DEPT_ADMIN' in report_viewer_hierarchy
            assert 'MELC,1007025,DEPT_ADMIN' in report_viewer_hierarchy
            assert 'ANCIENT_HISTORY,5013530,DEPT_ADMIN' in report_viewer_hierarchy
            assert 'ANCIENT_HISTORY,6982398,DEPT_ADMIN' in report_viewer_hierarchy

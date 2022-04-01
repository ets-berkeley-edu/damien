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

from moto import mock_s3
from tests.api.test_department_controller import \
    _api_get_evaluation, _api_update_evaluation, _api_update_history_evaluation, _api_update_melc_evaluation
from tests.util import mock_s3_bucket


non_admin_uid = '100'
admin_uid = '200'


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
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        client.get(f'/api/department/{melc_id}')
        response = _api_get_validations(client)
        assert len(response) == 2
        for r in response:
            assert r['courseNumber'] == '30643'
            assert r['instructor']['uid'] == '326054'
            assert r['conflicts']['departmentForm']
            assert r['conflicts']['evaluationType']
            assert r['valid'] is False


def _api_export_evaluations(client, expected_status_code=200):
    response = client.get('/api/evaluations/export')
    assert response.status_code == expected_status_code


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

    def test_unauthorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        _api_export_evaluations(client, expected_status_code=401)

    def test_validation_errors(self, client, fake_auth, history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, None, None, type_f_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        _api_export_evaluations(client, expected_status_code=400)

    @mock_s3
    def test_nothing_confirmed_headers_only(self, client, app, fake_auth):
        fake_auth.login(admin_uid)
        with mock_s3_bucket(app) as s3:
            _api_export_evaluations(client)
            exported_objects = list(s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all())
            assert len(exported_objects) == 3

            courses = _read_csv(exported_objects, '/courses.csv')
            assert len(courses) == 1
            assert courses[0] == ('COURSE_ID,COURSE_ID_2,COURSE_NAME,CROSS_LISTED_FLAG,CROSS_LISTED_NAME,DEPT_NAME,CATALOG_ID,INSTRUCTION_FORMAT,'
                                  'SECTION_NUM,PRIMARY_SECONDARY_CD,EVALUATE,DEPT_FORM,EVALUATION_TYPE,MODULAR_COURSE,START_DATE,END_DATE,'
                                  'CANVAS_COURSE_ID,QB_MAPPING')

            course_instructors = _read_csv(exported_objects, '/course_instructors.csv')
            assert len(course_instructors) == 1
            assert course_instructors[0] == 'COURSE_ID,LDAP_UID'

            instructors = _read_csv(exported_objects, '/instructors.csv')
            assert len(instructors) == 1
            assert instructors[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS,BLUE_ROLE'

    @mock_s3
    def test_confirmed_course(self, client, app, fake_auth, history_id, form_history_id, type_f_id):
        fake_auth.login(admin_uid)
        _api_update_history_evaluation(client, history_id, form_history_id, type_f_id)
        evaluation = _api_get_evaluation(client, history_id, '30643', '326054')
        _api_update_evaluation(client, history_id, params={'evaluationIds': [evaluation['id']], 'action': 'confirm'})
        with mock_s3_bucket(app) as s3:
            _api_export_evaluations(client)
            exported_objects = list(s3.Bucket(app.config['AWS_S3_BUCKET']).objects.all())
            assert len(exported_objects) == 3

            courses = _read_csv(exported_objects, '/courses.csv')
            assert len(courses) == 2
            assert courses[0] == ('COURSE_ID,COURSE_ID_2,COURSE_NAME,CROSS_LISTED_FLAG,CROSS_LISTED_NAME,DEPT_NAME,CATALOG_ID,INSTRUCTION_FORMAT,'
                                  'SECTION_NUM,PRIMARY_SECONDARY_CD,EVALUATE,DEPT_FORM,EVALUATION_TYPE,MODULAR_COURSE,START_DATE,END_DATE,'
                                  'CANVAS_COURSE_ID,QB_MAPPING')
            assert courses[1] == ('2022-B-30643,2022-B-30643,"Magic, Religion, and Science: The Ancient and Medieval Worlds",Y,30470-30643,HISTORY,'
                                  'C188C,LEC,001,P,Y,HISTORY,F,,01-18-2022,05-02-2022,,HISTORY-F')

            course_instructors = _read_csv(exported_objects, '/course_instructors.csv')
            assert len(course_instructors) == 2
            assert course_instructors[0] == 'COURSE_ID,LDAP_UID'
            assert course_instructors[1] == '2022-B-30643,326054'

            instructors = _read_csv(exported_objects, '/instructors.csv')
            assert len(instructors) == 2
            assert instructors[0] == 'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS,BLUE_ROLE'
            assert instructors[1] == '326054,4159446,Kjsyobkui,Nxvlusjof,ietkoqrg@berkeley.edu,23'

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


from tests.api.test_department_controller import \
    _api_get_evaluation, _api_update_evaluation, _api_update_history_evaluation, _api_update_melc_evaluation

non_admin_uid = '100'
admin_uid = '200'


def _api_get_validations(client, expected_status_code=200):
    response = client.get('/api/validation')
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
        _api_update_evaluation(client, history_id, params={'evaluationIds': ['_2222_30643_326054'], 'action': 'confirm'})
        response = _api_get_validations(client)
        assert len(response) == 1

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

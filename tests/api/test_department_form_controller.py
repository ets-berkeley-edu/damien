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

from damien import std_commit
from damien.models.department_form import DepartmentForm

non_admin_uid = '100'
admin_uid = '200'


def _api_add_department_form(client, name='TEST', expected_status_code=200):
    response = client.post(f'/api/department_form/{name}')
    assert response.status_code == expected_status_code
    return response.json


class TestAddDepartmentForm:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_add_department_form(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_add_department_form(client, expected_status_code=401)

    def test_authorized_create(self, client, fake_auth):
        """Authorized user can create a new form."""
        fake_auth.login(admin_uid)
        form = _api_add_department_form(client, name='NEW')
        assert form['name'] == 'NEW'

    def test_authorized_restore(self, client, fake_auth):
        """Authorized user can restore a deleted form."""
        form = DepartmentForm.query.filter_by(deleted_at=None).first()
        DepartmentForm.delete(form.name)
        std_commit(allow_test_environment=True)

        fake_auth.login(admin_uid)
        response = _api_add_department_form(client, name=form.name)
        assert response['name'] == form.name

        std_commit(allow_test_environment=True)
        new_form = DepartmentForm.find_by_id(response['id'])
        assert new_form.deleted_at is None


def _api_delete_department_form(client, name='TEST', expected_status_code=200):
    response = client.delete(f'/api/department_form/{name}')
    assert response.status_code == expected_status_code
    return response.json


class TestDeleteDepartmentForm:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_delete_department_form(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_delete_department_form(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        DepartmentForm.create_or_restore(name='TEST')
        std_commit(allow_test_environment=True)

        fake_auth.login(admin_uid)
        response = _api_delete_department_form(client)
        assert response['message']

        std_commit(allow_test_environment=True)
        deleted_type = DepartmentForm.query.filter_by(name='TEST').first()
        assert deleted_type.deleted_at is not None

    def test_invalid_dept_id(self, client, fake_auth):
        """Fails silently when department form does not exist."""
        fake_auth.login(admin_uid)
        _api_delete_department_form(client, name='NOPE')


def _api_department_forms(client, expected_status_code=200):
    response = client.get('/api/department_forms')
    assert response.status_code == expected_status_code
    return response.json


class TestDepartmentForms:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_department_forms(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        forms = _api_department_forms(client)
        assert len(forms) == 197
        for f in forms:
            assert f['id']
            assert f['name']
            assert f['createdAt']
            assert f['updatedAt']
        assert next(f for f in forms if f['name'] == 'MUSIC')
        assert next(f for f in forms if f['name'] == 'HUNGARI')

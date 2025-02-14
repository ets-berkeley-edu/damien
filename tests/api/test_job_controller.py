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


non_admin_uid = '100'
admin_uid = '200'


def _api_refresh_loch(client, expected_status_code=200):
    response = client.get('/api/job/refresh_unholy_loch')
    assert response.status_code == expected_status_code
    return response.json


class TestJobRefresh:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_refresh_loch(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_refresh_loch(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        _api_refresh_loch(client)


def _api_job_status(client, expected_status_code=200):
    response = client.get('/api/job/status')
    assert response.status_code == expected_status_code
    return response.json


class TestJobStatus:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_job_status(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(non_admin_uid)
        _api_job_status(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = _api_job_status(client)
        assert response['status'] == 'done'

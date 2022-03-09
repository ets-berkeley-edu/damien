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


admin_uid = '200'
non_admin_uid = '100'


def _api_search_instructors(client, snippet='123', expected_status_code=200):
    response = client.post(
        '/api/instructor/search',
        data=json.dumps({'snippet': snippet}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestSearchInstructors:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_search_instructors(client, expected_status_code=401)

    def test_search_by_uid(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='713')
        assert len(results) == 1
        assert results[0]['uid'] == '713836'
        assert results[0]['csid'] == '6856470'
        assert results[0]['firstName'] == 'Mlskagctr'
        assert results[0]['lastName'] == 'Wondwzckm'
        assert results[0]['email'] == 'wdjmytek@berkeley.edu'

    def test_search_by_name(self, client, fake_auth):
        fake_auth.login(non_admin_uid)
        results = _api_search_instructors(client, snippet='Mlskagctr Wo')
        assert len(results) == 1
        assert results[0]['uid'] == '713836'
        assert results[0]['csid'] == '6856470'
        assert results[0]['firstName'] == 'Mlskagctr'
        assert results[0]['lastName'] == 'Wondwzckm'
        assert results[0]['email'] == 'wdjmytek@berkeley.edu'

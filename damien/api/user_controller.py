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

from damien.api.util import admin_required
from damien.lib.http import tolerant_jsonify
from damien.lib.queries import get_loch_basic_attributes_by_uid_or_name
from damien.lib.util import get as get_param
from damien.models.user import User
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/user/<uid>/forms')
@admin_required
def get_user_department_forms(uid):
    user = User.find_by_uid(uid)
    if user:
        results = [df.to_api_json() for df in user.department_forms]
        return tolerant_jsonify(results)
    return tolerant_jsonify([])


@app.route('/api/user/my_profile')
def my_profile():
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/user/search', methods=['POST'])
@admin_required
def search():
    params = request.get_json()
    snippet = get_param(params, 'snippet').strip()
    exclude_uids = get_param(params, 'excludeUids', [])
    users = User.search(snippet, exclude_uids)
    exclude_uids += [u['uid'] for u in users]
    calnet_results = []
    if len(users) < 20:
        calnet_results = get_loch_basic_attributes_by_uid_or_name(snippet, limit=(20 - len(users)), exclude_uids=exclude_uids)
    results = [_to_api_json(u) for u in users] + [_to_api_json(u) for u in calnet_results or []]
    results.sort(key=lambda x: f"{x['firstName'] or ''}{x['lastName'] or ''}")
    return tolerant_jsonify(results)


def _to_api_json(user):
    return {
        'csid': user['csid'],
        'email': user['email'],
        'firstName': user['first_name'],
        'lastName': user['last_name'],
        'uid': user['uid'],
    }

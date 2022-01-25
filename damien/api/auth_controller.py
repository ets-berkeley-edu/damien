"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from damien.api.errors import ResourceNotFoundError
from damien.lib.http import tolerant_jsonify
from damien.merged.user_session import UserSession
from damien.models.user import User
from flask import current_app as app, request
from flask_login import current_user, login_required, login_user, logout_user


@app.route('/api/auth/dev_auth_login', methods=['POST'])
def dev_auth_login():
    params = request.get_json() or {}
    if app.config['DEVELOPER_AUTH_ENABLED']:
        password = params.get('password')
        if password != app.config['DEVELOPER_AUTH_PASSWORD']:
            return tolerant_jsonify({'message': 'Invalid credentials'}, 401)
        uid = params.get('uid')
        return _login_user(uid)
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/logout')
@login_required
def logout():
    logout_user()
    redirect_url = app.config['VUE_LOCALHOST_BASE_URL'] or request.url_root
    return tolerant_jsonify({
        'logoutUrl': redirect_url,
        **current_user.to_api_json(),
    })


def _login_user(uid):
    user = User.find_by_uid(uid)
    user_id = user and user.id
    authenticated = login_user(UserSession(user_id)) and current_user.is_authenticated
    if authenticated:
        return tolerant_jsonify(current_user.to_api_json())
    else:
        return tolerant_jsonify({'message': f'User {user_id} failed to authenticate.'}, 403)

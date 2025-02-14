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

from damien.api.errors import BadRequestError
from damien.api.util import admin_required
from damien.lib.http import tolerant_jsonify
from damien.lib.queries import get_loch_basic_attributes_by_uid_or_name, get_loch_instructors_for_snippet
from damien.lib.util import get as get_param
from damien.models.supplemental_instructor import SupplementalInstructor
from flask import current_app as app, request
from flask_login import login_required


@app.route('/api/instructor', methods=['POST'])
@admin_required
def add_instructor():
    params = request.get_json() or {}

    try:
        valid_uid = (params.get('uid') and params['uid'] == str(int(params['uid'])))
    except ValueError:
        valid_uid = False
    if not valid_uid:
        raise BadRequestError('Bad or missing UID')

    try:
        valid_csid = (params.get('csid') is None or params['csid'] == str(int(params['csid'])))
    except ValueError:
        valid_csid = False
    if not valid_csid:
        raise BadRequestError('Bad CSID')

    if not params.get('lastName'):
        raise BadRequestError('Missing lastName')

    if not params.get('emailAddress') or not re.match(r'.+@.+\..+\Z', str(params['emailAddress'])):
        raise BadRequestError('Bad or missing email address')

    instructor = SupplementalInstructor.create_or_restore(
        ldap_uid=params['uid'],
        sis_id=params['csid'],
        first_name=params['firstName'],
        last_name=params['lastName'],
        email_address=params['emailAddress'],
    )
    return tolerant_jsonify(instructor.to_api_json())


@app.route('/api/instructor/<uid>', methods=['DELETE'])
@admin_required
def delete_instructor(uid):
    SupplementalInstructor.delete(uid)
    return tolerant_jsonify({'message': f'Instructor {uid} has been deleted'}), 200


@app.route('/api/instructors')
@admin_required
def get_supplemental_instructors():
    instructors = SupplementalInstructor.query.filter_by(deleted_at=None).order_by(SupplementalInstructor.ldap_uid).all()
    return tolerant_jsonify([_to_api_json(i) for i in instructors])


@app.route('/api/instructor/search', methods=['POST'])
@login_required
def search_instructors():
    params = request.get_json()
    snippet = get_param(params, 'snippet').strip()
    instructors = SupplementalInstructor.search(snippet)
    exclude_uids = [i.ldap_uid for i in instructors]
    if len(instructors) < 20:
        loch_instructors = get_loch_instructors_for_snippet(snippet, limit=(20 - len(instructors)), exclude_uids=exclude_uids)
        instructors.extend([{**i, 'isSisInstructor': True} for i in loch_instructors])
        exclude_uids.extend([str(i['uid']) for i in loch_instructors])
    if len(instructors) < 20:
        non_sis_instructors = get_loch_basic_attributes_by_uid_or_name(snippet, limit=(20 - len(instructors)), exclude_uids=exclude_uids)
        instructors.extend([{**i, 'isSisInstructor': False} for i in non_sis_instructors])
    results = [_to_api_json(i) for i in instructors]
    results.sort(key=lambda x: x['firstName'] or '')
    return tolerant_jsonify(results)


def _to_api_json(instructor):
    if isinstance(instructor, SupplementalInstructor):
        return {**instructor.to_api_json(), 'isSisInstructor': True}
    else:
        return {
            'csid': instructor['csid'],
            'email': instructor['email'],
            'firstName': instructor['first_name'],
            'lastName': instructor['last_name'],
            'uid': instructor['uid'],
            'isSisInstructor': instructor['isSisInstructor'],
        }

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

from damien.api.errors import BadRequestError, ResourceNotFoundError
from damien.api.util import admin_required
from damien.lib.berkeley import available_term_ids
from damien.lib.http import tolerant_jsonify
from damien.lib.util import get as get_param
from damien.models.department import Department
from damien.models.department_member import DepartmentMember
from damien.models.user import User
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/departments/enrolled')
@admin_required
def enrolled_departments():
    enrolled_depts = Department.all_enrolled()
    return tolerant_jsonify([d.to_api_json() for d in enrolled_depts])


@app.route('/api/department/<department_id>')
@login_required
def get_department(department_id):
    department = Department.find_by_id(int(department_id))
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    term_id = get_param(request.args, 'term_id', app.config['CURRENT_TERM_ID'])
    if term_id not in available_term_ids():
        raise BadRequestError('Invalid term id.')
    feed = department.to_api_json(
        include_contacts=current_user.is_admin,
        include_evaluations=True,
        term_id=term_id,
    )
    return tolerant_jsonify(feed)


@app.route('/api/department/<department_id>', methods=['POST'])
@admin_required
def update(department_id):
    department = Department.find_by_id(department_id)
    if department:
        params = request.get_json()
        note = get_param(params, 'note')
        department = Department.update(department_id, note=note)
        return tolerant_jsonify(department.to_api_json())
    else:
        raise ResourceNotFoundError(f'Department {department_id} not found.')


@app.route('/api/department/<department_id>/contact', methods=['POST'])
@admin_required
def update_contact(department_id):
    department = Department.find_by_id(department_id)
    if department:
        params = request.get_json()
        user_id = get_param(params, 'userId')
        if User.find_by_id(user_id):
            can_receive_communications = get_param(params, 'canReceiveCommunications')
            can_view_response_rates = get_param(params, 'canViewResponseRates')
            email = get_param(params, 'email')
            first_name = get_param(params, 'firstName')
            last_name = get_param(params, 'lastName')
            department_member = DepartmentMember.upsert(
                can_receive_communications=can_receive_communications,
                can_view_response_rates=can_view_response_rates,
                department_id=department_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_id=user_id,
            )
            return tolerant_jsonify(department_member.to_api_json())
        else:
            raise ResourceNotFoundError(f'User {user_id} not found.')
    else:
        raise ResourceNotFoundError(f'Department {department_id} not found.')

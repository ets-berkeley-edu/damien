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

from damien.api.errors import BadRequestError, ResourceNotFoundError
from damien.api.util import admin_required
from damien.externals.b_connected import BConnected
from damien.lib.http import tolerant_jsonify
from damien.lib.util import get as get_param
from damien.models.department import Department
from damien.models.department_member import DepartmentMember
from damien.models.user import User
from damien.models.user_department_form import UserDepartmentForm
from flask import current_app as app, request


@app.route('/api/department/<department_id>/contact/<user_id>', methods=['DELETE'])
@admin_required
def delete_contact(department_id, user_id):
    DepartmentMember.delete(department_id, user_id)
    return tolerant_jsonify({'message': f'Department contact <dept_id={department_id}, user_id={user_id}> has been deleted'}), 200


@app.route('/api/department/contacts/notify', methods=['POST'])
@admin_required
def notify_contacts():
    params = request.get_json()
    message = get_param(params, 'message')
    recipient = get_param(params, 'recipient')
    subject = get_param(params, 'subject')
    if not (message and recipient and subject):
        raise BadRequestError('Required parameters are missing.')
    result = {}
    for department in recipient:
        valid_recipient = []
        for user in department['recipients']:
            contact = DepartmentMember.find_by_department_and_user(department_id=user['departmentId'], user_id=user['id'])
            if contact.can_receive_communications:
                valid_recipient.append(user['email'])
        BConnected().send(
            recipient=valid_recipient,
            message=message,
            subject_line=subject,
        )
        result[department['deptName']] = valid_recipient
    return tolerant_jsonify({'message': f'Email sent to {result}'}), 200


@app.route('/api/department/<department_id>/contact', methods=['POST'])
@admin_required
def update_contact(department_id):
    if not Department.find_by_id(department_id):
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    params = request.get_json()
    can_receive_communications = get_param(params, 'canReceiveCommunications')
    can_view_reports = get_param(params, 'canViewReports')
    can_view_response_rates = get_param(params, 'canViewResponseRates')
    department_forms = get_param(params, 'departmentForms')
    email = get_param(params, 'email')
    uid = get_param(params, 'uid')
    user_id = get_param(params, 'userId')
    user = User.find_by_id(user_id) or User.find_by_uid(uid)
    csid = get_param(params, 'csid')
    first_name = get_param(params, 'firstName')
    last_name = get_param(params, 'lastName')
    user = User.create_or_restore(
        csid=csid,
        uid=uid,
        email=email,
        first_name=first_name,
        last_name=last_name,
        db_id=user_id,
    )
    blue_permissions = None
    if can_view_response_rates:
        blue_permissions = 'response_rates'
    elif can_view_reports:
        blue_permissions = 'reports_only'
    department_form_ids = [df['id'] for df in department_forms or []]
    UserDepartmentForm.update(department_form_ids=department_form_ids, user=user)
    department_member = DepartmentMember.upsert(
        blue_permissions=blue_permissions,
        can_receive_communications=can_receive_communications,
        department_id=department_id,
        email=email,
        user_id=user.id,
    )
    return tolerant_jsonify(department_member.to_api_json())

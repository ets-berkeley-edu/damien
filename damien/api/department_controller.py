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

from datetime import date
import re

from damien.api.errors import BadRequestError, ResourceNotFoundError
from damien.api.util import admin_required
from damien.lib.berkeley import available_term_ids, current_term_dates
from damien.lib.http import tolerant_jsonify
from damien.lib.util import get as get_param
from damien.models.department import Department
from damien.models.department_form import DepartmentForm
from damien.models.department_note import DepartmentNote
from damien.models.evaluation import Evaluation
from damien.models.evaluation_type import EvaluationType
from damien.models.supplemental_section import SupplementalSection
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/department/<department_id>/section', methods=['POST'])
@login_required
def add_section(department_id):
    department = Department.find_by_id(department_id)
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    params = request.get_json() or {}
    course_number = str(params.get('courseNumber'))
    if not course_number or not re.match(r'\d{5}\Z', course_number):
        raise BadRequestError('Missing or invalid course number.')
    current_term_id = app.config['CURRENT_TERM_ID']
    SupplementalSection.create_or_restore(current_term_id, course_number, department_id)
    response = department.evaluations_feed(current_term_id)
    return tolerant_jsonify(response)


@app.route('/api/departments/enrolled')
@admin_required
def enrolled_departments():
    enrolled_depts = Department.all_enrolled()
    include_contacts = bool(get_param(request.args, 'c', False))
    include_sections = bool(get_param(request.args, 's', False))
    return tolerant_jsonify([d.to_api_json(include_contacts=include_contacts, include_sections=include_sections) for d in enrolled_depts])


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
        include_notes=True,
        term_id=term_id,
    )
    return tolerant_jsonify(feed)


@app.route('/api/department/<department_id>/note', methods=['POST'])
@admin_required
def update_note(department_id):
    department = Department.find_by_id(int(department_id))
    if department:
        params = request.get_json()
        note = get_param(params, 'note')
        term_id = get_param(params, 'termId', app.config['CURRENT_TERM_ID'])
        if term_id not in available_term_ids():
            raise BadRequestError('Invalid term id.')
        department_note = DepartmentNote.upsert(department_id, term_id=term_id, note=note)
        return tolerant_jsonify(department_note.to_api_json())
    else:
        raise ResourceNotFoundError(f'Department {department_id} not found.')


@app.route('/api/department/<department_id>/evaluations', methods=['POST'])
@login_required
def update_evaluations(department_id):
    department = Department.find_by_id(department_id)
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    params = request.get_json() or {}
    action = params.get('action')
    evaluation_ids = params.get('evaluationIds')
    if not evaluation_ids:
        raise BadRequestError('No evaluation ids supplied.')
    updated_ids = []
    if action == 'confirm':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'confirmed'})
    elif action == 'delete':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'deleted'})
    elif action == 'duplicate':
        fields = None
        if params.get('fields'):
            fields = _validate_evaluation_fields(params.get('fields'))
        updated_ids = Evaluation.duplicate_bulk(department_id=department_id, evaluation_ids=evaluation_ids, department=department, fields=fields)
    elif action == 'edit':
        fields = _validate_evaluation_fields(params.get('fields'))
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields=fields)
    elif action == 'mark':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'marked'})
    elif action == 'ignore':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'ignore'})
    elif action == 'unmark':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': None})
    else:
        raise BadRequestError('Invalid update action.')
    if not updated_ids:
        raise BadRequestError('Evaluation ids could not be updated.')
    response = department.evaluations_feed(app.config['CURRENT_TERM_ID'], updated_ids)
    return tolerant_jsonify(response)


def _validate_evaluation_fields(fields):  # noqa C901
    validated_fields = {}
    if not fields or not type(fields) is dict:
        raise BadRequestError('No fields supplied for evaluation edit.')
    for k, v in fields.items():
        if k == 'departmentFormId':
            try:
                department_form = DepartmentForm.find_by_id(int(v))
            except ValueError:
                department_form = None
            if not department_form:
                raise BadRequestError(f'Invalid department form id {v}.')
            validated_fields['departmentForm'] = department_form
        elif k == 'evaluationTypeId':
            try:
                evaluation_type = EvaluationType.find_by_id(int(v))
            except ValueError:
                evaluation_type = None
            if not evaluation_type:
                raise BadRequestError(f'Invalid evaluation type id {v}.')
            validated_fields['evaluationType'] = evaluation_type
        elif k in {'startDate', 'endDate'}:
            try:
                validated_fields[k] = date.fromisoformat(v)
            except ValueError:
                raise BadRequestError(f'Invalid date format {v}.')
            _validate_current_term_date(validated_fields[k])
        elif k == 'instructorUid':
            try:
                validated_fields['instructorUid'] = str(int(v))
            except ValueError:
                raise BadRequestError(f'Invalid instructor UID {v}.')
        elif k == 'midterm':
            if v == 'true':
                validated_fields[k] = True
            elif v == 'false':
                validated_fields[k] = False
            else:
                raise BadRequestError(f'Invalid midterm value {v}')
        else:
            raise BadRequestError(f"Evaluation field '{k}' not recognized.")
    if 'startDate' in validated_fields and 'endDate' in validated_fields and validated_fields['startDate'] >= validated_fields['endDate']:
        raise BadRequestError('Start date must be before end date.')
    return validated_fields


def _validate_current_term_date(submitted_date):
    term_begin, term_end = current_term_dates()
    if submitted_date < term_begin or submitted_date > term_end:
        raise BadRequestError(f'Date {date} outside current term.')

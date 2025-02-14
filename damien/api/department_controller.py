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

from datetime import date
import re

from damien.api.errors import BadRequestError, ResourceNotFoundError
from damien.api.util import admin_required, department_membership_required, get_boolean_param, get_term_id
from damien.lib import cache
from damien.lib.berkeley import term_name_for_sis_id
from damien.lib.http import tolerant_jsonify
from damien.lib.queries import get_valid_meeting_dates
from damien.lib.util import get as get_param, safe_strftime
from damien.models.department import Department
from damien.models.department_form import DepartmentForm
from damien.models.department_note import DepartmentNote
from damien.models.evaluation import Evaluation
from damien.models.evaluation_term import EvaluationTerm
from damien.models.evaluation_type import EvaluationType
from damien.models.supplemental_section import SupplementalSection
from flask import current_app as app, request
from flask_login import login_required


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
    term_id = get_term_id(request)
    SupplementalSection.create_or_restore(term_id, course_number, department_id)
    response = department.evaluations_feed(term_id)
    return tolerant_jsonify(response)


@app.route('/api/departments/enrolled')
@admin_required
def enrolled_departments():
    include_contacts = get_boolean_param(request.args, 'c', False)
    enrolled_depts = Department.all_enrolled(load_contacts=include_contacts)
    term_id = get_term_id(request)
    cached = cache.fetch_all_departments(term_id)
    notes = DepartmentNote.find_by_term(term_id)
    include_sections = get_boolean_param(request.args, 's', False)
    include_status = get_boolean_param(request.args, 't', False)
    return tolerant_jsonify([d.to_api_json(
        term_id=term_id,
        include_contacts=include_contacts,
        include_sections=include_sections,
        include_status=include_status,
        departments_cache=cached,
        notes_cache=notes,
    ) for d in enrolled_depts if d.catalog_listings_map(term_id)])


@app.route('/api/department/<department_id>')
@login_required
def get_department(department_id):
    department = Department.find_by_id(int(department_id))
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    term_id = get_term_id(request)
    feed = department.to_api_json(
        term_id=term_id,
        include_contacts=True,
        include_evaluations=True,
    )
    feed['evaluationTerm'] = EvaluationTerm.find_or_create(term_id).to_api_json()
    return tolerant_jsonify(feed)


@app.route('/api/department/<department_id>/section_evaluations/<section_id>')
@login_required
def get_section_evaluations(department_id, section_id):
    department = Department.find_by_id(int(department_id))
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    term_id = get_term_id(request)
    if not section_id or not re.match(r'\d{5}\Z', section_id):
        raise BadRequestError('Missing or invalid course number.')
    feed = department.evaluations_feed(term_id, section_id=section_id)
    return tolerant_jsonify(feed)


@app.route('/api/department/<department_id>/note', methods=['POST'])
@department_membership_required
def update_note(department_id):
    department = Department.find_by_id(int(department_id))
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    params = request.get_json()
    note = get_param(params, 'note')
    term_id = get_term_id(request)
    department_note = DepartmentNote.upsert(department_id, term_id=term_id, note=note)
    return tolerant_jsonify(department_note.to_api_json())


@app.route('/api/department/<department_id>/evaluations', methods=['POST'])
@login_required
def update_evaluations(department_id):  # noqa C901
    department = Department.find_by_id(department_id)
    if not department:
        raise ResourceNotFoundError(f'Department {department_id} not found.')
    params = request.get_json() or {}
    action = params.get('action')
    evaluation_ids = params.get('evaluationIds')
    if not evaluation_ids:
        raise BadRequestError('No evaluation ids supplied.')
    term_id = get_term_id(request)
    updated_ids = []
    uses_midterm_forms = department.fetch_summary_feed(term_id).get('usesMidtermForms')
    if action == 'confirm':
        evaluations_feed = department.evaluations_feed(term_id=term_id)
        _validate_confirmable(evaluation_ids, term_id, evaluations_feed)
        updated_ids = Evaluation.update_bulk(
            department_id=department_id,
            evaluation_ids=evaluation_ids,
            fields={'status': 'confirmed'},
            evaluations_feed=evaluations_feed,
        )
    elif action == 'delete':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'deleted'})
    elif action == 'duplicate':
        fields = None
        if params.get('fields'):
            fields = _validate_evaluation_fields(params.get('fields'), term_id, uses_midterm_forms)
        updated_ids = Evaluation.duplicate_bulk(department=department, term_id=term_id, evaluation_ids=evaluation_ids, fields=fields)
    elif action == 'edit':
        fields = _validate_evaluation_fields(params.get('fields'), term_id, uses_midterm_forms)
        evaluations_feed = None
        if fields.get('status') == 'confirmed':
            evaluations_feed = department.evaluations_feed(term_id=term_id)
            _validate_confirmable(evaluation_ids, term_id, evaluations_feed, fields=fields)
        updated_ids = Evaluation.update_bulk(
            department_id=department_id,
            evaluation_ids=evaluation_ids,
            fields=fields,
            evaluations_feed=evaluations_feed,
        )
    elif action == 'review':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'marked'})
    elif action == 'ignore':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': 'ignore'})
    elif action == 'unmark':
        updated_ids = Evaluation.update_bulk(department_id=department_id, evaluation_ids=evaluation_ids, fields={'status': None})
    else:
        raise BadRequestError('Invalid update action.')
    if not updated_ids:
        raise BadRequestError('Evaluations could not be updated.')
    response = department.evaluations_feed(term_id, evaluation_ids=updated_ids)
    return tolerant_jsonify(response)


def _validate_confirmable(evaluation_ids, term_id, evaluations_feed, fields={}):

    def _is_numeric(eid):
        return re.match(r'\d+\Z', str(eid))
    numeric_ids = [int(eid) for eid in evaluation_ids if _is_numeric(eid)]
    if numeric_ids:
        if not (fields.get('departmentForm') and fields.get('evaluationType') and fields.get('instructorUid') and fields.get('startDate')):
            validation_errors = Evaluation.get_invalid(term_id, evaluation_ids=numeric_ids)
            if validation_errors:
                raise BadRequestError('Could not confirm evaluations with errors.')

        def _defaults(e):
            return (
                e['id'],
                e['departmentForm']['id'],
                e['evaluationType']['id'],
                e['startDate'],
            )
        defaults = [_defaults(e) for e in evaluations_feed if (_is_numeric(e['id']) and e['departmentForm'] and e['evaluationType'])]
        conflicts = Evaluation.find_potential_conflicts(numeric_ids, fields, defaults)
        if conflicts:
            raise BadRequestError('Could not confirm evaluations with conflicting information.')


def _validate_evaluation_fields(fields, term_id, dept_uses_midterm_forms):  # noqa C901
    validated_fields = {}
    if not fields or not type(fields) is dict:
        raise BadRequestError('No fields supplied for evaluation edit.')
    for k, v in fields.items():
        if k == 'departmentFormId':
            if not v:
                validated_fields['departmentForm'] = None
            else:
                try:
                    department_form = DepartmentForm.find_by_id(int(v))
                except (TypeError, ValueError):
                    department_form = None
                    raise BadRequestError('Invalid department form.')
                if not department_form:
                    raise BadRequestError('Invalid department form.')
                elif department_form and department_form.deleted_at:
                    raise BadRequestError(f'Invalid department form {department_form.name}.')
                validated_fields['departmentForm'] = department_form
        elif k == 'startDate':
            try:
                validated_fields[k] = date.fromisoformat(v)
            except (TypeError, ValueError):
                raise BadRequestError(f'Invalid date format {v}.')
            _validate_current_term_date(validated_fields[k], term_id)
        elif k == 'evaluationTypeId':
            if not v:
                validated_fields['evaluationType'] = None
            else:
                try:
                    evaluation_type = EvaluationType.find_by_id(int(v))
                except (TypeError, ValueError):
                    evaluation_type = None
                if not evaluation_type:
                    raise BadRequestError(f'Invalid evaluation type id {v}.')
                validated_fields['evaluationType'] = evaluation_type
        elif k == 'instructorUid':
            try:
                validated_fields['instructorUid'] = str(int(v))
            except (TypeError, ValueError):
                raise BadRequestError(f'Invalid instructor UID {v}.')
        elif k == 'midterm':
            if v == 'true' and dept_uses_midterm_forms:
                validated_fields[k] = True
            elif v == 'false':
                validated_fields[k] = False
            else:
                raise BadRequestError(f'Invalid midterm value {v}')
        elif k == 'status':
            if v is None:
                validated_fields[k] = None
            elif v == 'review':
                validated_fields[k] = 'marked'
            elif v == 'confirmed':
                validated_fields[k] = 'confirmed'
            elif v == 'ignore':
                validated_fields[k] = 'ignore'
            else:
                raise BadRequestError(f'Invalid status value {v}')
        else:
            raise BadRequestError(f"Evaluation field '{k}' not recognized.")
    return validated_fields


def _validate_current_term_date(submitted_date, term_id):
    valid_meeting_dates = get_valid_meeting_dates(term_ids=[term_id])[0]
    if submitted_date < valid_meeting_dates['start_date'] or submitted_date > valid_meeting_dates['end_date']:
        submitted_date = safe_strftime(submitted_date, '%m/%d/%Y')
        raise BadRequestError(f'Date {submitted_date} is outside the {term_name_for_sis_id(term_id)} term.')

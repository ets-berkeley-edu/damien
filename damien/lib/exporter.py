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

from itertools import groupby

from damien.externals.s3 import get_s3_path, put_csv_to_s3
from damien.lib.berkeley import term_code_for_sis_id
from damien.lib.queries import get_confirmed_enrollments, get_loch_basic_attributes
from damien.lib.util import safe_strftime
from damien.models.department import Department
from damien.models.department_form import DepartmentForm
from damien.models.evaluation import is_modular
from damien.models.export import Export
from damien.models.user import User


def generate_exports(evals, term_id, timestamp):
    evaluations = {}
    instructors = {}
    sections = {}

    for dept_id, dept_evals in groupby(evals, key=lambda e: e.department_id):
        department_exports = Department.find_by_id(dept_id).get_evaluation_exports(term_id, evaluation_ids=[e.id for e in dept_evals])
        instructors.update(department_exports['instructors'])
        sections.update(department_exports['sections'])

        for export_key, instructor_uid_set in department_exports['evaluations'].items():
            if export_key not in evaluations:
                evaluations[export_key] = set()
            evaluations[export_key].update(instructor_uid_set)

    dept_forms_to_uids = {df.name: [udf.user.uid for udf in df.users] for df in DepartmentForm.query.filter_by(deleted_at=None).all()}

    courses, course_instructors, course_students, course_supervisors, students =\
        _generate_course_rows(term_id, sections, evaluations, dept_forms_to_uids)
    instructors = [_export_instructor_row(instructors[k]) for k in sorted(instructors.keys())]
    supervisors = [_export_supervisor_row(u) for u in User.get_dept_contacts_with_blue_permissions()]
    department_hierarchy, report_viewer_hierarchy = _generate_hierarchy_rows(dept_forms_to_uids)

    put_csv_to_s3(term_id, timestamp, 'courses', course_headers, courses)
    put_csv_to_s3(term_id, timestamp, 'course_instructors', course_instructor_headers, course_instructors)
    put_csv_to_s3(term_id, timestamp, 'course_students', course_student_headers, course_students)
    put_csv_to_s3(term_id, timestamp, 'course_supervisors', course_supervisor_headers, course_supervisors)
    put_csv_to_s3(term_id, timestamp, 'department_hierarchy', department_hierarchy_headers, department_hierarchy)
    put_csv_to_s3(term_id, timestamp, 'instructors', instructor_headers, instructors)
    put_csv_to_s3(term_id, timestamp, 'report_viewer_hierarchy', report_viewer_hierarchy_headers, report_viewer_hierarchy)
    put_csv_to_s3(term_id, timestamp, 'students', student_headers, students)
    put_csv_to_s3(term_id, timestamp, 'supervisors', supervisor_headers, supervisors)

    s3_path = get_s3_path(term_id, timestamp)
    export = Export.create(term_id, s3_path)
    return export.to_api_json()


def _generate_course_rows(term_id, sections, keys_to_instructor_uids, dept_forms_to_uids):
    course_rows = []
    course_instructor_rows = []
    course_student_rows = []
    course_supervisor_rows = []

    enrollments = get_confirmed_enrollments(term_id)
    students_by_uid = {r['uid']: r for r in get_loch_basic_attributes(list({e['ldap_uid'] for e in enrollments}))}

    course_numbers_to_uids = {}
    for k, v in groupby(enrollments, key=lambda e: e['course_number']):
        course_numbers_to_uids[k] = [e['ldap_uid'] for e in v if e['ldap_uid'] in students_by_uid]

    sorted_keys = sorted(keys_to_instructor_uids.keys(), key=lambda k: (k.course_number, k.department_form, k.evaluation_type))

    for course_number, keys in groupby(sorted_keys, lambda k: k.course_number):
        course_id_prefix = f'{term_code_for_sis_id(term_id)}-{course_number}'
        keys = list(keys)

        # One key per course number makes life easy.
        if len(keys) == 1:
            course_ids = {keys[0]: course_id_prefix}
        # A couple of common cases.
        elif len(keys) == 2 and keys[0].evaluation_type == 'F' and keys[1].evaluation_type == 'G':
            course_ids = {keys[0]: course_id_prefix, keys[1]: f'{course_id_prefix}_GSI'}
        elif len(keys) == 2 and not keys[0].department_form.endswith('_MID') and keys[1].department_form.endswith('_MID'):
            course_ids = {keys[0]: course_id_prefix, keys[1]: f'{course_id_prefix}_MID'}
        # If we can't make sense of how the eval keys differ, just use the alphabet.
        else:
            course_ids = {key: f'{course_id_prefix}_{chr(65 + index)}' for index, key in enumerate(keys)}

        for key in keys:
            course_rows.append(_export_course_row(course_ids[key], key, sections[course_number]))
            for instructor_uid in keys_to_instructor_uids[key]:
                course_instructor_rows.append({'COURSE_ID': course_ids[key], 'LDAP_UID': instructor_uid})
            for student_uid in course_numbers_to_uids.get(course_number, []):
                course_student_rows.append({'COURSE_ID': course_ids[key], 'LDAP_UID': student_uid})
            for supervisor_uid in dept_forms_to_uids.get(key.department_form, []):
                course_supervisor_rows.append({'COURSE_ID': course_ids[key], 'LDAP_UID': supervisor_uid, 'DEPT_NAME': key.department_form})

    student_rows = [_export_student_row(v) for v in students_by_uid.values()]

    return course_rows, course_instructor_rows, course_student_rows, course_supervisor_rows, student_rows


def _generate_hierarchy_rows(dept_forms_to_uids):
    department_hierarchy_rows = [{
        'NODE_ID': 'UC Berkeley',
        'NODE_CAPTION': 'UC Berkeley',
        'PARENT_NODE_ID': None,
        'PARENT_NODE_CAPTION': None,
        'LEVEL': 1,
    }]
    report_viewer_hierarchy_rows = []

    for dept_form, uids in dept_forms_to_uids.items():
        department_hierarchy_rows.append({
            'NODE_ID': dept_form,
            'NODE_CAPTION': dept_form,
            'PARENT_NODE_ID': 'UC Berkeley',
            'PARENT_NODE_CAPTION': 'UC Berkeley',
            'LEVEL': 2,
        })
        for uid in uids:
            report_viewer_hierarchy_rows.append({
                'SOURCE': dept_form,
                'TARGET': uid,
                'ROLE_ID': 'DEPT_ADMIN',
            })

    return department_hierarchy_rows, report_viewer_hierarchy_rows


course_headers = [
    'COURSE_ID',
    'COURSE_ID_2',
    'COURSE_NAME',
    'CROSS_LISTED_FLAG',
    'CROSS_LISTED_NAME',
    'DEPT_NAME',
    'CATALOG_ID',
    'INSTRUCTION_FORMAT',
    'SECTION_NUM',
    'PRIMARY_SECONDARY_CD',
    'EVALUATE',
    'DEPT_FORM',
    'EVALUATION_TYPE',
    'MODULAR_COURSE',
    'START_DATE',
    'END_DATE',
    'CANVAS_COURSE_ID',
    'QB_MAPPING',
]


course_instructor_headers = [
    'COURSE_ID',
    'LDAP_UID',
]


course_student_headers = [
    'COURSE_ID',
    'LDAP_UID',
]


course_supervisor_headers = [
    'COURSE_ID',
    'LDAP_UID',
    'DEPT_NAME',
]


department_hierarchy_headers = [
    'NODE_ID',
    'NODE_CAPTION',
    'PARENT_NODE_ID',
    'PARENT_NODE_CAPTION',
    'LEVEL',
]


instructor_headers = [
    'LDAP_UID',
    'SIS_ID',
    'FIRST_NAME',
    'LAST_NAME',
    'EMAIL_ADDRESS',
    'BLUE_ROLE',
]


report_viewer_hierarchy_headers = [
    'SOURCE',
    'TARGET',
    'ROLE_ID',
]


student_headers = [
    'LDAP_UID',
    'SIS_ID',
    'FIRST_NAME',
    'LAST_NAME',
    'EMAIL_ADDRESS',
]


supervisor_headers = [
    'LDAP_UID',
    'SIS_ID',
    'FIRST_NAME',
    'LAST_NAME',
    'EMAIL_ADDRESS',
    'SUPERVISOR_GROUP',
    'PRIMARY_ADMIN',
    'SECONDARY_ADMIN',
    'DEPT_NAME_1',
    'DEPT_NAME_2',
    'DEPT_NAME_3',
    'DEPT_NAME_4',
    'DEPT_NAME_5',
    'DEPT_NAME_6',
    'DEPT_NAME_7',
    'DEPT_NAME_8',
    'DEPT_NAME_9',
    'DEPT_NAME_10',
]


def _export_course_row(course_id, key, section):
    return {
        'COURSE_ID': course_id,
        'COURSE_ID_2': course_id,
        'COURSE_NAME': section.course_title,
        'CROSS_LISTED_FLAG': _cross_listed_flag(section),
        'CROSS_LISTED_NAME': _cross_listed_name(section),
        'DEPT_NAME': section.subject_area,
        'CATALOG_ID': section.catalog_id,
        'INSTRUCTION_FORMAT': section.instruction_format,
        'SECTION_NUM': section.section_num,
        'PRIMARY_SECONDARY_CD': 'P' if section.is_primary else 'S',
        'EVALUATE': 'Y',
        'DEPT_FORM': key.department_form,
        'EVALUATION_TYPE': key.evaluation_type,
        'MODULAR_COURSE': 'Y' if is_modular(key.start_date, key.end_date) else '',
        'START_DATE': safe_strftime(key.start_date, '%m-%d-%Y'),
        'END_DATE': safe_strftime(key.end_date, '%m-%d-%Y'),
        'CANVAS_COURSE_ID': '',
        'QB_MAPPING': '-'.join([key.department_form, key.evaluation_type]),
    }


def _cross_listed_flag(section):
    if section.cross_listed_with:
        return 'Y'
    elif section.room_shared_with:
        return 'RM SHARE'
    else:
        return ''


def _cross_listed_name(section):
    if section.cross_listed_with or section.room_shared_with:
        course_numbers = {section.course_number}
        course_numbers.update(section.cross_listed_with)
        course_numbers.update(section.room_shared_with)
        return '-'.join(sorted(s for s in course_numbers if s))
    else:
        return ''


def _export_instructor_row(instructor):
    return {
        'LDAP_UID': instructor['uid'],
        'SIS_ID': instructor['sisId'],
        'FIRST_NAME': instructor['firstName'],
        'LAST_NAME': instructor['lastName'],
        'EMAIL_ADDRESS': instructor['emailAddress'],
        'BLUE_ROLE': '23',
    }


def _export_student_row(student):
    return {
        'LDAP_UID': student['uid'],
        'SIS_ID': student['csid'],
        'FIRST_NAME': student['first_name'],
        'LAST_NAME': student['last_name'],
        'EMAIL_ADDRESS': student['email'],
    }


def _export_supervisor_row(user):
    row = {
        'LDAP_UID': user.uid,
        'SIS_ID': user.csid or f'UID:{user.uid}',
        'FIRST_NAME': user.first_name,
        'LAST_NAME': user.last_name,
        'EMAIL_ADDRESS': user.email,
        'SUPERVISOR_GROUP': 'DEPT_ADMIN',
        'PRIMARY_ADMIN': 'Y' if user.can_view_response_rates() else '',
        'SECONDARY_ADMIN': '',
    }
    dept_index = 1
    for udf in user.department_forms:
        row[f'DEPT_NAME_{dept_index}'] = udf.department_form.name
        dept_index += 1
    while dept_index <= 10:
        row[f'DEPT_NAME_{dept_index}'] = ''
        dept_index += 1
    return row

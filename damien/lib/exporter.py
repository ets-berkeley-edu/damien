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

import csv
from itertools import groupby
import os
import tempfile

from damien.externals.s3 import get_s3_path, put_binary_data_to_s3, stream_object_text
from damien.externals.sftp import get_sftp_client
from damien.lib.berkeley import term_code_for_sis_id, term_ids_range
from damien.lib.queries import get_confirmed_enrollments, get_loch_basic_attributes
from damien.lib.util import safe_strftime
from damien.models.department import Department
from damien.models.department_catalog_listing import DepartmentCatalogListing
from damien.models.department_form import DepartmentForm
from damien.models.evaluation import Evaluation, is_modular
from damien.models.export import Export
from damien.models.user import User
from flask import current_app as app


def background_generate_exports(app_arg, term_id, timestamp):
    with app_arg.app_context():
        try:
            generate_exports(term_id, timestamp)
        except Exception as e:
            app.logger.error('Background thread is stopping')
            app.logger.exception(e)
            Export.update_status(get_s3_path(term_id, timestamp), 'error')
            raise e


def generate_exports(term_id, timestamp):
    s3_path = get_s3_path(term_id, timestamp)
    export = Export.create(term_id, s3_path)
    all_catalog_listings = DepartmentCatalogListing.query.all()
    dept_forms_to_uids = {df.name: [udf.user.uid for udf in df.users] for df in DepartmentForm.query.all()}

    # Past terms are included in 1) course-instructor mappings; 2) course-supervisor mappings for cross-listed courses; 3) instructor data.
    past_term_ids = term_ids_range(app.config['EARLIEST_TERM_ID'], term_id)[:-1]
    course_instructors = list(csv.DictReader(stream_object_text('exports/legacy/course_instructors.csv') or []))
    xlisted_course_supervisors = []
    instructors_by_uid = {}

    for past_term_id in past_term_ids:
        evaluation_keys_to_instructor_uids, past_term_instructors, sections = _generate_evaluation_maps(past_term_id)
        instructors_by_uid.update(past_term_instructors)
        sorted_keys = sorted(evaluation_keys_to_instructor_uids.keys(), key=lambda k: (k.course_number, k.department_form, k.evaluation_type))
        for course_number, keys in groupby(sorted_keys, lambda k: k.course_number):
            keys = list(keys)
            course_ids = _generate_course_id_map(keys, course_number, past_term_id)
            for key in keys:
                course_instructors.extend(
                    _generate_course_instructor_rows(course_ids[key], evaluation_keys_to_instructor_uids[key], key.evaluation_type))
                xlisted_course_supervisors.extend(
                    _generate_xlisted_course_supervisor_rows(course_ids[key], course_number, sections, dept_forms_to_uids, all_catalog_listings))

    # All other exports are for the current term only.
    evaluation_keys_to_instructor_uids, current_term_instructors, sections = _generate_evaluation_maps(term_id)
    courses, current_term_course_instructors, course_students, course_supervisors, students, current_term_xlisted_course_supervisors =\
        _generate_course_rows(term_id, sections, evaluation_keys_to_instructor_uids, dept_forms_to_uids, all_catalog_listings)

    course_instructors.extend(current_term_course_instructors)
    xlisted_course_supervisors.extend(current_term_xlisted_course_supervisors)
    instructors_by_uid.update(current_term_instructors)

    instructors = []
    for legacy_instructor in csv.DictReader(stream_object_text('exports/legacy/instructors.csv') or []):
        if legacy_instructor['LDAP_UID'] not in instructors_by_uid:
            instructors.append(legacy_instructor)
    for instructor_uid in sorted(instructors_by_uid.keys()):
        instructors.append(_export_instructor_row(instructors_by_uid[instructor_uid]))

    supervisors = [_export_supervisor_row(u) for u in User.get_dept_contacts_with_blue_permissions()]
    department_hierarchy, report_viewer_hierarchy = _generate_hierarchy_rows(dept_forms_to_uids)

    try:
        with get_sftp_client() as sftp:
            upload(sftp, term_id, timestamp, 'courses', course_headers, courses)
            upload(sftp, term_id, timestamp, 'course_instructors', course_instructor_headers, course_instructors)
            upload(sftp, term_id, timestamp, 'course_students', course_student_headers, course_students)
            upload(sftp, term_id, timestamp, 'course_supervisors', course_supervisor_headers, course_supervisors)
            upload(sftp, term_id, timestamp, 'department_hierarchy', department_hierarchy_headers, department_hierarchy)
            upload(sftp, term_id, timestamp, 'instructors', instructor_headers, instructors)
            upload(sftp, term_id, timestamp, 'report_viewer_hierarchy', report_viewer_hierarchy_headers, report_viewer_hierarchy)
            upload(sftp, term_id, timestamp, 'students', student_headers, students)
            upload(sftp, term_id, timestamp, 'supervisors', supervisor_headers, supervisors)
            upload(sftp, term_id, timestamp, 'xlisted_course_supervisors', xlisted_course_supervisor_headers, xlisted_course_supervisors)

            export = Export.update_status(s3_path, 'success')
            return export.to_api_json()

    except Exception as e:
        app.logger.error(f'Error uploading exports: term_id={term_id}, timestamp={timestamp}, error={e}')
        Export.update_status(s3_path, 'error')
        return None


def upload(sftp, term_id, timestamp, filename, headers, rows):
    success = False

    tmpfile = tempfile.NamedTemporaryFile()
    with open(tmpfile.name, mode='wt', encoding='utf-8') as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        csv_writer.writeheader()
        csv_writer.writerows(rows)

    filesize = os.stat(tmpfile.name).st_size
    with open(tmpfile.name, mode='rb') as f:
        if sftp:
            sftp.putfo(f, f'{filename}.csv', file_size=filesize)
        f.seek(0)
        if put_binary_data_to_s3(get_s3_path(term_id, timestamp, filename), f, 'text/csv'):
            success = True

    if not success:
        raise RuntimeError(f'Could not upload {filename}')


def _generate_course_rows(term_id, sections, keys_to_instructor_uids, dept_forms_to_uids, all_catalog_listings):
    course_rows = []
    course_instructor_rows = []
    course_student_rows = []
    course_supervisor_rows = []
    xlisted_course_supervisor_rows = []

    enrollments = get_confirmed_enrollments(term_id)
    students_by_uid = {r['uid']: r for r in get_loch_basic_attributes(list({e['ldap_uid'] for e in enrollments}))}

    course_numbers_to_uids = {}
    for k, v in groupby(enrollments, key=lambda e: e['course_number']):
        course_numbers_to_uids[k] = [e['ldap_uid'] for e in v if e['ldap_uid'] in students_by_uid]

    sorted_keys = sorted(
        keys_to_instructor_uids.keys(),
        key=lambda k: (k.course_number, k.department_form, k.evaluation_type, k.start_date, k.end_date),
    )

    for course_number, keys in groupby(sorted_keys, lambda k: k.course_number):
        keys = list(keys)
        course_ids = _generate_course_id_map(keys, course_number, term_id)
        for key in keys:
            course_rows.append(_export_course_row(course_ids[key], key, sections[course_number]))
            course_instructor_rows.extend(
                _generate_course_instructor_rows(course_ids[key], keys_to_instructor_uids[key], key.evaluation_type))
            for student_uid in course_numbers_to_uids.get(course_number, []):
                course_student_rows.append({'COURSE_ID': course_ids[key], 'LDAP_UID': student_uid})
            for supervisor_uid in dept_forms_to_uids.get(key.department_form, []):
                course_supervisor_rows.append({'COURSE_ID': course_ids[key], 'LDAP_UID': supervisor_uid, 'DEPT_NAME': key.department_form})
            xlisted_course_supervisor_rows.extend(
                _generate_xlisted_course_supervisor_rows(course_ids[key], course_number, sections, dept_forms_to_uids, all_catalog_listings))

    student_rows = [_export_student_row(v) for v in students_by_uid.values()]

    return course_rows, course_instructor_rows, course_student_rows, course_supervisor_rows, student_rows, xlisted_course_supervisor_rows


def _generate_course_id_map(keys, course_number, term_id):
    course_id_prefix = f'{term_code_for_sis_id(term_id)}-{course_number}'
    # Try generating unique IDs by evaluation type and/or department form.
    course_id_map = {}
    for key in keys:
        postfix = f"{'_GSI' if key.evaluation_type == 'G' else ''}{'_MID' if key.department_form.endswith('_MID') else ''}"
        course_id_map[key] = f'{course_id_prefix}{postfix}'
    if len(set(course_id_map.values())) == len(keys):
        return course_id_map
    # If we can't make sense of how the eval keys differ, just use the alphabet.
    else:
        course_id_map = {}
        for index, key in enumerate(keys):
            postfix = '' if index == 0 else f'_{chr(64 + index)}'
            course_id_map[key] = f'{course_id_prefix}{postfix}'
        return course_id_map


def _generate_evaluation_maps(term_id):
    evaluations = {}
    instructors = {}
    sections = {}

    db_evals = Evaluation.get_confirmed(term_id)

    for dept_id, dept_evals in groupby(db_evals, key=lambda e: e.department_id):
        department_exports = Department.find_by_id(dept_id).get_evaluation_exports(term_id, evaluation_ids=[e.id for e in dept_evals])
        instructors.update(department_exports['instructors'])
        sections.update(department_exports['sections'])

        for export_key, instructor_uid_set in department_exports['evaluations'].items():
            if export_key not in evaluations:
                evaluations[export_key] = set()
            evaluations[export_key].update(instructor_uid_set)
    return evaluations, instructors, sections


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


def _generate_course_instructor_rows(course_id, instructor_uids, evaluation_type):
    rows = []
    for instructor_uid in instructor_uids:
        if evaluation_type == 'F':
            role = 'Faculty'
        elif evaluation_type == 'G':
            role = 'GSI'
        else:
            role = evaluation_type
        rows.append({
            'COURSE_ID': course_id,
            'LDAP_UID': instructor_uid,
            'ROLE': role,
        })
    return rows


def _generate_xlisted_course_supervisor_rows(course_id, course_number, sections, dept_forms_to_uids, all_catalog_listings):
    rows = []
    cln = _cross_listed_name(sections[course_number])
    if cln:
        supervisor_uids = set()
        for n in cln.split('-'):
            catalog_listing = None
            try:
                catalog_listing = sections[n].find_catalog_listing(all_catalog_listings)
            except KeyError as e:
                app.logger.error(
                    f'Error exporting xlisted course supervisors: course_number={course_number}, xlisted_name={cln}, error=KeyError: {e}',
                )
            if catalog_listing and catalog_listing.default_form:
                for supervisor_uid in dept_forms_to_uids.get(catalog_listing.default_form.name, []):
                    supervisor_uids.add(supervisor_uid)
        for supervisor_uid in sorted(supervisor_uids):
            rows.append({'COURSE_ID': course_id, 'LDAP_UID': supervisor_uid})
    return rows


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
    'ROLE',
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


xlisted_course_supervisor_headers = [
    'COURSE_ID',
    'LDAP_UID',
]


def _export_course_row(course_id, key, section):
    return {
        'COURSE_ID': course_id,
        'COURSE_ID_2': course_id,
        'COURSE_NAME': _course_name(section, course_id),
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
        'START_DATE': safe_strftime(key.start_date, '%-m/%-d/%y'),
        'END_DATE': safe_strftime(key.end_date, '%-m/%-d/%y'),
        'CANVAS_COURSE_ID': '',
        'QB_MAPPING': '-'.join([key.department_form, key.evaluation_type]),
    }


def _course_name(section, course_id):
    name = ' '.join([
        section.subject_area,
        section.catalog_id,
        section.instruction_format,
        section.section_num,
        section.course_title,
    ])
    if course_id.endswith('_GSI'):
        name = name + ' (EVAL FOR GSI)'
    return name


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
        'SIS_ID': instructor['sisId'] or f"UID:{instructor['uid']}",
        'FIRST_NAME': instructor['firstName'],
        'LAST_NAME': instructor['lastName'],
        'EMAIL_ADDRESS': instructor['emailAddress'],
        'BLUE_ROLE': '23',
    }


def _export_student_row(student):
    return {
        'LDAP_UID': student['uid'],
        'SIS_ID': student['csid'] or f"UID:{student['uid']}",
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
    department_form_names = sorted(udf.department_form.name for udf in user.department_forms)
    for name in department_form_names:
        row[f'DEPT_NAME_{dept_index}'] = name
        dept_index += 1
    while dept_index <= 10:
        row[f'DEPT_NAME_{dept_index}'] = ''
        dept_index += 1
    return row

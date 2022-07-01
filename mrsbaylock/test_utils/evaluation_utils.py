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

from datetime import timedelta
import re

from damien import db, std_commit
from flask import current_app as app
from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.evaluation import Evaluation
from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.models.evaluation_type import EvaluationType
from mrsbaylock.models.instructor import Instructor
from mrsbaylock.test_utils import utils
from sqlalchemy import text
from sqlalchemy.exc import NoSuchColumnError


def list_to_str(list_o_strings):
    string = ''
    for i in list_o_strings:
        string += f'\'{i}\', '
    return string[:-2]


def get_evaluations(term, dept):
    evals_total = []
    get_sis_sections_to_evaluate(evals_total, term, dept)
    get_x_listings_and_shares(evals_total, term, dept)
    remove_listing_dept_forms(evals_total)
    get_manual_sections(evals_total, term, dept)
    edits = get_edited_sections(term, dept)
    merge_edited_evals(evals_total, edits)
    get_instructors(evals_total)
    get_eval_types(evals_total)
    calculate_eval_dates(evals_total)

    sorted_evals = sorted(
        evals_total,
        key=lambda x: (
            x.ccn, (float('-inf') if x.instructor and x.instructor.uid is None or 'None' or '' else float(x.uid))),
    )
    for e in sorted_evals:
        app.logger.info(f'Evaluation: {vars(e)}')
        app.logger.info(f'Instructor: {vars(e.instructor)}')
    return sorted_evals


def row_data(row, field):
    try:
        return row[field]
    except NoSuchColumnError:
        return None


def row_x_listings(row):
    try:
        return list(filter(lambda i: i != '', row['listings'].split(',')))
    except NoSuchColumnError:
        return []


def row_room_shares(row):
    try:
        return list(filter(lambda i: i != '', row['shares'].split(',')))
    except NoSuchColumnError:
        return []


def row_instructor(row):
    try:
        instructor_data = {
            'uid': row['uid'],
            'instructor_role': row['instructor_role'],
            'affiliations': None,
        }
        return Instructor(instructor_data)
    except NoSuchColumnError:
        return None


def row_eval_end_from_eval_start(course_start, eval_start):
    if course_start:
        return eval_start + timedelta(days=20) if (eval_start - course_start).days > 90 else eval_start + timedelta(days=13)
    else:
        return None


def row_eval_start_from_course_end(course_end, course_start):
    if course_start:
        return course_end - timedelta(days=20) if (course_end - course_start).days > 90 else course_end - timedelta(days=13)
    else:
        return None


def remove_listing_dept_forms(evals):
    for e in evals:
        if e.x_listing_ccns or e.room_share_ccns:
            e.dept_form = None


def calculate_eval_dates(evals):
    for e in evals:
        e.eval_end_date = row_eval_end_from_eval_start(e.course_start_date, e.eval_start_date) if e.eval_start_date else e.course_end_date
        e.eval_start_date = e.eval_start_date or row_eval_start_from_course_end(e.course_end_date, e.course_start_date)


def result_row_to_eval(row, term, dept):
    listings = row_x_listings(row)
    shares = row_room_shares(row)
    for i in listings:
        if i in shares:
            shares.remove(i)

    dept_form = row_data(row, 'dept_form')
    eval_type = row_data(row, 'eval_type')
    status = next(filter(lambda s: (s.value['db'] == row_data(row, 'status')), EvaluationStatus))

    instructor = row_instructor(row)
    if instructor.uid == 'None':
        instructor.uid = None

    course_start = row_data(row, 'course_start_date')
    course_end = row_data(row, 'course_end_date')
    eval_start = row_data(row, 'eval_start_date')
    eval_end = row_data(row, 'eval_end_date')

    eval_data = {
        'term': term,
        'dept': dept,
        'dept_form': dept_form,
        'eval_type': eval_type,
        'status': status,
        'ccn': row['ccn'],
        'x_listing_ccns': listings,
        'room_share_ccns': shares,
        'instructor': instructor,
        'subject': row['subject'],
        'catalog_id': row['catalog_id'],
        'instruction_format': row['instruction_format'],
        'section_num': row['section_num'],
        'title': row['title'],
        'primary': row['primary'],
        'course_start_date': course_start,
        'course_end_date': course_end,
        'eval_start_date': eval_start,
        'eval_end_date': eval_end,
    }
    return Evaluation(eval_data)


def result_to_evals(result, evaluations, term, dept):
    for row in result:
        evaluations.append(result_row_to_eval(row, term, dept))


def get_sis_sections_to_evaluate(evals_total, term, dept):
    # All subjects
    sql = 'SELECT department_catalog_listings.subject_area FROM department_catalog_listings'
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    all_subjects = [row['subject_area'] for row in result]

    # Dept subjects
    sql = f"""
        SELECT DISTINCT department_catalog_listings.subject_area
          FROM department_catalog_listings
         WHERE department_catalog_listings.department_id = '{dept.dept_id}'
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    dept_subjects = [row['subject_area'] for row in result]

    subjects = all_subjects if '' in dept_subjects else dept_subjects
    subject_str = list_to_str(subjects)

    clause = '' if '' in dept_subjects else ' AND unholy_loch.sis_sections.subject_area = department_catalog_listings.subject_area'
    sql = f"""
        SELECT unholy_loch.sis_sections.course_number AS ccn,
               ARRAY_TO_STRING(ARRAY_AGG(DISTINCT unholy_loch.cross_listings.cross_listing_number), ',') AS listings,
               ARRAY_TO_STRING(ARRAY_AGG(DISTINCT unholy_loch.co_schedulings.room_share_number), ',') AS shares,
               unholy_loch.sis_sections.subject_area AS subject,
               unholy_loch.sis_sections.catalog_id AS catalog_id,
               unholy_loch.sis_sections.instruction_format AS instruction_format,
               unholy_loch.sis_sections.section_num AS section_num,
               unholy_loch.sis_sections.course_title AS title,
               unholy_loch.sis_sections.is_primary AS primary,
               unholy_loch.sis_sections.instructor_uid AS uid,
               unholy_loch.sis_sections.instructor_role_code AS instructor_role,
               unholy_loch.sis_sections.meeting_start_date AS course_start_date,
               unholy_loch.sis_sections.meeting_end_date AS course_end_date,
               department_forms.name AS dept_form
          FROM departments
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.subject_area IN ({subject_str})
          JOIN department_catalog_listings
            ON department_catalog_listings.department_id = departments.id{clause}
          JOIN department_forms
            ON department_forms.id = department_catalog_listings.default_form_id
     LEFT JOIN unholy_loch.cross_listings
            ON unholy_loch.cross_listings.course_number = unholy_loch.sis_sections.course_number
           AND unholy_loch.cross_listings.term_id = unholy_loch.sis_sections.term_id
     LEFT JOIN unholy_loch.co_schedulings
            ON unholy_loch.co_schedulings.course_number = unholy_loch.sis_sections.course_number
           AND unholy_loch.co_schedulings.term_id = unholy_loch.sis_sections.term_id
         WHERE departments.id = '{dept.dept_id}'
           AND unholy_loch.sis_sections.term_id = '{term.term_id}'
           AND unholy_loch.sis_sections.enrollment_count > 0
           AND (unholy_loch.sis_sections.instructor_role_code IS NULL
            OR unholy_loch.sis_sections.instructor_role_code !='ICNT')
           AND unholy_loch.sis_sections.instruction_format NOT IN ('CLC', 'GRP', 'IND', 'SUP', 'VOL')
      GROUP BY unholy_loch.sis_sections.course_number,
               unholy_loch.sis_sections.subject_area,
               unholy_loch.sis_sections.catalog_id,
               unholy_loch.sis_sections.instruction_format,
               unholy_loch.sis_sections.section_num,
               unholy_loch.sis_sections.course_title,
               unholy_loch.sis_sections.is_primary,
               unholy_loch.sis_sections.instructor_uid,
               unholy_loch.sis_sections.instructor_role_code,
               unholy_loch.sis_sections.enrollment_count,
               unholy_loch.sis_sections.meeting_start_date,
               unholy_loch.sis_sections.meeting_end_date,
               department_forms.name;
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    evaluations = []
    result_to_evals(result, evaluations, term, dept)

    for subject in dept_subjects:
        evals_to_include = []
        sql = f"SELECT catalog_id FROM department_catalog_listings WHERE subject_area = \'{subject}\' AND department_id = '{dept.dept_id}'"
        catalog_ids_to_include = get_subj_catalog_ids(sql)
        app.logger.info(f'Catalog IDs to include {catalog_ids_to_include}')
        get_matching_evals(subject, catalog_ids_to_include, evaluations, evals_to_include, evals_total)
        evals_total += evals_to_include

        evals_to_exclude = []
        sql = f'SELECT catalog_id FROM department_catalog_listings WHERE subject_area = \'\' AND department_id != \'{dept.dept_id}\''
        catalog_ids_to_exclude = get_subj_catalog_ids(sql)
        sql = f'SELECT catalog_id FROM department_catalog_listings WHERE subject_area = \'{subject}\' AND department_id != \'{dept.dept_id}\''
        catalog_ids_to_exclude += get_subj_catalog_ids(sql)
        app.logger.info(f'Catalog IDs to exclude {catalog_ids_to_exclude}')
        get_matching_evals(subject, catalog_ids_to_exclude, evaluations, evals_to_exclude, evals_total)

        for i in evals_to_exclude:
            if i in evals_total:
                evals_total.remove(i)
    return evals_total


def get_subj_catalog_ids(sql):
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    catalog_ids = []
    for row in result:
        catalog_ids.append(row['catalog_id'])
    catalog_ids = list(filter(None, catalog_ids))
    return catalog_ids


def get_matching_evals(subject, catalog_ids, all_evals, matching_evals, included_evals):
    for evaluation in all_evals:
        if catalog_ids:
            for catalog_id in catalog_ids:
                if subject == '' or evaluation.subject == subject:
                    match = re.search(f'^{catalog_id}$', evaluation.catalog_id)
                    if match:
                        matching_evals.append(evaluation)
        else:
            if evaluation.subject == subject:
                if evaluation not in included_evals:
                    matching_evals.append(evaluation)


def get_x_listings_and_shares(evals, term, dept):
    ccns = []
    for i in evals:
        for x in i.x_listing_ccns:
            if x != '':
                ccns.append(x)
        for x in i.room_share_ccns:
            if x != '':
                ccns.append(x)
    if ccns:
        ccn_str = list_to_str(ccns)
        sql = f"""
            SELECT unholy_loch.sis_sections.course_number AS ccn,
                   ARRAY_TO_STRING(ARRAY_AGG(DISTINCT unholy_loch.cross_listings.cross_listing_number), ',') AS listings,
                   ARRAY_TO_STRING(ARRAY_AGG(DISTINCT unholy_loch.co_schedulings.room_share_number), ',') AS shares,
                   unholy_loch.sis_sections.subject_area AS subject,
                   unholy_loch.sis_sections.catalog_id AS catalog_id,
                   unholy_loch.sis_sections.instruction_format AS instruction_format,
                   unholy_loch.sis_sections.section_num AS section_num,
                   unholy_loch.sis_sections.course_title AS title,
                   unholy_loch.sis_sections.is_primary AS primary,
                   unholy_loch.sis_sections.instructor_uid AS uid,
                   unholy_loch.sis_sections.instructor_role_code AS instructor_role,
                   unholy_loch.sis_sections.meeting_start_date AS course_start_date,
                   unholy_loch.sis_sections.meeting_end_date AS course_end_date
              FROM unholy_loch.sis_sections
         LEFT JOIN unholy_loch.cross_listings
                ON unholy_loch.cross_listings.course_number = unholy_loch.sis_sections.course_number
               AND unholy_loch.cross_listings.term_id = unholy_loch.sis_sections.term_id
         LEFT JOIN unholy_loch.co_schedulings
                ON unholy_loch.co_schedulings.course_number = unholy_loch.sis_sections.course_number
               AND unholy_loch.co_schedulings.term_id = unholy_loch.sis_sections.term_id
             WHERE unholy_loch.sis_sections.course_number IN({ccn_str})
               AND unholy_loch.sis_sections.term_id = '{term.term_id}'
               AND unholy_loch.sis_sections.enrollment_count > 0
               AND (unholy_loch.sis_sections.instructor_role_code IS NULL
                OR unholy_loch.sis_sections.instructor_role_code !='ICNT')
               AND unholy_loch.sis_sections.instruction_format NOT IN ('CLC', 'GRP', 'IND', 'SUP', 'VOL')
          GROUP BY unholy_loch.sis_sections.course_number,
                   unholy_loch.sis_sections.subject_area,
                   unholy_loch.sis_sections.catalog_id,
                   unholy_loch.sis_sections.instruction_format,
                   unholy_loch.sis_sections.section_num,
                   unholy_loch.sis_sections.course_title,
                   unholy_loch.sis_sections.is_primary,
                   unholy_loch.sis_sections.instructor_uid,
                   unholy_loch.sis_sections.instructor_role_code,
                   unholy_loch.sis_sections.enrollment_count,
                   unholy_loch.sis_sections.meeting_start_date,
                   unholy_loch.sis_sections.meeting_end_date;
        """
        app.logger.info(sql)
        result = db.session.execute(text(sql))
        std_commit(allow_test_environment=True)
        result_to_evals(result, evals, term, dept)


def get_manual_sections(evals, term, dept):
    sql = f"""
        SELECT supplemental_sections.course_number AS ccn,
               unholy_loch.sis_sections.subject_area AS subject,
               unholy_loch.sis_sections.catalog_id AS catalog_id,
               unholy_loch.sis_sections.instruction_format AS instruction_format,
               unholy_loch.sis_sections.section_num AS section_num,
               unholy_loch.sis_sections.course_title AS title,
               unholy_loch.sis_sections.is_primary AS primary,
               unholy_loch.sis_sections.instructor_uid AS uid,
               unholy_loch.sis_sections.instructor_role_code AS instructor_role,
               unholy_loch.sis_sections.meeting_start_date AS course_start_date,
               unholy_loch.sis_sections.meeting_end_date AS course_end_date
          FROM supplemental_sections
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.course_number = supplemental_sections.course_number
         WHERE supplemental_sections.department_id = '{dept.dept_id}'
           AND supplemental_sections.term_id = '{term.term_id}'
           AND unholy_loch.sis_sections.term_id = '{term.term_id}'
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    result_to_evals(result, evals, term, dept)


def get_edited_sections(term, dept):
    sql = f"""
        SELECT evaluations.course_number AS ccn,
               unholy_loch.sis_sections.subject_area AS subject,
               unholy_loch.sis_sections.catalog_id AS catalog_id,
               unholy_loch.sis_sections.instruction_format AS instruction_format,
               unholy_loch.sis_sections.section_num AS section_num,
               unholy_loch.sis_sections.course_title AS title,
               unholy_loch.sis_sections.is_primary AS primary,
               evaluations.instructor_uid AS uid,
               unholy_loch.sis_sections.instructor_role_code AS instructor_role,
               evaluations.start_date AS eval_start_date,
               evaluations.end_date AS eval_end_date,
               evaluations.status AS status,
               department_forms.name AS dept_form,
               evaluation_types.name AS eval_type
          FROM evaluations
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.course_number = evaluations.course_number
     LEFT JOIN department_forms
            ON department_forms.id = evaluations.department_form_id
     LEFT JOIN evaluation_types
            ON evaluation_types.id = evaluations.evaluation_type_id
         WHERE evaluations.term_id = '{term.term_id}'
           AND unholy_loch.sis_sections.term_id = '{term.term_id}'
    """
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    evals = []
    result_to_evals(results, evals, term, dept)
    return evals


def merge_edited_evals(evaluations, edited_evals):
    eval_ccns = []
    for e in evaluations:
        eval_ccns.append(e.ccn)
    for edit in edited_evals:
        uid = edit.instructor.uid if edit.instructor else ''
        app.logger.info(f'Checking edited eval for {edit.ccn}-{uid}')
        match = None
        for e in evaluations:
            if e.ccn == edit.ccn and e.instructor and e.instructor.uid == uid and e.dept_form != edit.dept_form:
                match = True
                app.logger.info(f'Merging existing eval for {e.ccn}-{uid}')
                e.status = edit.status
                if edit.dept_form:
                    e.dept_form = edit.dept_form
                if edit.eval_type:
                    e.eval_type = edit.eval_type
                if edit.eval_start_date:
                    e.eval_start_date = edit.eval_start_date
                if edit.eval_end_date:
                    e.eval_end_date = edit.eval_end_date
        if not match and edit.ccn in eval_ccns:
            app.logger.info(f'CCN match but no UID match, adding new eval for {edit.ccn}-{uid}')
            evaluations.append(edit)


def get_all_dept_forms():
    sql = 'SELECT name FROM department_forms WHERE deleted_at IS NULL'
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    forms = []
    for row in results:
        forms.append(DepartmentForm(row['name']))
    return forms


def get_all_eval_types():
    sql = 'SELECT name FROM evaluation_types WHERE deleted_at IS NULL'
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    types = []
    for row in results:
        types.append(EvaluationType(row['name']))
    return types


def get_instructors(evals):
    instructors = []
    uids = []
    for e in evals:
        if e.instructor and e.instructor.uid not in uids:
            uids.append(e.instructor.uid)
    uids = [u for u in uids if (u and u != 'None')]
    if uids:
        uids_string = list_to_str(uids)
        sql = f"""
            SELECT ldap_uid,
                   first_name,
                   last_name,
                   email_address,
                   deleted_at
              FROM supplemental_instructors
             WHERE ldap_uid IN({uids_string})
        """
        app.logger.info(sql)
        results = db.session.execute(text(sql))
        std_commit(allow_test_environment=True)
        for row in results:
            app.logger.info(f"Checking UID {row['ldap_uid']}")
            if not row['deleted_at']:
                instructors.append(Instructor({
                    'uid': row['ldap_uid'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email_address'],
                    'affiliations': None,
                }))

        for i in instructors:
            uids.remove(i.uid)
        uids_string = list_to_str(uids)
        sql = f"""
            SELECT ldap_uid,
                   sis_id,
                   first_name,
                   last_name,
                   email_address,
                   affiliations,
                   deleted_at
              FROM unholy_loch.sis_instructors
             WHERE ldap_uid IN({uids_string})
        """
        app.logger.info(sql)
        results = db.session.execute(text(sql))
        std_commit(allow_test_environment=True)
        for row in results:
            # TODO if not row['deleted_at']:
            instructors.append(Instructor({
                'uid': row['ldap_uid'],
                'csid': row['sis_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email_address'],
                'affiliations': row['affiliations'],
            }))

        for e in evals:
            for i in instructors:
                if e.instructor and e.instructor.uid == i.uid:
                    e.instructor.csid = i.csid
                    e.instructor.first_name = i.first_name
                    e.instructor.last_name = i.last_name
                    e.instructor.email = i.email
                    e.instructor.affiliations = i.affiliations


def get_section_dept(ccn, all_users=None):
    sql = f"""
        SELECT dept_name
          FROM departments
          JOIN department_catalog_listings
            ON department_catalog_listings.department_id = departments.id
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.subject_area = department_catalog_listings.subject_area
         WHERE unholy_loch.sis_sections.course_number = '{ccn}'
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return utils.get_dept(result['dept_name'], all_users)


def get_eval_types(evals):
    for e in evals:
        if e.eval_type or e.dept.dept_id == '92':
            app.logger.info('Skipping eval type')
        else:
            if e.instructor.uid and e.instructor.affiliations:
                affils = e.instructor.affiliations
                if 'EMPLOYEE-TYPE-ACADEMIC' in affils:
                    if 'STUDENT-TYPE' in affils:
                        e.eval_type = 'G'
                    else:
                        e.eval_type = 'F'
                elif 'STUDENT-TYPE' in affils:
                    e.eval_type = 'G'
                else:
                    e.eval_type = None
            else:
                e.eval_type = None

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

from datetime import datetime
from datetime import timedelta
import itertools
import re

from damien import db, std_commit
from flask import current_app as app
from mrsbaylock.models.department import Department
from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.department_note import DepartmentNote
from mrsbaylock.models.evaluation import Evaluation
from mrsbaylock.models.evaluation_type import EvaluationType
from mrsbaylock.models.instructor import Instructor
from mrsbaylock.models.term import Term
from mrsbaylock.models.user import User
from mrsbaylock.models.user_dept_role import UserDeptRole
from sqlalchemy import text
from sqlalchemy.exc import NoSuchColumnError


def get_browser():
    return app.config['BROWSER']


def browser_is_headless():
    return app.config['BROWSER_HEADLESS']


def get_click_sleep():
    return app.config['CLICK_SLEEP']


def get_short_timeout():
    return app.config['TIMEOUT_SHORT']


def get_medium_timeout():
    return app.config['TIMEOUT_MEDIUM']


def get_long_timeout():
    return app.config['TIMEOUT_LONG']


def get_admin_uid():
    return app.config['ADMIN_UID']


def get_admin_username():
    return app.config['ADMIN_USERNAME']


def get_admin_password():
    return app.config['ADMIN_PASSWORD']


def get_test_dept_contact_uid():
    return app.config['TEST_DEPT_CONTACT_UID']


def get_test_email_account():
    return app.config['TEST_EMAIL']


def default_download_dir():
    return f'{app.config["BASE_DIR"]}/mrsbaylock/downloads'


def get_current_term():
    return Term(
        term_id=app.config['CURRENT_TERM_ID'],
        name=app.config['CURRENT_TERM_NAME'],
        start_date=datetime.strptime(app.config['CURRENT_TERM_BEGIN'], '%Y-%m-%d'),
        end_date=datetime.strptime(app.config['CURRENT_TERM_END'], '%Y-%m-%d'),
    )


def get_previous_term_code(current_term_id):
    d1 = '2'
    d2_3 = str(int(current_term_id[1:3]) - 1) if (current_term_id[-1] == '2') else current_term_id[1:2]
    if current_term_id[3] == '8':
        d4 = '5'
    elif current_term_id[3] == '5':
        d4 = '2'
    else:
        d4 = '8'
    return d1 + d2_3 + d4


# DATABASE - USERS


def get_all_users():
    sql = """SELECT users.id,
                    users.uid,
                    users.csid,
                    users.first_name,
                    users.last_name,
                    users.email,
                    users.blue_permissions,
                    department_members.department_id,
                    department_members.can_receive_communications,
                    ARRAY_TO_STRING(ARRAY_AGG(department_forms.name), ',') AS forms
               FROM users
          LEFT JOIN department_members ON department_members.user_id = users.id
          LEFT JOIN departments ON departments.id = department_members.department_id
          LEFT JOIN user_department_forms ON user_department_forms.user_id = users.id
          LEFT JOIN department_forms ON department_forms.id = user_department_forms.department_form_id
           GROUP BY users.id, users.uid, users.csid, users.first_name, users.last_name, users.blue_permissions,
                    department_members.department_id,
                    department_members.can_receive_communications
    """
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    users_data = []
    for row in results:
        form_names = row['forms'].split(',')
        form_names.sort()
        forms = list(map(lambda name: DepartmentForm(name), form_names))
        data = {
            'user_id': row['id'],
            'uid': row['uid'],
            'csid': row['csid'],
            'first_name': row['first_name'].strip(),
            'last_name': row['last_name'].strip(),
            'email': row['email'],
            'blue_permissions': row['blue_permissions'],
            'dept_id': row['department_id'],
            'receives_comms': row['can_receive_communications'],
            'dept_forms': forms,
        }
        users_data.append(data)
    users = []
    key = lambda x: x['uid']
    grouped = itertools.groupby(users_data, key)
    for k, g in grouped:
        grp = list(g)
        data = {
            'user_id': grp[0]['user_id'],
            'uid': grp[0]['uid'],
            'csid': grp[0]['csid'],
            'first_name': grp[0]['first_name'],
            'last_name': grp[0]['last_name'],
            'email': grp[0]['email'],
            'blue_permissions': grp[0]['blue_permissions'],
            'dept_forms': grp[0]['dept_forms'],
        }
        dept_roles = []
        for i in grp:
            role = UserDeptRole(dept_id=i['dept_id'], receives_comms=i['receives_comms'])
            dept_roles.append(role)
        user = User(data, dept_roles)
        users.append(user)
        for r in user.dept_roles:
            app.logger.info(f'{vars(r)}')
    return users


def get_user(uid):
    users = get_all_users()
    for u in users:
        if u.uid == uid:
            user = u
    return user


def get_user_id(user):
    sql = f"SELECT id FROM users WHERE users.uid = '{user.uid}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result['id']


def get_dept_users(dept, all_users=None):
    dept_users = []
    users = all_users or get_all_users()
    for u in users:
        for r in u.dept_roles:
            if r.dept_id == dept.dept_id:
                dept_users.append(u)
    for u in dept_users:
        app.logger.info(f'{vars(u)}')
        for r in u.dept_roles:
            app.logger.info(f'{vars(r)}')
    return dept_users


def get_user_dept_role(user, dept):
    for role in user.dept_roles:
        if role.dept_id == dept.dept_id:
            return role


def get_test_user(dept_role=None, blue_permissions=None):
    user = User({
        'uid': app.config['TEST_DEPT_CONTACT_UID'],
        'first_name': app.config['TEST_DEPT_CONTACT_FIRST_NAME'],
        'last_name': app.config['TEST_DEPT_CONTACT_LAST_NAME'],
        'email': app.config['TEST_DEPT_CONTACT_EMAIL'],
        'dept_forms': list(map(lambda f: DepartmentForm(f), (app.config['TEST_DEPT_CONTACT_FORMS'].split(',')))),
    })
    user.blue_permissions = blue_permissions
    if dept_role:
        user.dept_roles.append(dept_role)
    return user


def create_admin_user(user):
    sql = f"""
        INSERT INTO users (
            csid, uid, first_name, last_name, email, is_admin, blue_permissions,
            created_at, updated_at, login_at
        )
        SELECT
            '{user.csid}', '{user.uid}', '{user.first_name}', '{user.last_name}', '{user.email}', TRUE, NULL,
            NOW(), NOW(), NULL
    """
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def hard_delete_user(user):
    sql = f"DELETE FROM users WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def soft_delete_user(user):
    sql = f"UPDATE users SET deleted_at = NOW() WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def restore_user(user):
    sql = f"UPDATE users SET deleted_at = NULL WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


# DEPARTMENTS


def get_participating_depts():
    sql = 'SELECT id, dept_name FROM departments WHERE is_enrolled IS TRUE'
    app.logger.info(sql)
    depts = []
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in result:
        data = {
            'dept_id': row['id'],
            'name': row['dept_name'],
            'participating': True,
        }
        depts.append(Department(data))
    return depts


def get_dept(name, all_users=None):
    sql = f"""
        SELECT departments.id AS dept_id,
               departments.is_enrolled,
               department_notes.term_id,
               department_notes.note
          FROM departments
     LEFT JOIN department_notes
            ON departments.id = department_notes.department_id
         WHERE departments.dept_name = '{name}';
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    app.logger.info(result)
    dept_terms_data = []
    for row in result:
        term_data = {
            'dept_id': row['dept_id'],
            'participating': row['is_enrolled'],
            'term_id': row['term_id'],
            'note': row['note'],
        }
        dept_terms_data.append(term_data)
    key = lambda x: x['dept_id']
    grouped = itertools.groupby(dept_terms_data, key)
    for k, g in grouped:
        grp = list(g)
        dept_data = {
            'dept_id': grp[0]['dept_id'],
            'name': name,
            'participating': grp[0]['participating'],
        }
        notes = []
        for i in grp:
            note = DepartmentNote(term_id=i['term_id'], note=i['note'])
            notes.append(note)
    dept = Department(dept_data, notes)
    app.logger.info(f'Department object: {vars(dept)}')
    for n in dept.notes:
        app.logger.info(f'Department note: {vars(n)}')
    dept.users = get_dept_users(dept, all_users)
    return dept


def get_test_dept_1():
    name = app.config['TEST_DEPT_1']
    return get_dept(name)


def get_test_dept_2():
    name = app.config['TEST_DEPT_2']
    return get_dept(name)


def get_dept_sans_contacts():
    sql = """SELECT name
               FROM departments
              WHERE is_enrolled IS True
                AND id NOT IN (SELECT DISTINCT(department_id)
                                 FROM department_members)
              LIMIT 1
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return get_dept(result['name'])


def create_dept_note(term, dept, note):
    delete_dept_note(term, dept)
    sql = f"""
        INSERT INTO department_notes (department_id, term_id, note, created_at, updated_at)
             VALUES ('{dept.dept_id}', '{term.term_id}', '{note}', now(), now())
    """
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def delete_dept_note(term, dept):
    sql = f"""
        DELETE FROM department_notes
              WHERE department_id = {dept.dept_id}
                AND term_id = '{term.term_id}'
    """
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    dept.note = None


# EVALUATIONS


def list_to_str(list_o_strings):
    string = ''
    for i in list_o_strings:
        string += f'\'{i}\', '
    return string[:-2]


def get_evaluations(term, dept):
    # All subjects
    sql = 'SELECT department_catalog_listings.subject_area FROM department_catalog_listings'
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    all_subjects = [row['subject_area'] for row in result]

    # Dept subjects
    sql = f"""
        SELECT department_catalog_listings.subject_area
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
    evals_total = []

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

    get_x_listings_and_shares(evals_total, term, dept)
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


def row_eval_end_from_eval_start(evaluation):
    course_start = evaluation.course_start_date
    eval_start = evaluation.eval_start_date
    return eval_start + timedelta(days=20) if (eval_start - course_start).days > 90 else eval_start + timedelta(days=13)


def row_eval_start_from_course_end(evaluation):
    course_end = evaluation.course_end_date
    course_start = evaluation.course_start_date
    return course_end - timedelta(days=20) if (course_end - course_start).days > 90 else course_end - timedelta(days=13)


def calculate_eval_dates(evals):
    for e in evals:
        e.eval_end_date = row_eval_end_from_eval_start(e) if e.eval_start_date else e.course_end_date
        e.eval_start_date = e.eval_start_date or row_eval_start_from_course_end(e)


def result_row_to_eval(row, term, dept):
    listings = row_x_listings(row)
    shares = row_room_shares(row)
    for i in listings:
        if i in shares:
            shares.remove(i)

    dept_form = row_data(row, 'dept_form')
    eval_type = row_data(row, 'eval_type')
    status = row_data(row, 'status')
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
        'course_start_date': course_start,
        'course_end_date': course_end,
        'eval_start_date': eval_start,
        'eval_end_date': eval_end,
    }
    return Evaluation(eval_data)


def result_to_evals(result, evaluations, term, dept):
    for row in result:
        evaluations.append(result_row_to_eval(row, term, dept))


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
               unholy_loch.sis_sections.instructor_uid AS uid,
               unholy_loch.sis_sections.instructor_role_code AS instructor_role,
               unholy_loch.sis_sections.meeting_start_date AS course_start_date,
               unholy_loch.sis_sections.meeting_end_date AS course_end_date
          FROM supplemental_sections
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.course_number = supplemental_sections.course_number
         WHERE supplemental_sections.department_id = '{dept.dept_id}'
           AND supplemental_sections.term_id = '{term.term_id}'
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
               evaluations.instructor_uid AS uid,
               unholy_loch.sis_sections.instructor_role_code AS instructor_role,
               evaluations.start_date AS eval_start_date,
               evaluations.end_date AS eval_end_date,
               evaluations.status AS status,
               evaluations.department_form_id AS dept_form,
               evaluation_types.name AS eval_type
          FROM evaluations
          JOIN unholy_loch.sis_sections
            ON unholy_loch.sis_sections.course_number = evaluations.course_number
     LEFT JOIN evaluation_types
            ON evaluation_types.id = evaluations.evaluation_type_id
         WHERE evaluations.term_id = '{term.term_id}'
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
            if e.ccn == edit.ccn and e.instructor and e.instructor.uid == uid:
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
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email_address'],
                'affiliations': row['affiliations'],
            }))

        for e in evals:
            for i in instructors:
                if e.instructor and e.instructor.uid == i.uid:
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
    return get_dept(result['dept_name'], all_users)


def get_eval_types(evals):
    for e in evals:
        if e.eval_type or e.dept.dept_id == '92':
            app.logger.info('Skipping eval type')
        else:
            app.logger.info(f'Checking eval {vars(e)}')
            app.logger.info(f'Instructor is {vars(e.instructor)}')
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


# TEST DATA


def reset_test_data(term, dept):
    sql = f"DELETE FROM evaluations WHERE term_id = '{term.term_id}' AND department_id = {dept.dept_id}"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    sql = f"DELETE FROM supplemental_sections WHERE term_id = '{term.term_id}' AND department_id = {dept.dept_id}"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    sql = 'DELETE FROM supplemental_instructors'
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    sql = "DELETE FROM department_forms WHERE name LIKE 'Form %'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    sql = "DELETE FROM evaluation_types WHERE name LIKE 'Type %'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

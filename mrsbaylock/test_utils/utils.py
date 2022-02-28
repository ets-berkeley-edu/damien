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
import re

from damien import db, std_commit
from flask import current_app as app
from mrsbaylock.models.department import Department
from mrsbaylock.models.evaluation import Evaluation
from mrsbaylock.models.user import User
from sqlalchemy import text


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


def default_download_dir():
    return f'{app.config["BASE_DIR"]}/mrsbaylock/downloads'


# DATABASE - USERS


def get_user(uid):
    sql = f"SELECT * FROM users WHERE uid = '{uid}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(f'{result}')
    data = {
        'uid': uid,
        'csid': result['csid'],
        'first_name': result['first_name'],
        'last_name': result['last_name'],
        'email': result['email'],
        'is_admin': result['is_admin'],
        'receives_comms': result['can_receive_communications'],
        'views_response_rates': result['can_view_response_rates'],
    }
    return User(data)


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
            'id': row['id'],
            'name': row['dept_name'],
            'participating': True,
        }
        depts.append(Department(data))
    return depts


def get_dept_users(dept):
    sql = f"""
        SELECT users.id,
               users.uid,
               users.csid,
               users.first_name,
               users.last_name,
               users.email,
               users.can_receive_communications,
               users.can_view_response_rates
          FROM users
          JOIN department_members ON department_members.user_id = users.id
          JOIN departments ON departments.id = department_members.department_id
         WHERE departments.id = '{dept.dept_id}';
    """
    app.logger.info(sql)
    users = []
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in result:
        user_data = {
            'id': row['id'],
            'uid': row['uid'],
            'csid': row['csid'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'receives_comms': row['can_receive_communications'],
            'views_response_rates': row['can_view_response_rates'],
        }
        user = User(user_data)
        users.append(user)
    return users


def get_dept(name):
    sql = f"""
        SELECT id,
               is_enrolled,
               note
          FROM departments
         WHERE dept_name = '{name}';
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(result)
    dept_data = {
        'id': result['id'],
        'name': name,
        'participating': result['is_enrolled'],
        'note': result['note'],
    }
    dept = Department(dept_data)
    dept.users = get_dept_users(dept)
    return dept


def delete_dept_note(dept):
    sql = f'UPDATE departments SET note = NULL WHERE id = {dept.dept_id};'
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    dept.note = None


# SECTIONS


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
    subject_str = ''
    for subject in subjects:
        subject_str += f'\'{subject}\', '

    clause = '' if '' in dept_subjects else ' AND unholy_loch.sis_sections.subject_area = department_catalog_listings.subject_area'
    sql = f"""
        SELECT DISTINCT unholy_loch.sis_sections.course_number AS ccn,
                        unholy_loch.sis_sections.subject_area AS subject,
                        unholy_loch.sis_sections.catalog_id AS catalog_id,
                        unholy_loch.sis_sections.instruction_format AS instruction_format,
                        unholy_loch.sis_sections.instructor_uid AS uid,
                        unholy_loch.sis_sections.instructor_role_code AS instructor_role,
                        unholy_loch.sis_sections.meeting_start_date AS start_date,
                        unholy_loch.sis_sections.meeting_end_date AS end_date,
                        department_forms.name AS dept_form
                   FROM departments
                   JOIN unholy_loch.sis_sections
                     ON unholy_loch.sis_sections.subject_area IN ({subject_str[:-2]})
                   JOIN department_catalog_listings
                     ON department_catalog_listings.department_id = departments.id{clause}
                   JOIN department_forms
                     ON department_forms.id = department_catalog_listings.default_form_id
                  WHERE departments.id = '{dept.dept_id}'
                    AND unholy_loch.sis_sections.term_id = '{term.id}'
                    AND unholy_loch.sis_sections.enrollment_count > 0
                    AND (unholy_loch.sis_sections.instructor_role_code IS NULL
                     OR unholy_loch.sis_sections.instructor_role_code !='ICNT')
                    AND	unholy_loch.sis_sections.instruction_format NOT IN ('CLC', 'GRP', 'IND', 'SUP', 'VOL');
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
    return evals_total


def result_to_evals(result, evaluations, term, dept):
    for row in result:
        eval_data = {
            'term': term,
            'dept': dept,
            'dept_form': row['dept_form'],
            'ccn': row['ccn'],
            'uid': row['uid'],
            'instructor_role': row['instructor_role'],
            'subject': row['subject'],
            'catalog_id': row['catalog_id'],
            'instruction_format': row['instruction_format'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
        }
        evaluation = Evaluation(eval_data)
        evaluations.append(evaluation)


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

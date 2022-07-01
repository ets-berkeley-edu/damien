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
import itertools

from damien import db, std_commit
from flask import current_app as app
from mrsbaylock.models.department import Department
from mrsbaylock.models.department_form import DepartmentForm
from mrsbaylock.models.department_note import DepartmentNote
from mrsbaylock.models.term import Term
from mrsbaylock.models.user import User
from mrsbaylock.models.user_dept_role import UserDeptRole
from mrsbaylock.test_utils import evaluation_utils
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


def get_test_dept_contact_uid():
    return app.config['TEST_DEPT_CONTACT_UID']


def get_test_email_account():
    return app.config['TEST_EMAIL']


def default_download_dir():
    return f'{app.config["BASE_DIR"]}/mrsbaylock/tmp'


def get_current_term():
    return Term(
        term_id=app.config['CURRENT_TERM_ID'],
        name=app.config['CURRENT_TERM_NAME'],
        prefix=app.config['CURRENT_TERM_PREFIX'],
        start_date=datetime.strptime(app.config['CURRENT_TERM_BEGIN'], '%Y-%m-%d'),
        end_date=datetime.strptime(app.config['CURRENT_TERM_END'], '%Y-%m-%d'),
    )


def get_previous_term_code(current_term_id):
    d1 = '2'
    d2_3 = str(int(current_term_id[1:3]) - 1) if (current_term_id[-1] == '2') else current_term_id[1:3]
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


def get_test_dept_1(all_contacts=None):
    name = app.config['TEST_DEPT_1']
    return get_dept(name, all_contacts)


def get_test_dept_2(all_contacts=None):
    name = app.config['TEST_DEPT_2']
    return get_dept(name, all_contacts)


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


# TEST DATA


def reset_test_data(term, dept=None):
    dept_clause = f'AND department_id = {dept.dept_id}' if dept else ''

    sql = f"DELETE FROM evaluations WHERE term_id = '{term.term_id}'{dept_clause}"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    sql = f"DELETE FROM supplemental_sections WHERE term_id = '{term.term_id}'{dept_clause}"
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


# CSV DATA


def verify_actual_matches_expected(actual, expected):
    unexpected = [x for x in actual if x not in expected]
    missing = [x for x in expected if x not in actual]
    app.logger.info(f'Unexpected {unexpected}')
    app.logger.info(f'Missing {missing}')
    assert not unexpected
    assert not missing
    expected = list(map(dict, set(tuple(sorted(i.items())) for i in expected)))
    app.logger.info(f'Expecting {len(expected)} rows, got {len(actual)}')
    assert len(actual) == len(expected)


def expected_courses(evaluations):
    term = get_current_term()
    courses = []
    for row in evaluations:
        eval_types = [e.eval_type for e in evaluations if e.ccn == row.ccn]
        suffix = '_GSI' if 'F' in eval_types and 'G' in eval_types and row.eval_type == 'G' else ''
        gsi = ' (EVAL FOR GSI)' if suffix else ''
        if row.x_listing_ccns:
            flag = 'Y'
            ccns = []
            ccns.extend(row.x_listing_ccns)
            ccns.append(row.ccn)
            ccns.sort()
            x_listed_name = '-'.join(ccns)
        elif row.room_share_ccns:
            flag = 'RM SHARE'
            ccns = []
            ccns.extend(row.room_share_ccns)
            ccns.append(row.ccn)
            ccns.sort()
            x_listed_name = '-'.join(row.room_share_ccns)
        else:
            flag = ''
            x_listed_name = ''
        modular = 'Y' if (term.start_date != row.course_start_date or term.end_date != row.course_end_date) else 'N'
        if row.eval_end_date:
            end_date = row.eval_end_date.strftime('%-m/%-d/%y')
        else:
            eval_end = evaluation_utils.row_eval_end_from_eval_start(row.course_end_date, row.course_start_date)
            if eval_end:
                end_date = eval_end.strftime('%-m/%-d/%y')
            else:
                end_date = ''
        data = {
            # TODO - COURSE_ID acct for dupes
            'COURSE_ID': f'{term.prefix}-{row.ccn}{suffix}',
            'COURSE_ID_2': f'{term.prefix}-{row.ccn}{suffix}',
            'COURSE_NAME': f'{row.subject} {row.catalog_id} {row.instruction_format} {row.section_num} {row.title}{gsi}',
            'CROSS_LISTED_FLAG': flag,
            'CROSS_LISTED_NAME': x_listed_name,
            'DEPT_NAME': row.subject,
            'CATALOG_ID': row.catalog_id,
            'INSTRUCTION_FORMAT': row.instruction_format,
            'SECTION_NUM': row.section_num,
            'PRIMARY_SECONDARY_CD': ('P' if row.primary else 'S'),
            'EVALUATE': 'Y',
            'DEPT_FORM': row.dept_form,
            'EVALUATION_TYPE': row.eval_type,
            'MODULAR_COURSE': modular,
            'START_DATE': (row.eval_start_date.strftime('%-m/%-d/%y') if row.eval_start_date else ''),
            'END_DATE': end_date,
            'CANVAS_COURSE_ID': '',
            'QB_MAPPING': f'{row.dept_form}-{row.eval_type}',
        }
        courses.append(data)
    return courses


def expected_course_students(evaluations):
    ccns = "', '".join(e.ccn for e in evaluations)
    term = get_current_term()
    sql = f"""
        SELECT ldap_uid, course_number
          FROM unholy_loch.sis_enrollments
         WHERE unholy_loch.sis_enrollments.term_id = '{term.term_id}'
           AND unholy_loch.sis_enrollments.course_number IN('{ccns}')
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    enrollments = []
    for row in result:
        data = {
            'COURSE_ID': f'{term.prefix}-{row["course_number"]}',
            'LDAP_UID': row['ldap_uid'],
        }
        enrollments.append(data)

        eval_types = [e.eval_type for e in evaluations if e.ccn == row['course_number']]
        if 'F' in eval_types and 'G' in eval_types:
            gsi_data = {
                'COURSE_ID': f'{term.prefix}-{row["course_number"]}_GSI',
                'LDAP_UID': row['ldap_uid'],
            }
            enrollments.append(gsi_data)
    return enrollments


def expected_instructors(evaluations):
    instructors = []
    for row in evaluations:
        if row.instructor.uid:
            data = {
                'LDAP_UID': row.instructor.uid,
                'SIS_ID': row.instructor.csid or f'UID:{row.instructor.uid}',
                'FIRST_NAME': row.instructor.first_name,
                'LAST_NAME': row.instructor.last_name,
                'EMAIL_ADDRESS': row.instructor.email,
                'BLUE_ROLE': '23',
            }
            instructors.append(data)
    return {v['LDAP_UID']: v for v in instructors}.values()


def expected_course_instructors(evaluations):
    term = get_current_term()
    instructors = []
    for row in evaluations:
        eval_types = [e.eval_type for e in evaluations if e.ccn == row.ccn]
        suffix = '_GSI' if 'F' in eval_types and 'G' in eval_types and row.eval_type == 'G' else ''
        data = {
            'COURSE_ID': f'{term.prefix}-{row.ccn}{suffix}',
            'LDAP_UID': row.instructor.uid,
            'ROLE': 'Faculty' if row.eval_type == 'F' else 'GSI' if row.eval_type == 'G' else row.eval_type,
        }
        instructors.append(data)
    return instructors


def expected_supervisors():
    sql = """
        SELECT users.id,
               users.uid,
               users.csid,
               users.first_name,
               users.last_name,
               users.email,
               users.blue_permissions,
               department_members.can_receive_communications,
               ARRAY_TO_STRING(ARRAY_AGG(DISTINCT department_forms.name), ',') AS forms
          FROM users
     LEFT JOIN department_members ON department_members.user_id = users.id
     LEFT JOIN departments ON departments.id = department_members.department_id
     LEFT JOIN user_department_forms ON user_department_forms.user_id = users.id
     LEFT JOIN department_forms ON department_forms.id = user_department_forms.department_form_id
         WHERE users.is_admin IS FALSE
      GROUP BY users.id, users.uid, users.csid, users.first_name, users.last_name, users.blue_permissions,
               department_members.can_receive_communications
      ORDER BY users.uid
    """
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    supervisors = []
    for row in result:
        forms = row['forms'].split(',')
        forms.sort()
        data = {
            'LDAP_UID': row['uid'],
            'SIS_ID': (row['csid'] or f"UID:{row['uid']}"),
            'FIRST_NAME': row['first_name'],
            'LAST_NAME': row['last_name'],
            'EMAIL_ADDRESS': row['email'],
            'SUPERVISOR_GROUP': 'DEPT_ADMIN',
            'PRIMARY_ADMIN': ('Y' if row['blue_permissions'] == 'response_rates' else ''),
            'SECONDARY_ADMIN': '',
            'DEPTS': [i for i in forms if i],
        }
        supervisors.append(data)
    return supervisors


def expected_course_supervisors(evaluations, all_contacts):
    term = get_current_term()
    forms_per_uid = []
    for contact in all_contacts:
        forms = list(map(lambda f: f.name, contact.dept_forms))
        forms_per_uid.append({'uid': contact.uid, 'forms': forms})

    supervisors = []
    for row in evaluations:
        eval_types = [e.eval_type for e in evaluations if e.ccn == row.ccn]
        suffix = '_GSI' if 'F' in eval_types and 'G' in eval_types and row.eval_type == 'G' else ''
        for uid in forms_per_uid:
            if row.dept_form in uid['forms']:
                data = {
                    'COURSE_ID': f'{term.prefix}-{row.ccn}{suffix}',
                    'LDAP_UID': uid['uid'],
                    'DEPT_NAME': row.dept_form,
                }
                supervisors.append(data)
    return supervisors


def expected_dept_hierarchy():
    forms = list(map(lambda f: f.name, evaluation_utils.get_all_dept_forms()))
    rows = [{
        'NODE_ID': 'UC Berkeley',
        'NODE_CAPTION': 'UC Berkeley',
        'PARENT_NODE_ID': '',
        'PARENT_NODE_CAPTION': '',
        'LEVEL': '1',
    }]
    for form in forms:
        rows.append({
            'NODE_ID': form,
            'NODE_CAPTION': form,
            'PARENT_NODE_ID': 'UC Berkeley',
            'PARENT_NODE_CAPTION': 'UC Berkeley',
            'LEVEL': '2',
        })
    return rows

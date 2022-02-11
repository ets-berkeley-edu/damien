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

from damien import db, std_commit
from flask import current_app as app
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
            csid, uid, first_name, last_name, email, is_admin, can_receive_communications, can_view_response_rates,
            created_at, updated_at
        )
        SELECT
            '{user.csid}', '{user.uid}', '{user.first_name}', '{user.last_name}', '{user.email}', TRUE, TRUE, TRUE,
            NOW(), NOW()
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

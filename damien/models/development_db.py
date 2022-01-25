"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from damien.models.user import User
from flask import current_app as app
from sqlalchemy.sql import text


_test_users = [
    {
        'csid': '100100100',
        'uid': '100',
        'first_name': 'Father',
        'last_name': 'Brennan',
        'email': 'fatherbrennan@berkeley.edu',
    },
    {
        'csid': '200200200',
        'uid': '200',
        'first_name': 'Father',
        'last_name': 'Spiletto',
        'email': 'fatherspiletto@berkeley.edu',
        'is_admin': True,
    },
]


def clear():
    with open(app.config['BASE_DIR'] + '/scripts/db/drop_schema.sql', 'r') as ddlfile:
        db.session().execute(text(ddlfile.read()))
        std_commit()
    db.session().execute(text('DROP SCHEMA IF EXISTS unholy_loch CASCADE'))
    std_commit()


def load():
    _load_schemas()
    _create_users()
    return db


def _create_users():
    for test_user in _test_users:
        db.session.add(User(**test_user))
    std_commit(allow_test_environment=True)


def _load_schemas():
    """Create DB schema from SQL file."""
    for schema in ['schema', 'unholy_loch', 'populate_departments']:
        with open(app.config['BASE_DIR'] + f'/scripts/db/{schema}.sql', 'r') as ddlfile:
            db.session().execute(text(ddlfile.read()))
            std_commit()

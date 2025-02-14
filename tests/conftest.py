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

import json
import os

from flask_login import logout_user
import pytest  # noqa
import damien.factory  # noqa
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tests.util import override_config

os.environ['DAMIEN_ENV'] = 'test'  # noqa


class FakeAuth(object):
    def __init__(self, the_app, the_client):
        self.app = the_app
        self.client = the_client

    def login(self, uid):
        with override_config(self.app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {
                'uid': uid,
                'password': self.app.config['DEVELOPER_AUTH_PASSWORD'],
            }
            self.client.post(
                '/api/auth/dev_auth_login',
                data=json.dumps(params),
                content_type='application/json',
            )


# Because app and db fixtures are only created once per pytest run, individual tests
# are not able to modify application configuration values before the app is created.
# Per-test customizations could be supported via a fixture scope of 'function' and
# the @pytest.mark.parametrize annotation.

@pytest.fixture(scope='session')
def app(request):
    """Fixture application object, shared by all tests."""
    _app = damien.factory.create_app()

    # Create app context before running tests.
    ctx = _app.app_context()
    ctx.push()

    # Pop the context after running tests.
    def teardown():
        ctx.pop()
    request.addfinalizer(teardown)

    return _app


# TODO Perform DB schema creation and deletion outside an app context, enabling test-specific app configurations.
@pytest.fixture(scope='session')
def db(app):
    """Fixture database object, shared by all tests."""
    from damien.models import development_db
    # Drop all tables before re-loading the schemas.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    _db = development_db.load()

    return _db


@pytest.fixture(scope='function', autouse=True)
def db_session(db):
    """Fixture database session used for the scope of a single test.

    All executions are wrapped in a session and then rolled back to keep individual tests isolated.
    """
    # Mixing SQL-using test fixtures with SQL-using decorators seems to cause timing issues with pytest's
    # fixture finalizers. Instead of using a finalizer to roll back the session and close connections,
    # we begin by cleaning up any previous invocations.
    # This fixture is marked 'autouse' to ensure that cleanup happens at the start of every test, whether
    # or not it has an explicit database dependency.
    db.session.rollback()
    try:
        bind = db.session.get_bind()
        if isinstance(bind, Engine):
            bind.dispose()
        else:
            bind.close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except TypeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    _session = scoped_session(sessionmaker(bind=connection))
    db.session = _session

    return _session


@pytest.fixture(scope='function', autouse=True)
def cache_session():
    from damien import cache
    cache.clear()


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    yield FakeAuth(app, client)
    logout_user()


@pytest.fixture(scope='session')
def form_history_id(app, db):
    from damien.models.department_form import DepartmentForm
    return DepartmentForm.find_by_name('HISTORY').id


@pytest.fixture(scope='session')
def form_melc_id(app, db):
    from damien.models.department_form import DepartmentForm
    return DepartmentForm.find_by_name('MELC').id


@pytest.fixture(scope='session')
def type_f_id(app, db):
    from damien.models.evaluation_type import EvaluationType
    return EvaluationType.find_by_name('F').id


@pytest.fixture(scope='session')
def type_g_id(app, db):
    from damien.models.evaluation_type import EvaluationType
    return EvaluationType.find_by_name('G').id


@pytest.fixture(scope='session')
def history_id(app, db):
    from damien.models.department import Department
    return Department.find_by_name('History').id


@pytest.fixture(scope='session')
def melc_id(app, db):
    from damien.models.department import Department
    return Department.find_by_name('Middle Eastern Languages and Cultures').id

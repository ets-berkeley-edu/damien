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

from damien import __version__ as version
from damien import db
from damien.externals.b_connected import BConnected
from damien.externals.sftp import get_sftp_client
from damien.lib.http import tolerant_jsonify
from flask import current_app as app
import psycopg2
from sqlalchemy.exc import SQLAlchemyError


@app.route('/api/ping')
def ping():
    b_connected_ping = False
    db_ping = False
    try:
        b_connected_ping = BConnected().ping()
        db_ping = _db_status()
        explorance_ping = _explorance_status()
    except Exception as e:
        app.logger.error(f'Error during /api/ping: {e}')
        app.logger.exception(e)
    finally:
        return tolerant_jsonify(
            {
                'app': True,
                'bConnected': b_connected_ping,
                'db': db_ping,
                'explorance': explorance_ping,
            },
        )


@app.route('/api/version')
def app_version():
    v = {
        'version': version,
    }
    build_stats = load_json('config/build-summary.json')
    if build_stats:
        v.update(build_stats)
    else:
        v.update({
            'build': None,
        })
    return tolerant_jsonify(v)


def load_json(relative_path):
    try:
        file = open(app.config['BASE_DIR'] + '/' + relative_path)
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


def _db_status():
    sql = 'SELECT 1'
    try:
        db.session.execute(sql)
        return True
    except psycopg2.Error as e:
        error_str = str(e)
        if e.pgcode:
            error_str += f'{e.pgcode}: {e.pgerror}\n'
        error_str += f'on SQL: {sql}'
        app.logger.warning(error_str)
        return False
    except SQLAlchemyError as e:
        app.logger.error('Database connection error during /api/ping')
        app.logger.exception(e)
        return False


def _explorance_status():
    try:
        get_sftp_client()
        return True
    except Exception as e:
        app.logger.error('SFTP connection error during /api/ping')
        app.logger.exception(e)
        return False

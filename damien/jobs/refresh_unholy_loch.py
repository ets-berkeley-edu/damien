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

import os
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from damien import cache, db, std_commit
from damien.lib.queries import refresh_additional_instructors
from damien.lib.util import resolve_sql_template
from sqlalchemy.sql import text


def initialize_refresh_schedule(app):
    if app.config['SCHEDULE_LOCH_REFRESH']:
        scheduler = BackgroundScheduler()

        @scheduler.scheduled_job('cron', id='refresh_unholy_loch', **app.config['SCHEDULE_LOCH_REFRESH'])
        def scheduled_refresh():
            _refresh_unholy_loch(app)

        scheduler.start()


def refresh_from_api():
    from flask import current_app as app
    app_arg = app._get_current_object()
    return _refresh_unholy_loch(app_arg)


def _refresh_unholy_loch(app):
    with app.app_context():
        if os.environ.get('DAMIEN_ENV') in ['test', 'testext']:
            app.logger.info('Test run in progress; will not muddy the waters by actually kicking off a background thread.')
            return True
        else:
            app.logger.info('About to start background thread.')
            thread = Thread(target=_bg_refresh_unholy_loch, args=[app], daemon=True)
            thread.start()
            return True


def _bg_refresh_unholy_loch(app):
    with app.app_context():
        app.logger.info('Starting unholy loch refresh...')
        try:
            template_sql = 'refresh_unholy_loch.template.sql'
            resolved_ddl = resolve_sql_template(template_sql, term_id=app.config['CURRENT_TERM_ID'])
            db.session().execute(text(resolved_ddl))
            refresh_additional_instructors()
            std_commit()
            cache.clear()
            app.logger.info('Unholy loch refresh completed, cache cleared.')
        except Exception as e:
            app.logger.error('Unholy loch refresh failed:')
            app.logger.exception(e)

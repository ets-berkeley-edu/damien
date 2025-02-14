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

from datetime import datetime
import os
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from damien import cache, db, std_commit
from damien.externals.s3 import get_s3_path
from damien.lib.berkeley import get_current_term_id, get_refreshable_term_ids
from damien.lib.exporter import generate_exports
from damien.lib.queries import refresh_additional_instructors
from damien.lib.util import resolve_sql_template
from damien.models.department import Department
from damien.models.export import Export
from damien.models.tool_setting import ToolSetting
from damien.models.util import advisory_lock, get_granted_lock_ids
from sqlalchemy.sql import text


LOCH_REFRESH_LOCK_ID = 666


def initialize_refresh_schedule(app):
    if app.config['SCHEDULE_LOCH_REFRESH']:
        scheduler = BackgroundScheduler()

        @scheduler.scheduled_job(
            'cron',
            id='refresh_unholy_loch',
            max_instances=1,
            **app.config['SCHEDULE_LOCH_REFRESH'],
            timezone=app.config['TIMEZONE'],
        )
        def scheduled_refresh():
            _refresh_unholy_loch(app, publish_before_refresh=True)

        scheduler.start()


def is_refreshing():
    lock_ids = get_granted_lock_ids()
    return (LOCH_REFRESH_LOCK_ID in lock_ids)


def refresh_from_api():
    from flask import current_app as app
    app_arg = app._get_current_object()
    return _refresh_unholy_loch(app_arg, publish_before_refresh=False)


def _refresh_unholy_loch(app, publish_before_refresh=False):
    with app.app_context():
        if os.environ.get('DAMIEN_ENV') in ['test', 'testext']:
            app.logger.info('Test run in progress; will not muddy the waters by actually kicking off a background thread.')
            return True
        else:
            app.logger.info('About to start background thread.')
            thread = Thread(target=_bg_refresh_unholy_loch, name='refresh_unholy_loch', args=[app, publish_before_refresh], daemon=True)
            thread.start()
            return True


def _bg_refresh_unholy_loch(app, publish_before_refresh=False):
    with app.app_context():
        with advisory_lock(LOCH_REFRESH_LOCK_ID) as has_lock:
            if not has_lock:
                return

            if publish_before_refresh and ToolSetting.get_tool_setting_boolean('AUTO_PUBLISH_ENABLED'):
                app.logger.info('Starting automatic publication...')

                term_id = get_current_term_id()
                timestamp = datetime.now()

                try:
                    generate_exports(term_id, timestamp)
                    app.logger.info('Automatic publication complete.')
                except Exception as e:
                    app.logger.error('Automatic publication failed.')
                    app.logger.exception(e)
                    Export.update_status(get_s3_path(term_id, timestamp), 'error')

            app.logger.info('Starting unholy loch refresh...')

            try:
                template_sql = 'refresh_unholy_loch.template.sql'
                cache.delete('current_term_id')
                term_ids = get_refreshable_term_ids()
                for term_id in term_ids:
                    app.logger.debug(f'Refreshing unholy loch term {term_id}.')
                    resolved_ddl = resolve_sql_template(template_sql, term_id=term_id)
                    db.session().execute(text(resolved_ddl))
                    refresh_additional_instructors()
                    std_commit()

                    # Pre-populate term cache by generating full evaluation feeds for all departments.
                    department_ids = [d.id for d in Department.all_enrolled()]
                    for dept_id in department_ids:
                        d = Department.find_by_id(dept_id)
                        d.evaluations_feed(term_id=term_id)

                    app.logger.info(f'Term {term_id} refreshed.')

                app.logger.info(f"Unholy loch refresh completed (term_ids={','.join(term_ids)}), cache refreshed.")

            except Exception as e:
                app.logger.error('Unholy loch refresh failed:')
                app.logger.exception(e)

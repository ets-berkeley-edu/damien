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

from datetime import date, timedelta

from damien import cache
from damien.models.util import select_column
from flask import current_app as app


def available_term_ids():
    return term_ids_range(app.config['EARLIEST_TERM_ID'], get_current_term_id())


def get_current_term_id():
    if app.config['CURRENT_TERM_ID'] == 'auto':
        current_term_id = cache.get('current_term_id')
        if not current_term_id:
            # Auto-configured terms roll over in advance of the term start date.
            term_start_cutoff = date.today() + timedelta(days=app.config['TERM_TRANSITION_ADVANCE_DAYS'])
            current_term_id = select_column(f"""
                SELECT term_id from unholy_loch.sis_terms
                WHERE term_begins <= '{term_start_cutoff.strftime('%Y-%m-%d')}'
                ORDER BY term_id DESC
                LIMIT 1""")[0]
            cache.set('current_term_id', current_term_id)
        return current_term_id
    else:
        return app.config['CURRENT_TERM_ID']


def get_refreshable_term_ids():
    current_term_id = get_current_term_id()
    term_in_progress_result = select_column(f"""
        SELECT term_id from unholy_loch.sis_terms
        WHERE term_begins <= '{date.today().strftime('%Y-%m-%d')}'
        AND term_ends >= '{date.today().strftime('%Y-%m-%d')}'""")
    if term_in_progress_result and term_in_progress_result[0] < current_term_id:
        return term_ids_range(term_in_progress_result[0], current_term_id)
    else:
        return [current_term_id]


def term_ids_range(earliest_term_id, latest_term_id):
    """Return SIS ID of each term in the range, from oldest to newest."""
    term_id = int(earliest_term_id)
    ids = []
    while term_id <= int(latest_term_id):
        ids.append(str(term_id))
        term_id += 4 if (term_id % 10 == 8) else 3
    return ids


def term_code_for_sis_id(sis_id=None):
    if sis_id:
        sis_id = str(sis_id)
        season_codes = {
            '0': 'A',
            '2': 'B',
            '5': 'C',
            '8': 'D',
        }
        year = f'19{sis_id[1:3]}' if sis_id.startswith('1') else f'20{sis_id[1:3]}'
        return f'{year}-{season_codes[sis_id[3:4]]}'


def term_name_for_sis_id(sis_id=None):
    if sis_id:
        sis_id = str(sis_id)
        season_codes = {
            '0': 'Winter',
            '2': 'Spring',
            '5': 'Summer',
            '8': 'Fall',
        }
        year = f'19{sis_id[1:3]}' if sis_id.startswith('1') else f'20{sis_id[1:3]}'
        return f'{season_codes[sis_id[3:4]]} {year}'

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

from damien.lib.berkeley import available_term_ids, current_term_dates, term_name_for_sis_id
from damien.lib.http import tolerant_jsonify
from damien.lib.util import safe_strftime
from flask import current_app as app


@app.route('/api/config')
def app_config():
    def _term_feed(term_id):
        return {'id': term_id, 'name': term_name_for_sis_id(term_id)}
    term_begin, term_end = current_term_dates()
    return tolerant_jsonify({
        'availableTerms': [_term_feed(term_id) for term_id in available_term_ids()],
        'currentTermDates': {
            'begin': safe_strftime(term_begin, '%Y-%m-%d'),
            'end': safe_strftime(term_end, '%Y-%m-%d'),
        },
        'currentTermId': app.config['CURRENT_TERM_ID'],
        'damienEnv': app.config['DAMIEN_ENV'],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'easterEggMonastery': app.config['EASTER_EGG_MONASTERY'],
        'easterEggNannysRoom': app.config['EASTER_EGG_NANNYSROOM'],
        'ebEnvironment': app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None,
        'emailSupport': app.config['EMAIL_COURSE_EVALUATION_ADMIN'],
        'emailTestMode': app.config['EMAIL_TEST_MODE'],
        'timezone': app.config['TIMEZONE'],
    })

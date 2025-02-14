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

from damien.api.errors import BadRequestError
from damien.api.util import admin_required
from damien.lib.berkeley import available_term_ids, get_current_term_id, term_name_for_sis_id
from damien.lib.http import tolerant_jsonify
from damien.lib.queries import get_default_meeting_dates, get_valid_meeting_dates
from damien.lib.util import safe_strftime, to_bool_or_none
from damien.models.department_form import DepartmentForm
from damien.models.evaluation_type import EvaluationType
from damien.models.tool_setting import ToolSetting
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/config')
def app_config():
    def _term_feed(term_id, default_meeting_dates, valid_meeting_dates):
        if not (default_meeting_dates and valid_meeting_dates):
            app.logger.warning(f'No meeting dates found for term_id {term_id}')
            return {
                'id': term_id,
                'name': term_name_for_sis_id(term_id),
            }
        return {
            'id': term_id,
            'name': term_name_for_sis_id(term_id),
            'defaultDates': {
                'begin': safe_strftime(default_meeting_dates['start_date'], '%Y-%m-%d'),
                'end': safe_strftime(default_meeting_dates['end_date'], '%Y-%m-%d'),
            },
            'validDates': {
                'begin': safe_strftime(valid_meeting_dates['start_date'], '%Y-%m-%d'),
                'end': safe_strftime(valid_meeting_dates['end_date'], '%Y-%m-%d'),
            },
        }

    term_ids = available_term_ids()
    current_term_id = get_current_term_id()
    default_meeting_dates = {row['term_id']: row for row in get_default_meeting_dates(term_ids)}
    valid_meeting_dates = {row['term_id']: row for row in get_valid_meeting_dates(term_ids)}

    department_forms = DepartmentForm.query.order_by(DepartmentForm.name).all()
    evaluation_types = EvaluationType.query.filter_by(deleted_at=None).order_by(EvaluationType.name).all()
    # Force 'F' and 'G' to sort to the top of the list.
    evaluation_types = sorted(evaluation_types, key=lambda e: {'F': '0', 'G': '00'}.get(e.name, e.name))

    return tolerant_jsonify({
        'availableTerms': [_term_feed(
            term_id,
            default_meeting_dates.get(term_id),
            valid_meeting_dates.get(term_id),
        ) for term_id in term_ids],
        'currentTermId': current_term_id,
        'currentTermName': term_name_for_sis_id(current_term_id),
        'damienEnv': app.config['DAMIEN_ENV'],
        'departmentForms': [d.to_api_json() for d in department_forms],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'easterEggMonastery': app.config['EASTER_EGG_MONASTERY'],
        'easterEggNannysRoom': app.config['EASTER_EGG_NANNYSROOM'],
        'ebEnvironment': app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None,
        'emailSupport': app.config['EMAIL_COURSE_EVALUATION_ADMIN'],
        'emailTestMode': app.config['EMAIL_TEST_MODE'],
        'evaluationTypes': [e.to_api_json() for e in evaluation_types],
        'scheduleLochRefresh': app.config['SCHEDULE_LOCH_REFRESH'],
        'timezone': app.config['TIMEZONE'],
    })


@app.route('/api/auto_publish')
@admin_required
def get_auto_publish_enabled():
    enabled = ToolSetting.get_tool_setting_boolean('AUTO_PUBLISH_ENABLED')
    return tolerant_jsonify({'enabled': enabled})


@app.route('/api/auto_publish/update', methods=['POST'])
@admin_required
def set_auto_publish_enabled():
    params = request.get_json()
    enabled = to_bool_or_none(params.get('enabled'))
    if enabled is None:
        raise BadRequestError('API requires \'enabled\'')
    ToolSetting.upsert('AUTO_PUBLISH_ENABLED', enabled)
    return tolerant_jsonify({'enabled': enabled})


@app.route('/api/service_announcement')
@login_required
def get_service_announcement():
    announcement = _get_service_announcement()
    return tolerant_jsonify(announcement if current_user.is_admin or announcement['isLive'] else None)


@app.route('/api/service_announcement/update', methods=['POST'])
@admin_required
def update_service_announcement():
    params = request.get_json()
    text = params.get('text')
    is_live = to_bool_or_none(params.get('isLive'))
    if not text or is_live is None:
        raise BadRequestError('API requires \'text\' and \'isLive\'')
    _update_service_announcement(text, is_live)
    return tolerant_jsonify(_get_service_announcement())


def _get_service_announcement():
    is_live = ToolSetting.get_tool_setting_boolean('SERVICE_ANNOUNCEMENT_IS_LIVE')
    return {
        'text': ToolSetting.get_tool_setting('SERVICE_ANNOUNCEMENT_TEXT'),
        'isLive': is_live,
    }


def _update_service_announcement(text, is_live):
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_TEXT', text)
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_IS_LIVE', is_live)

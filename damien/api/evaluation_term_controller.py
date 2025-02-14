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
from damien.lib.berkeley import available_term_ids, get_current_term_id
from damien.lib.http import tolerant_jsonify
from damien.lib.util import get as get_param
from damien.models.evaluation_term import EvaluationTerm
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/evaluation_term/<term_id>')
@login_required
def get_evaluation_term(term_id):
    _validate(term_id)
    evaluation_term = EvaluationTerm.find_or_create(term_id)
    return tolerant_jsonify(evaluation_term.to_api_json())


@app.route('/api/evaluation_term/lock', methods=['POST'])
@admin_required
def lock_evaluation_term():
    term_id = get_param(request.get_json(), 'termId', get_current_term_id())
    _validate(term_id)
    evaluation_term = EvaluationTerm.lock(term_id, current_user.get_uid())
    return tolerant_jsonify(evaluation_term.to_api_json())


@app.route('/api/evaluation_term/unlock', methods=['POST'])
@admin_required
def unlock_evaluation_term():
    term_id = get_param(request.get_json(), 'termId', get_current_term_id())
    _validate(term_id)
    evaluation_term = EvaluationTerm.unlock(term_id, current_user.get_uid())
    return tolerant_jsonify(evaluation_term.to_api_json())


def _validate(term_id):
    if term_id not in available_term_ids():
        raise BadRequestError('Invalid term ID.')

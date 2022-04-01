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

from datetime import datetime
from itertools import groupby

from damien.api.errors import BadRequestError, InternalServerError
from damien.api.util import admin_required
from damien.lib.exporter import generate_exports
from damien.lib.http import tolerant_jsonify
from damien.models.department import Department
from damien.models.evaluation import Evaluation
from flask import current_app as app


@app.route('/api/evaluations/export')
@admin_required
def export_evaluations():
    term_id = app.config['CURRENT_TERM_ID']
    validation_errors = Evaluation.get_invalid(term_id, status='confirmed')
    if len(validation_errors):
        raise BadRequestError(f'Cannot export evaluations: {len(validation_errors)} validation errors')

    evals = Evaluation.get_confirmed(term_id)
    timestamp = datetime.now()
    if generate_exports(evals, term_id, timestamp):
        return tolerant_jsonify({'result': 'success'})
    else:
        raise InternalServerError('Something went wrong.')


@app.route('/api/evaluations/validate')
@admin_required
def get_validation():
    term_id = app.config['CURRENT_TERM_ID']
    evals = Evaluation.get_invalid(term_id)
    feed = []
    for dept_id, dept_evals in groupby(evals, key=lambda e: e.department_id):
        feed.extend(Department.find_by_id(dept_id).evaluations_feed(term_id, evaluation_ids=[e.id for e in dept_evals]))
    return tolerant_jsonify(feed)

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
from urllib.parse import unquote

from damien.api.errors import BadRequestError, InternalServerError
from damien.api.util import admin_required, get_term_id
from damien.externals.s3 import stream_folder_zipped
from damien.lib.exporter import generate_exports
from damien.lib.http import tolerant_jsonify
from damien.models.department import Department
from damien.models.evaluation import Evaluation
from damien.models.export import Export
from flask import current_app as app, request, Response, stream_with_context


@app.route('/api/evaluations/export', methods=['POST'])
@admin_required
def export_evaluations():
    term_id = get_term_id(request)
    validation_errors = Evaluation.get_invalid(term_id, status='confirmed')
    if len(validation_errors):
        raise BadRequestError(f'Cannot export evaluations: {len(validation_errors)} validation errors')
    timestamp = datetime.now()
    result = generate_exports(term_id, timestamp)
    if result:
        return tolerant_jsonify(result)
    else:
        raise InternalServerError('Something went wrong.')


@app.route('/api/evaluations/exports')
@admin_required
def get_term_evaluation_exports():
    term_id = get_term_id(request)
    exports = Export.get_for_term(term_id)
    return tolerant_jsonify([e.to_api_json() for e in exports])


@app.route('/api/evaluations/validate')
@admin_required
def get_validation():
    term_id = app.config['CURRENT_TERM_ID']
    evals = Evaluation.get_invalid(term_id)
    feed = []
    for dept_id, dept_evals in groupby(evals, key=lambda e: e.department_id):
        feed.extend(Department.find_by_id(dept_id).evaluations_feed(term_id, evaluation_ids=[e.id for e in dept_evals]))
    return tolerant_jsonify(feed)


@app.route('/api/export/<path:key>')
@admin_required
def download_evaluation_export(key):
    def generator():
        for chunk in stream_folder_zipped(unquote(key)):
            yield chunk
    response = Response(stream_with_context(generator()), mimetype='application/zip')
    timestamp = key[-19:]
    response.headers['Content-Disposition'] = f'attachment; filename=export_{timestamp}.zip'
    return response

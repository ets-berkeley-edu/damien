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
from itertools import groupby
import os
from threading import Thread
from urllib.parse import unquote

from damien.api.errors import BadRequestError, InternalServerError
from damien.api.util import admin_required, get_term_id
from damien.externals.s3 import get_s3_path, stream_folder_zipped
from damien.lib.exporter import background_generate_exports, generate_exports
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
    if os.environ.get('DAMIEN_ENV') == 'test':
        app.logger.info('Test run in progress; will not muddy the waters by actually kicking off a background thread.')
        result = generate_exports(term_id, timestamp)
        if result:
            return tolerant_jsonify(result)
        else:
            raise InternalServerError('There was an error connecting to external services during publication. Please try again.')
    else:
        app.logger.warning('About to start background thread')
        thread = Thread(
            target=background_generate_exports,
            daemon=True,
            kwargs={
                'app_arg': app._get_current_object(),
                'term_id': term_id,
                'timestamp': timestamp,
            },
        )
        try:
            thread.start()
        except Exception as e:
            app.logger.error(e)
            raise InternalServerError('There was an error connecting to external services during publication. Please try again.')
    export = Export.find_by_s3_key(get_s3_path(term_id, timestamp))
    return tolerant_jsonify(export.to_api_json() if export else {})


@app.route('/api/evaluations/export/status')
@admin_required
def get_export_status():
    export = Export.get_latest()
    return tolerant_jsonify(export.to_api_json() if export else {})


@app.route('/api/evaluations/confirmed')
@admin_required
def get_confirmed():
    term_id = get_term_id(request)
    confirmed = Evaluation.get_confirmed(term_id)
    feed = []
    for dept_name, evals in groupby(confirmed, lambda c: c.department.dept_name):
        feed.append({'deptName': dept_name, 'count': len(list(evals))})
    return tolerant_jsonify(feed)


@app.route('/api/evaluations/exports')
@admin_required
def get_term_evaluation_exports():
    term_id = get_term_id(request)
    exports = Export.get_for_term(term_id)
    return tolerant_jsonify([e.to_api_json() for e in exports])


@app.route('/api/evaluations/validate')
@admin_required
def get_validation():
    term_id = get_term_id(request)
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

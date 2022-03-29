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

from itertools import groupby

from damien.api.errors import BadRequestError
from damien.api.util import admin_required
from damien.lib.http import response_with_csv_download, tolerant_jsonify
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

    instructors = {}
    for dept_id, dept_evals in groupby(evals, key=lambda e: e.department_id):
        department_exports = Department.find_by_id(dept_id).get_evaluation_exports(term_id, evaluation_ids=[e.id for e in dept_evals])
        instructors.update(department_exports['instructors'])

    return response_with_csv_download(
        rows=[_export_instructor_row(instructors[k]) for k in sorted(instructors.keys())],
        filename_prefix='instructors',
        fieldnames=_export_instructor_headers(),
    )


@app.route('/api/evaluations/validate')
@admin_required
def get_validation():
    term_id = app.config['CURRENT_TERM_ID']
    evals = Evaluation.get_invalid(term_id)
    feed = []
    for dept_id, dept_evals in groupby(evals, key=lambda e: e.department_id):
        feed.extend(Department.find_by_id(dept_id).evaluations_feed(term_id, evaluation_ids=[e.id for e in dept_evals]))
    return tolerant_jsonify(feed)


def _export_instructor_headers():
    return ['LDAP_UID', 'SIS_ID', 'FIRST_NAME', 'LAST_NAME', 'EMAIL_ADDRESS', 'BLUE_ROLE']


def _export_instructor_row(instructor):
    return {
        'LDAP_UID': instructor['uid'],
        'SIS_ID': instructor['sisId'],
        'FIRST_NAME': instructor['firstName'],
        'LAST_NAME': instructor['lastName'],
        'EMAIL_ADDRESS': instructor['emailAddress'],
        'BLUE_ROLE': '23',
    }

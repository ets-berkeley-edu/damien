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

from damien.api.util import admin_required
from damien.lib.http import tolerant_jsonify
from damien.models.evaluation_type import EvaluationType
from flask import current_app as app
from flask_login import login_required


@app.route('/api/evaluation_type/<name>', methods=['POST'])
@admin_required
def add_evaluation_type(name):
    evaluation_type = EvaluationType.create_or_restore(name)
    return tolerant_jsonify(evaluation_type.to_api_json())


@app.route('/api/evaluation_type/<name>', methods=['DELETE'])
@admin_required
def delete_evaluation_type(name):
    EvaluationType.delete(name)
    return tolerant_jsonify({'message': f'Evaluation type {name} has been deleted'}), 200


@app.route('/api/evaluation_types')
@login_required
def get_evaluation_types():
    evaluation_types = EvaluationType.query.filter_by(deleted_at=None).order_by(EvaluationType.name).all()
    # Force 'F' and 'G' to sort to the top of the list.
    return tolerant_jsonify([e.to_api_json() for e in sorted(evaluation_types, key=lambda e: {'F': '0', 'G': '00'}.get(e.name, e.name))])

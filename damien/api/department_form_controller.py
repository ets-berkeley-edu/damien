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
from damien.lib.cache import delete_from_cache
from damien.lib.http import tolerant_jsonify
from damien.models.department_form import DepartmentForm
from flask import current_app as app
from flask_login import login_required


@app.route('/api/department_form/<name>', methods=['POST'])
@admin_required
def add_department_form(name):
    department_form = DepartmentForm.create_or_restore(name)
    return tolerant_jsonify(department_form.to_api_json())


@app.route('/api/department_form/<name>', methods=['DELETE'])
@admin_required
def delete_department_form(name):
    DepartmentForm.delete(name)
    delete_from_cache(name)
    return tolerant_jsonify({'message': f'Department form {name} has been deleted'}), 200


@app.route('/api/department_forms')
@login_required
def get_department_forms():
    department_forms = DepartmentForm.query.filter_by(deleted_at=None).order_by(DepartmentForm.name).all()
    return tolerant_jsonify([d.to_api_json() for d in department_forms])

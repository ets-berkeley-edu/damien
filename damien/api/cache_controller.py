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

from damien import cache
from damien.api.errors import InternalServerError
from damien.api.util import admin_required
from damien.lib.http import tolerant_jsonify
from flask import current_app as app


@app.route('/api/cache/clear')
@admin_required
def cache_clear():
    if cache.clear():
        return tolerant_jsonify({'status': 'cleared'})
    else:
        raise InternalServerError('Cache clear failed.')


@app.route('/api/cache/delete/<key>')
@admin_required
def cache_delete(key):
    if cache.delete(key):
        return tolerant_jsonify({'key': key, 'status': 'deleted'})
    else:
        raise InternalServerError('Cache delete failed.')


@app.route('/api/cache/inspect/<key>')
@admin_required
def cache_inspect(key):
    value = cache.get(key)
    return tolerant_jsonify({'key': key, 'value': value})

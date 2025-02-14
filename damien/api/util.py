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
from functools import wraps

from damien.api.errors import BadRequestError
from damien.lib.berkeley import available_term_ids, get_current_term_id
from damien.lib.util import get as get_param
from flask import current_app as app, request
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def department_membership_required(func):
    @wraps(func)
    def _department_membership_required(*args, **kw):
        department_id = kw['department_id']
        if current_user.is_authenticated and (
            current_user.is_admin
            or department_id in [str(d['id']) for d in current_user.get_departments() or []]
        ):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _department_membership_required


def get_boolean_param(_dict, key, default_value=None):
    param = get_param(_dict, key, default_value)
    if param == '0' or param == 'f':
        return False
    else:
        return bool(param)


def get_term_id(request):
    term_id = get_param(request.args, 'term_id', get_current_term_id())
    if term_id not in available_term_ids():
        raise BadRequestError('Invalid term ID.')
    return term_id

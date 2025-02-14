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

from damien.models.user import User
from flask_login import UserMixin


class UserSession(UserMixin):

    def __init__(self, user_id):
        self.user = self._load_user(user_id)

    def get_departments(self):
        return self.user['departments']

    def get_id(self):
        return self.user.get('id', None)

    def get_uid(self):
        return self.user.get('uid', None)

    @property
    def is_active(self):
        return self.user['isAuthenticated']

    @property
    def is_anonymous(self):
        return not self.user['isAuthenticated']

    @property
    def is_admin(self):
        return self.user.get('isAdmin', False)

    @property
    def is_authenticated(self):
        return self.user['isAuthenticated']

    def logout(self):
        self.user = self._load_user()

    def to_api_json(self):
        return self.user

    @classmethod
    def _load_user(cls, user_id=None):
        def _to_json(membership):
            return {'id': membership.department_id, 'name': membership.department.dept_name}

        user = User.find_by_id(user_id) if user_id else None
        memberships = user.department_memberships if user else []
        return {
            **(user.to_api_json() if user else {}),
            'departments': [_to_json(m) for m in memberships],
            'isAuthenticated': user is not None,
        }

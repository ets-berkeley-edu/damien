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

from damien.models.user import User
from flask_login import UserMixin


class UserSession(UserMixin):

    def __init__(self, user_id):
        self.user = User.find_by_id(user_id) if user_id else None

    def get_departments(self):
        return self.user and [dm.department for dm in self.user.department_memberships or []]

    def get_id(self):
        return self.user and self.user.id

    def get_uid(self):
        return self.user and self.user.uid

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    @property
    def is_admin(self):
        return self.user.is_admin

    @property
    def is_authenticated(self):
        return self.user is not None

    def logout(self):
        self.user = None

    def to_api_json(self):
        api_json = {
            **(self.user.to_api_json() if self.user else {}),
            'isAuthenticated': self.is_authenticated,
        }

        def _department(department_membership):
            return {
                'id': department_membership.department_id,
                'name': department_membership.department.dept_name,
            }
        if self.user:
            api_json['departments'] = [_department(dm) for dm in self.user.department_memberships]
        return api_json

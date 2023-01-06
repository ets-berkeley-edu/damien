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

from mrsbaylock.models.blue_perm import BluePerm


class User(object):

    def __init__(self, data, dept_roles=[]):
        self.data = data
        self.dept_roles = dept_roles

    @property
    def user_id(self):
        return self.data['user_id']

    @user_id.setter
    def user_id(self, value):
        self.data['user_id'] = value

    @property
    def uid(self):
        uid = self.data['uid'].strip() if self.data['uid'] else None
        return uid

    @uid.setter
    def uid(self, value):
        self.data['uid'] = value

    @property
    def csid(self):
        try:
            return self.data['csid']
        except KeyError:
            return None

    @csid.setter
    def csid(self, value):
        self.data['csid'] = value

    @property
    def first_name(self):
        try:
            return self.data['first_name']
        except KeyError:
            return None

    @first_name.setter
    def first_name(self, value):
        self.data['first_name'] = value

    @property
    def last_name(self):
        try:
            return self.data['last_name']
        except KeyError:
            return None

    @last_name.setter
    def last_name(self, value):
        self.data['last_name'] = value

    @property
    def email(self):
        try:
            return self.data['email']
        except KeyError:
            return None

    @email.setter
    def email(self, value):
        self.data['email'] = value

    @property
    def is_admin(self):
        return self.data['is_admin']

    @property
    def blue_permissions(self):
        if self.data['blue_permissions'] == 'reports_only':
            return BluePerm.BLUE_REPORTS
        elif self.data['blue_permissions'] == 'response_rates':
            return BluePerm.BLUE_REPORTS_RESPONSES
        else:
            return BluePerm.NO_BLUE

    @blue_permissions.setter
    def blue_permissions(self, value):
        self.data['blue_permissions'] = value

    @property
    def dept_forms(self):
        return self.data['dept_forms']

    @dept_forms.setter
    def dept_forms(self, value):
        self.data['dept_forms'] = value

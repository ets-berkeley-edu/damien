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

from mrsbaylock.models.department import Department


class User(object):

    def __init__(self, data):
        self.data = data

    @property
    def user_id(self):
        return self.data['id']

    @property
    def uid(self):
        return self.data['uid']

    @property
    def csid(self):
        return self.data['csid']

    @property
    def first_name(self):
        return self.data['first_name']

    @property
    def last_name(self):
        return self.data['last_name']

    @property
    def email(self):
        return self.data['email']

    @property
    def role_code(self):
        return self.data['role_code']

    @property
    def is_admin(self):
        return self.data['is_admin']

    @property
    def receives_comms(self):
        return self.data['receives_comms']

    @property
    def views_response_rates(self):
        return self.data['views_response_rates']

    @property
    def dept(self):
        return [Department(i) for i in self.data['departments']]
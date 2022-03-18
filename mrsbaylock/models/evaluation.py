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


class Evaluation(object):

    def __init__(self, data):
        self.data = data

    @property
    def term(self):
        return self.data['term']

    @property
    def dept(self):
        return self.data['dept']

    @property
    def ccn(self):
        return self.data['ccn']

    @property
    def x_listing_ccns(self):
        return self.data['x_listing_ccns']

    @property
    def room_share_ccns(self):
        return self.data['room_share_ccns']

    @property
    def subject(self):
        return self.data['subject']

    @property
    def catalog_id(self):
        return self.data['catalog_id']

    @property
    def instruction_format(self):
        return self.data['instruction_format']

    @property
    def instructor(self):
        return self.data['instructor']

    @instructor.setter
    def instructor(self, value):
        self.data['instructor'] = value

    @property
    def start_date(self):
        return self.data['start_date']

    @start_date.setter
    def start_date(self, value):
        self.data['start_date'] = value

    @property
    def end_date(self):
        return self.data['end_date']

    @end_date.setter
    def end_date(self, value):
        self.data['end_date'] = value

    @property
    def dept_form(self):
        return self.data['dept_form']

    @dept_form.setter
    def dept_form(self, value):
        self.data['dept_form'] = value

    @property
    def eval_type(self):
        return self.data['eval_type']

    @eval_type.setter
    def eval_type(self, value):
        self.data['eval_type'] = value

    @property
    def status(self):
        return self.data['status']

    @status.setter
    def status(self, value):
        self.data['status'] = value

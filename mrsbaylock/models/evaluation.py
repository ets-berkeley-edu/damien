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
    def x_listing_ccns_all(self):
        return self.data['x_listing_ccns_all']

    @property
    def foreign_listing(self):
        return self.data['foreign_listing']

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
    def section_num(self):
        return self.data['section_num']

    @property
    def title(self):
        return self.data['title']

    @property
    def primary(self):
        return self.data['primary']

    @property
    def instructor(self):
        return self.data['instructor']

    @property
    def course_start_date(self):
        return self.data['course_start_date']

    @property
    def course_end_date(self):
        return self.data['course_end_date']

    @property
    def eval_start_date(self):
        return self.data['eval_start_date']

    @property
    def eval_end_date(self):
        return self.data['eval_end_date']

    @property
    def dept_form(self):
        return self.data['dept_form']

    @property
    def eval_type(self):
        return self.data['eval_type']

    @property
    def eval_type_custom(self):
        return self.data['eval_type_custom']

    @property
    def status(self):
        return self.data['status']

    @property
    def course_id(self):
        return self.data['course_id']

    @property
    def alpha_suffix(self):
        return self.data['alpha_suffix']

    @x_listing_ccns.setter
    def x_listing_ccns(self, value):
        self.data['x_listing_ccns'] = value

    @room_share_ccns.setter
    def room_share_ccns(self, value):
        self.data['room_share_ccns'] = value

    @instructor.setter
    def instructor(self, value):
        self.data['instructor'] = value

    @course_start_date.setter
    def course_start_date(self, value):
        self.data['course_start_date'] = value

    @course_end_date.setter
    def course_end_date(self, value):
        self.data['course_end_date'] = value

    @eval_start_date.setter
    def eval_start_date(self, value):
        self.data['eval_start_date'] = value

    @eval_end_date.setter
    def eval_end_date(self, value):
        self.data['eval_end_date'] = value

    @dept_form.setter
    def dept_form(self, value):
        self.data['dept_form'] = value

    @eval_type.setter
    def eval_type(self, value):
        self.data['eval_type'] = value

    @status.setter
    def status(self, value):
        self.data['status'] = value

    @course_id.setter
    def course_id(self, value):
        self.data['course_id'] = value

    @alpha_suffix.setter
    def alpha_suffix(self, value):
        self.data['alpha_suffix'] = value

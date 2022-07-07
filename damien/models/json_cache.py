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

from damien import db, std_commit
from damien.models.base import Base
from flask import current_app as app
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError


class JsonCache(Base):
    __tablename__ = 'json_cache'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    term_id = db.Column(db.String, nullable=False)
    department_id = db.Column(db.String, nullable=False)
    course_number = db.Column(db.String, nullable=False)
    json = db.Column(JSONB)

    def __init__(self, term_id, department_id, course_number, json=None):
        self.term_id = term_id
        self.department_id = department_id
        self.course_number = course_number
        self.json = json

    def __repr__(self):
        return f'<JsonCache {self.term_id}/{self.department_id}/{self.course_number}, json={self.json}>'

    @classmethod
    def clear_department(cls, term_id, department_id):
        cls.query.filter_by(term_id=term_id, department_id=department_id).delete(synchronize_session=False)

    @classmethod
    def clear_department_section(cls, term_id, department_id, course_number):
        cls.query.filter_by(term_id=term_id, department_id=department_id, course_number=course_number).delete(synchronize_session=False)

    @classmethod
    def clear_section(cls, term_id, course_number):
        cls.query.filter_by(term_id=term_id, course_number=course_number).delete(synchronize_session=False)

    @classmethod
    def clear_term(cls, term_id):
        cls.query.filter_by(term_id=term_id).delete(synchronize_session=False)

    @classmethod
    def fetch_all_departments(cls, term_id):
        return cls.query.filter_by(term_id=term_id, course_number=None).all()

    @classmethod
    def fetch_department(cls, term_id, department_id):
        stowed = cls.query.filter_by(term_id=term_id, department_id=department_id, course_number=None).first()
        if stowed is not None:
            return stowed.json

    @classmethod
    def fetch_section(cls, term_id, department_id, course_number):
        stowed = cls.query.filter_by(term_id=term_id, department_id=department_id, course_number=course_number).first()
        if stowed is not None:
            return stowed.json

    @classmethod
    def set_department(cls, term_id, department_id, json):
        row = cls(term_id=term_id, department_id=department_id, course_number=None, json=json)
        try:
            db.session.add(row)
            std_commit()
        except IntegrityError:
            app.logger.warn(f'Conflict for department cache {term_id}/{department_id}; will attempt to return stowed JSON')
            return cls.fetch_department(term_id, department_id)

    @classmethod
    def set_section(cls, term_id, department_id, course_number, json):
        row = cls(term_id=term_id, department_id=department_id, course_number=course_number, json=json)
        try:
            db.session.add(row)
            std_commit()
        except IntegrityError:
            app.logger.warn(f'Conflict for section cache {term_id}/{department_id}/{course_number}; will attempt to return stowed JSON')
            return cls.fetch_section(term_id, department_id, course_number)

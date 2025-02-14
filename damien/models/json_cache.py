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

from damien import db, std_commit
from damien.lib.util import utc_now
from damien.models.base import Base
from sqlalchemy.dialects.postgresql import insert, JSONB


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
        cls.query.filter_by(term_id=term_id, department_id=department_id, course_number=None).delete(synchronize_session=False)
        std_commit()

    @classmethod
    def clear_department_section(cls, term_id, department_id, course_number):
        cls.query.filter_by(term_id=term_id, department_id=department_id, course_number=course_number).delete(synchronize_session=False)
        std_commit()

    @classmethod
    def clear_section(cls, term_id, course_number):
        cls.query.filter_by(term_id=term_id, course_number=course_number).delete(synchronize_session=False)
        std_commit()

    @classmethod
    def clear_term(cls, term_id):
        cls.query.filter_by(term_id=term_id).delete(synchronize_session=False)
        std_commit()

    @classmethod
    def delete_matching(cls, token):
        cls.query.filter(cls.json[0].astext.like(f'%{token}%')).delete(synchronize_session=False)
        std_commit()

    @classmethod
    def fetch_all_departments(cls, term_id):
        return cls.query.filter_by(term_id=term_id, course_number=None).all()

    @classmethod
    def fetch_all_sections(cls, term_id, department_id):
        return cls.query.filter(cls.term_id == term_id, cls.department_id == department_id, cls.course_number.isnot(None)).all()

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
        timestamp = utc_now()
        upsert = insert(JsonCache).values(
            term_id=term_id,
            department_id=department_id,
            course_number=None,
            json=json,
            created_at=timestamp,
            updated_at=timestamp,
        ).on_conflict_do_update(
            index_elements=['term_id', 'department_id', 'course_number'],
            set_=dict(json=json, updated_at=timestamp),
        )
        db.session.execute(upsert)
        std_commit()

    @classmethod
    def set_section(cls, term_id, department_id, course_number, json):
        timestamp = utc_now()
        upsert = insert(JsonCache).values(
            term_id=term_id,
            department_id=department_id,
            course_number=course_number,
            json=json,
            created_at=timestamp,
            updated_at=timestamp,
        ).on_conflict_do_update(
            index_elements=['term_id', 'department_id', 'course_number'],
            set_=dict(json=json, updated_at=timestamp),
        )
        db.session.execute(upsert)
        std_commit()

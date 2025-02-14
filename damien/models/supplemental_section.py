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
from damien.lib.cache import clear_department_cache, clear_section_cache
from damien.lib.util import utc_now
from damien.models.base import Base


class SupplementalSection(Base):
    __tablename__ = 'supplemental_sections'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    term_id = db.Column(db.String(4), nullable=False)
    course_number = db.Column(db.String(5), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    deleted_at = db.Column(db.DateTime)

    def __init__(
        self,
        term_id,
        course_number,
        department_id,
    ):
        self.term_id = term_id
        self.course_number = course_number
        self.department_id = department_id

    def __repr__(self):
        return f"""<SupplementalSection id={self.id},
                    term_id={self.term_id}>
                    course_number={self.course_number}>
                    department_id={self.department_id}>
                    deleted_at={self.deleted_at}>
                """

    @classmethod
    def create_or_restore(
            cls,
            term_id,
            course_number,
            department_id,
    ):
        section = cls.query.filter_by(term_id=term_id, course_number=course_number, department_id=department_id).first()
        if section:
            section.deleted_at = None
        else:
            section = cls(term_id=term_id, course_number=course_number, department_id=department_id)
        db.session.add(section)
        std_commit()
        clear_section_cache(term_id, course_number)
        clear_department_cache(department_id, term_id)
        return section

    @classmethod
    def delete(cls, db_id):
        now = utc_now()
        section = cls.query.filter_by(id=db_id).first()
        if section:
            section.deleted_at = now
            db.session.add(section)
            std_commit()
            return section
        else:
            return None

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id, deleted_at=None)
        return query.first()

    @classmethod
    def for_term_and_department(cls, term_id, department_id):
        query = cls.query.filter_by(term_id=term_id, department_id=department_id, deleted_at=None)
        return query.all()

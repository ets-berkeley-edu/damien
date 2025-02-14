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
from damien.lib.util import isoformat
from damien.models.base import Base
from damien.models.department import Department


class DepartmentNote(Base):
    __tablename__ = 'department_notes'

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, primary_key=True)
    term_id = db.Column(db.String(4), nullable=False, primary_key=True)
    note = db.Column(db.Text, default=None)

    department = db.relationship(Department.__name__, back_populates='notes', lazy='joined')

    def __init__(
        self,
        department_id,
        term_id,
        note,
    ):
        self.department_id = department_id
        self.term_id = term_id
        self.note = note

    def __repr__(self):
        return f"""<DepartmentNote department_id={self.department_id},
                    term_id={self.term_id},
                    note={self.note},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>"""

    @classmethod
    def find_by_department_term(cls, department_id, term_id):
        return cls.query.filter_by(department_id=department_id, term_id=term_id).first()

    @classmethod
    def find_by_term(cls, term_id):
        return {n.department_id: n for n in cls.query.filter_by(term_id=term_id).all()}

    @classmethod
    def upsert(
        cls,
        department_id,
        term_id,
        note=None,

    ):
        deptartment_note = cls.query.filter_by(department_id=department_id, term_id=term_id).first()
        if not deptartment_note:
            deptartment_note = cls(department_id=department_id, term_id=term_id, note=note)
            db.session.add(deptartment_note)
            std_commit()
        deptartment_note.note = note.strip() if note else None
        std_commit()
        return deptartment_note

    def to_api_json(self):
        return {
            'departmentId': self.department_id,
            'termId': self.term_id,
            'note': self.note,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

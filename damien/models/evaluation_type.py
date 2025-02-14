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
from damien.lib.util import isoformat, utc_now
from damien.models.base import Base


class EvaluationType(Base):
    __tablename__ = 'evaluation_types'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    name = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime)

    def __init__(
        self,
        name,
    ):
        self.name = name

    def __repr__(self):
        return f"""<EvaluationType id={self.id},
                    name={self.name}>
                """

    @classmethod
    def create_or_restore(
            cls,
            name,
    ):
        evaluation_type = cls.query.filter_by(name=name).first()
        if evaluation_type:
            evaluation_type.deleted_at = None
        else:
            evaluation_type = cls(name=name)
        db.session.add(evaluation_type)
        std_commit()
        return evaluation_type

    @classmethod
    def delete(cls, name):
        now = utc_now()
        evaluation_type = cls.query.filter_by(name=name).first()
        if evaluation_type:
            evaluation_type.deleted_at = now
            db.session.add(evaluation_type)
            std_commit()
            return evaluation_type
        else:
            return None

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id, deleted_at=None)
        return query.first()

    @classmethod
    def find_by_name(cls, name):
        query = cls.query.filter_by(name=name, deleted_at=None)
        return query.first()

    def to_api_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

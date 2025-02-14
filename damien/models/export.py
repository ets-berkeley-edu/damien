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
from sqlalchemy.dialects.postgresql import ENUM


export_status_enum = ENUM(
    'started',
    'success',
    'error',
    name='export_status',
    create_type=False,
)


class Export(Base):
    __tablename__ = 'exports'

    term_id = db.Column(db.String(4), nullable=False)
    s3_path = db.Column(db.String(255), nullable=False, primary_key=True)
    status = db.Column(export_status_enum)

    def __init__(
        self,
        term_id,
        s3_path,
        status,
    ):
        self.term_id = term_id
        self.s3_path = s3_path
        self.status = status

    def __repr__(self):
        return f"""<Export term_id={self.term_id},
                    s3_path={self.s3_path},
                    created_at={self.created_at},
                    status={self.status}>
                """

    @classmethod
    def create(cls, term_id, s3_path):
        export = cls(term_id=term_id, s3_path=s3_path, status='started')
        db.session.add(export)
        std_commit()
        return export

    @classmethod
    def find_by_s3_key(cls, s3_path):
        return cls.query.filter_by(s3_path=s3_path).first()

    @classmethod
    def get_for_term(cls, term_id):
        return cls.query.filter_by(term_id=term_id, status='success').order_by(cls.created_at.desc()).all()

    @classmethod
    def get_latest(cls, term_id=None):
        q = cls.query
        if term_id:
            q = q.filter_by(term_id=term_id)
        return q.order_by(cls.created_at.desc()).first()

    @classmethod
    def update_status(cls, s3_path, status):
        export = cls.query.filter_by(s3_path=s3_path).first()
        if export:
            export.status = status
            std_commit()
        return export

    def to_api_json(self):
        return {
            'termId': self.term_id,
            's3Path': self.s3_path,
            'status': self.status,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

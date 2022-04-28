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
from damien.lib.util import isoformat
from damien.models.base import Base


class Export(Base):
    __tablename__ = 'exports'

    term_id = db.Column(db.String(4), nullable=False)
    s3_path = db.Column(db.String(255), nullable=False, primary_key=True)

    def __init__(
        self,
        term_id,
        s3_path,
    ):
        self.term_id = term_id
        self.s3_path = s3_path

    def __repr__(self):
        return f"""<Export term_id={self.term_id},
                    s3_path={self.s3_path},
                    created_at={self.created_at}>
                """

    @classmethod
    def create(cls, term_id, s3_path):
        export = cls(term_id=term_id, s3_path=s3_path)
        db.session.add(export)
        std_commit()
        return export

    @classmethod
    def get_for_term(cls, term_id):
        return cls.query.filter_by(term_id=term_id).order_by(cls.created_at.desc()).all()

    def to_api_json(self):
        return {
            'termId': self.term_id,
            's3Path': self.s3_path,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

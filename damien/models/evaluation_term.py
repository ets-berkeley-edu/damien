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
from damien.lib.berkeley import get_current_term_id
from damien.lib.util import isoformat, utc_now


class EvaluationTerm(db.Model):
    __tablename__ = 'evaluation_terms'

    term_id = db.Column(db.String(4), nullable=False, primary_key=True)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    updated_by = db.Column(db.String(80))

    def __init__(
        self,
        term_id,
        updated_by=None,
    ):
        self.term_id = term_id
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<EvaluationTerm term_id={self.term_id}, is_locked={self.is_locked}>"""

    @classmethod
    def find_or_create(cls, term_id):
        evaluation_term = cls.query.filter_by(term_id=term_id).first()
        if not evaluation_term:
            evaluation_term = cls(term_id=term_id)
            evaluation_term.is_locked = False if term_id == get_current_term_id() else True
            db.session.add(evaluation_term)
            std_commit()
        return evaluation_term

    @classmethod
    def lock(cls, term_id, updated_by):
        evaluation_term = cls.find_or_create(term_id)
        evaluation_term.is_locked = True
        evaluation_term.updated_by = updated_by
        db.session.add(evaluation_term)
        std_commit()
        return evaluation_term

    @classmethod
    def unlock(cls, term_id, updated_by):
        evaluation_term = cls.find_or_create(term_id)
        evaluation_term.is_locked = False
        evaluation_term.updated_by = updated_by
        db.session.add(evaluation_term)
        std_commit()
        return evaluation_term

    def to_api_json(self):
        return {
            'termId': self.term_id,
            'isLocked': self.is_locked,
            'updatedAt': isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }

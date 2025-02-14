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
from damien.models.department_catalog_listing import DepartmentCatalogListing


class DepartmentForm(Base):
    __tablename__ = 'department_forms'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    name = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime)

    catalog_listings = db.relationship(
        DepartmentCatalogListing.__name__,
        back_populates='default_form',
        lazy='dynamic',
    )
    users = db.relationship(
        'User',
        back_populates='department_forms',
        secondary='user_department_forms',
    )

    def __init__(
        self,
        name,
    ):
        self.name = name

    def __repr__(self):
        return f"""<DepartmentForm id={self.id},
                    name={self.name},
                    deleted_at={self.deleted_at}>
                """

    @classmethod
    def create_or_restore(
            cls,
            name,
    ):
        department_form = cls.query.filter_by(name=name).first()
        if department_form:
            department_form.deleted_at = None
        else:
            department_form = cls(name=name)
        db.session.add(department_form)
        std_commit()
        return department_form

    @classmethod
    def delete(cls, name):
        now = utc_now()
        department_form = cls.query.filter_by(name=name).first()
        if department_form:
            department_form.deleted_at = now
            db.session.add(department_form)
            std_commit()
            return department_form
        else:
            return None

    @classmethod
    def find_by_id(cls, db_id, include_deleted=False):
        if include_deleted:
            return cls.query.filter_by(id=db_id).first()
        return cls.query.filter_by(id=db_id, deleted_at=None).first()

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
            'deletedAt': isoformat(self.deleted_at),
        }

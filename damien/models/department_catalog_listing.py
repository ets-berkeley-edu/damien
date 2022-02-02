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


class DepartmentCatalogListing(Base):
    __tablename__ = 'department_catalog_listings'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    subject_area = db.Column(db.String(255), nullable=False)
    catalog_id = db.Column(db.String(255))

    department = db.relationship('Department', back_populates='catalog_listings')

    def __init__(
        self,
        department_id,
        subject_area,
        catalog_id,
    ):
        self.department_id = department_id
        self.subject_area = subject_area
        self.catalog_id = catalog_id

    def __repr__(self):
        return f"""<DepartmentCatalogListing id={self.id},
                    department_id={self.department_id},
                    subject_area={self.subject_area},
                    catalog_id={self.catalog_id}>
                """

    @classmethod
    def create(
            cls,
            department_id,
            subject_area,
            catalog_id,
    ):
        department_catalog_listing = cls(
            department_id=department_id,
            subject_area=subject_area,
            catalog_id=catalog_id,
        )
        db.session.add(department_catalog_listing)
        std_commit()
        return department_catalog_listing

    @classmethod
    def catalog_ids_to_exclude(cls, department_id, subject_area):
        results = cls.query.filter(cls.subject_area.in_([subject_area, '']), cls.department_id != department_id).all()
        return [r.catalog_id for r in results]

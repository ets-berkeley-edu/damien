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
from damien.models.department_catalog_listing import DepartmentCatalogListing
from flask import current_app as app
from sqlalchemy.sql import text


class Department(Base):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    dept_name = db.Column(db.String(255), nullable=False)
    is_enrolled = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.Text, default=None)

    members = db.relationship(
        'DepartmentMember',
        back_populates='department',
    )
    catalog_listings = db.relationship(
        DepartmentCatalogListing.__name__,
        back_populates='department',
        lazy='joined',
    )

    def __init__(
        self,
        dept_name,
        is_enrolled=False,
        note=None,
    ):
        self.dept_name = dept_name
        self.is_enrolled = is_enrolled
        self.note = note

    def __repr__(self):
        return f"""<Department id={self.id},
                    dept_name={self.dept_name},
                    is_enrolled={self.is_enrolled},
                    note={self.note}>
                """

    @classmethod
    def create(
            cls,
            dept_name,
            is_enrolled=False,
            note=None,
    ):
        department = cls(
            dept_name=dept_name,
            is_enrolled=is_enrolled,
            note=note,
        )
        db.session.add(department)
        std_commit()
        return department

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id)
        return query.first()

    @classmethod
    def find_by_name(cls, dept_name):
        query = cls.query.filter_by(dept_name=dept_name)
        return query.first()

    @classmethod
    def all_enrolled(cls):
        query = cls.query.filter_by(is_enrolled=True)
        return query.all()

    def catalog_listings_map(self):
        listings_map = {}
        for listing in self.catalog_listings:
            if listing.subject_area not in listings_map:
                listings_map[listing.subject_area] = []
            listings_map[listing.subject_area].append(listing.catalog_id or '*')
        return listings_map

    def get_loch_courses(self, term_id):
        conditions = []
        for subject_area, catalog_ids in self.catalog_listings_map().items():
            subconditions = []
            if len(subject_area):
                subconditions.append(f"s.subject_area = '{subject_area}'")
            if '*' in catalog_ids:
                exclusions = DepartmentCatalogListing.catalog_ids_to_exclude(self.id, subject_area)
                if len(exclusions):
                    subconditions.append(f"s.catalog_id NOT SIMILAR TO '({'|'.join(exclusions)})'")
            elif len(catalog_ids) == 1:
                subconditions.append(f"s.catalog_id SIMILAR TO '{catalog_ids[0]}'")
            else:
                subconditions.append(f"s.catalog_id SIMILAR TO '({'|'.join(catalog_ids)})'")
            conditions.append(f"({' AND '.join(subconditions)})")
        query = f"""SELECT *
                FROM unholy_loch.sis_sections s
                JOIN unholy_loch.sis_instructors i
                ON s.instructor_uid = i.ldap_uid
                WHERE s.term_id = :term_id AND ({' OR '.join(conditions)})
            """
        results = db.session().execute(text(query), {'term_id': term_id}).all()
        app.logger.info(f'Unholy loch query for {self.dept_name} courses returned {len(results)} reuslts: {query}')
        return results

    def to_api_json(self):
        return {
            'id': self.id,
            'deptName': self.dept_name,
            'isEnrolled': self.is_enrolled,
            'note': self.note,
            'catalogListings': self.catalog_listings_map(),
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

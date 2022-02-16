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

from itertools import groupby

from damien import db, std_commit
from damien.lib.queries import get_loch_instructors, get_loch_sections
from damien.lib.util import isoformat
from damien.merged.section import Section
from damien.models.base import Base
from damien.models.department_catalog_listing import DepartmentCatalogListing
from damien.models.evaluation import Evaluation
from damien.models.evaluation_type import EvaluationType
from flask import current_app as app


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

    @classmethod
    def update(cls, department_id, note=None):
        department = cls.query.filter_by(id=department_id).first()
        department.note = note.strip() if note else None
        db.session.add(department)
        std_commit()
        return department

    def catalog_listings_map(self):
        listings_map = {}
        for listing in self.catalog_listings:
            if listing.subject_area not in listings_map:
                listings_map[listing.subject_area] = []
            listings_map[listing.subject_area].append(listing.catalog_id or '*')
        return listings_map

    def get_department_sections(self, term_id):
        conditions = []
        for subject_area, catalog_ids in self.catalog_listings_map().items():
            subconditions = []
            if len(subject_area):
                subconditions.append(f"subject_area = '{subject_area}'")
            if '*' in catalog_ids:
                exclusions = DepartmentCatalogListing.catalog_ids_to_exclude(self.id, subject_area)
                if len(exclusions):
                    subconditions.append(f"catalog_id NOT SIMILAR TO '({'|'.join(exclusions)})'")
            elif len(catalog_ids) == 1:
                subconditions.append(f"catalog_id SIMILAR TO '{catalog_ids[0]}'")
            else:
                subconditions.append(f"catalog_id SIMILAR TO '({'|'.join(catalog_ids)})'")
            conditions.append(f"({' AND '.join(subconditions)})")
        return get_loch_sections(term_id, conditions)

    def get_visible_sections(self, term_id=None):
        sections = []
        term_id = term_id or app.config['CURRENT_TERM_ID']

        loch_sections = self.get_department_sections(term_id)
        sections_by_number = {k: list(v) for k, v in groupby(loch_sections, key=lambda r: r['course_number'])}
        evaluations = Evaluation.fetch_by_course_numbers(term_id, sections_by_number.keys())

        instructor_uids = set(s['instructor_uid'] for s in loch_sections if s['instructor_uid'])
        for v in evaluations.values():
            instructor_uids.update(e.instructor_uid for e in v if e.instructor_uid)
        instructors = {}
        for row in get_loch_instructors(list(instructor_uids)):
            instructors[row['ldap_uid']] = {
                'uid': row['ldap_uid'],
                'sisId': row['sis_id'],
                'firstName': row['first_name'],
                'lastName': row['last_name'],
                'emailAddress': row['email_address'],
                'affiliations': row['affiliations'],
            }

        all_eval_types = {et.name: et for et in EvaluationType.query.all()}

        for course_number, loch_rows in sections_by_number.items():
            section_evaluations = evaluations.get(course_number, [])
            loch_rows_visible = next((True for r in loch_rows if Section.is_visible_by_default(r)), False)
            evaluations_visible = next((True for e in section_evaluations if e.is_visible()), False)
            if loch_rows_visible or evaluations_visible:
                sections.append(Section(
                    loch_rows,
                    section_evaluations,
                    instructors=instructors,
                    catalog_listings=self.catalog_listings,
                    evaluation_type_cache=all_eval_types,
                ))
        return sections

    def evaluations_feed(self, term_id=None, evaluation_ids=None):
        feed = []
        for s in self.get_visible_sections(term_id):
            feed.extend(s.get_evaluation_feed(evaluation_ids=evaluation_ids))
        return feed

    def to_api_json(self, include_contacts=False, include_evaluations=False, term_id=None):
        feed = {
            'id': self.id,
            'deptName': self.dept_name,
            'isEnrolled': self.is_enrolled,
            'note': self.note,
            'catalogListings': self.catalog_listings_map(),
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }
        if include_contacts:
            feed['contacts'] = [user.to_api_json() for user in self.members]
        if include_evaluations:
            feed['evaluations'] = self.evaluations_feed(term_id)
        return feed

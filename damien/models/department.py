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
from damien.lib.queries import get_cross_listings, get_loch_instructors, get_loch_sections, get_loch_sections_by_ids, get_room_shares
from damien.lib.util import isoformat
from damien.merged.section import Section
from damien.models.base import Base
from damien.models.department_catalog_listing import DepartmentCatalogListing
from damien.models.evaluation import Evaluation
from damien.models.evaluation_type import EvaluationType
from damien.models.supplemental_section import SupplementalSection
from flask import current_app as app


class Department(Base):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    dept_name = db.Column(db.String(255), nullable=False)
    is_enrolled = db.Column(db.Boolean, nullable=False, default=False)

    members = db.relationship(
        'DepartmentMember',
        back_populates='department',
    )
    notes = db.relationship(
        'DepartmentNote',
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
    ):
        self.dept_name = dept_name
        self.is_enrolled = is_enrolled

    def __repr__(self):
        return f"""<Department id={self.id},
                    dept_name={self.dept_name},
                    is_enrolled={self.is_enrolled}>
                """

    @classmethod
    def create(
            cls,
            dept_name,
            is_enrolled=False,
    ):
        department = cls(
            dept_name=dept_name,
            is_enrolled=is_enrolled,
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
        sections = get_loch_sections(term_id, conditions)
        self.merge_cross_listings(sections, term_id)
        return sections

    def get_supplemental_sections(self, term_id):
        course_numbers = [r.course_number for r in SupplementalSection.for_term_and_department(term_id, self.id)]
        sections = get_loch_sections_by_ids(term_id, course_numbers)
        self.merge_cross_listings(sections, term_id)
        return sections

    def merge_cross_listings(self, sections, term_id):
        course_numbers = list(set(s.course_number for s in sections))
        sections.extend(get_cross_listings(term_id, course_numbers))
        sections.extend(get_room_shares(term_id, course_numbers))

    def get_visible_sections(self, term_id=None):
        sections = []
        term_id = term_id or app.config['CURRENT_TERM_ID']

        # Sections included in the department by default.
        default_loch_sections = self.get_department_sections(term_id)
        # Sections that have been manually added.
        supplemental_loch_sections = self.get_supplemental_sections(term_id)

        supplemental_section_ids = set()
        sections_by_number = {k: list(v) for k, v in groupby(default_loch_sections, key=lambda r: r['course_number'])}
        for k, v in groupby(supplemental_loch_sections, key=lambda r: r['course_number']):
            sections_by_number[k] = list(v)
            supplemental_section_ids.add(k)

        all_sections = default_loch_sections + supplemental_loch_sections

        evaluations = Evaluation.fetch_by_course_numbers(term_id, sections_by_number.keys())

        instructor_uids = set(s['instructor_uid'] for s in all_sections if s['instructor_uid'])
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

        for course_number in sorted(sections_by_number.keys()):
            section_evaluations = evaluations.get(course_number, [])
            visible_loch_rows = [
                r for r in sections_by_number[course_number] if Section.is_visible_by_default(r) or course_number in supplemental_section_ids]
            visible_evaluations = [e for e in section_evaluations if e.is_visible()]
            if len(visible_loch_rows) or len(visible_evaluations):
                sections.append(Section(
                    visible_loch_rows,
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

    def to_api_json(
        self,
        include_contacts=False,
        include_evaluations=False,
        include_notes=False,
        include_sections=False,
        term_id=None,
    ):
        feed = {
            'id': self.id,
            'deptName': self.dept_name,
            'isEnrolled': self.is_enrolled,
            'catalogListings': self.catalog_listings_map(),
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }
        if include_contacts:
            feed['contacts'] = [user.to_api_json() for user in self.members]
        if include_evaluations:
            feed['evaluations'] = self.evaluations_feed(term_id)
        if include_notes:
            feed['notes'] = {note.term_id: note.to_api_json() for note in self.notes}
        if include_sections:
            feed['totalSections'] = len(self.get_visible_sections())
        return feed

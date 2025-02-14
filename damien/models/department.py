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

from itertools import groupby

from damien import db, std_commit
from damien.lib.berkeley import get_current_term_id
from damien.lib.cache import clear_department_cache, fetch_all_sections, fetch_department_cache, set_department_cache
from damien.lib.queries import get_cross_listings, get_loch_instructors, get_loch_sections, get_loch_sections_by_ids, get_room_shares
from damien.lib.util import extract_int, isoformat
from damien.merged.section import Section
from damien.models.base import Base
from damien.models.department_catalog_listing import DepartmentCatalogListing
from damien.models.evaluation import Evaluation
from damien.models.evaluation_type import EvaluationType
from damien.models.supplemental_instructor import SupplementalInstructor
from damien.models.supplemental_section import SupplementalSection
from flask import current_app as app
from sqlalchemy import text
from sqlalchemy.orm import joinedload


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
    evaluations = db.relationship(
        'Evaluation',
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
    def all_enrolled(cls, load_contacts=False):
        query = cls.query.filter_by(is_enrolled=True).order_by(cls.dept_name)
        if load_contacts:
            query = query.options(joinedload(cls.members).joinedload('user'))
        return query.all()

    def catalog_listings_map(self, term_id):
        listings_map = {}
        for listing in sorted(self.catalog_listings, key=lambda cl: [cl.subject_area, extract_int(cl.catalog_id)]):
            if listing.start_term_id and listing.start_term_id > term_id:
                continue
            if listing.end_term_id and listing.end_term_id < term_id:
                continue
            if listing.subject_area not in listings_map:
                listings_map[listing.subject_area] = []
            listings_map[listing.subject_area].append(listing.catalog_id or '*')
        return listings_map

    def enrolled_terms(self):
        return DepartmentCatalogListing.department_terms(self.id)

    def get_department_sections(self, term_id):
        conditions = []
        for subject_area, catalog_ids in self.catalog_listings_map(term_id).items():
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
            if len(subconditions):
                conditions.append(f"({' AND '.join(subconditions)})")
        if not len(conditions):
            return []
        sections = get_loch_sections(term_id, conditions)
        self.merge_cross_listings(sections, term_id)
        return sorted(sections, key=lambda r: r['course_number'])

    def get_supplemental_sections(self, term_id):
        course_numbers = [r.course_number for r in SupplementalSection.for_term_and_department(term_id, self.id)]
        sections = get_loch_sections_by_ids(term_id, course_numbers)
        self.merge_cross_listings(sections, term_id, course_numbers)
        return sorted(sections, key=lambda r: r['course_number'])

    def merge_cross_listings(self, sections, term_id, course_numbers=None):
        if not course_numbers:
            course_numbers = list(set(s.course_number for s in sections if Section.is_visible_by_default(s)))
        room_shares = get_room_shares(term_id, course_numbers)
        sections.extend(room_shares)
        course_numbers.extend(list(set(s.course_number for s in room_shares if Section.is_visible_by_default(s))))
        sections.extend(get_cross_listings(term_id, course_numbers))

    def get_visible_sections(self, term_id=None, section_id=None, include_empty_sections=False):
        sections = []
        term_id = term_id or get_current_term_id()

        if section_id:
            # If we're fetching a feed for a specific section only, grab matching rows.
            default_loch_sections = get_loch_sections_by_ids(term_id, [section_id])
            supplemental_loch_sections = []
        else:
            # Otherwise grab everything in the department. First, sections included in the department by default.
            default_loch_sections = self.get_department_sections(term_id)
            # Next, sections that have been manually added.
            supplemental_loch_sections = self.get_supplemental_sections(term_id)

        supplemental_section_ids = set()
        sections_by_number = {k: list(v) for k, v in groupby(default_loch_sections, key=lambda r: r['course_number'])}
        for k, v in groupby(supplemental_loch_sections, key=lambda r: r['course_number']):
            sections_by_number[k] = list(v)
            supplemental_section_ids.add(k)

        all_sections = default_loch_sections + supplemental_loch_sections
        evaluations = Evaluation.fetch_by_course_numbers(term_id, sections_by_number.keys())
        instructors = _get_instructors(all_sections, evaluations)
        all_eval_types = {et.name: et for et in EvaluationType.query.all()}
        all_catalog_listings = DepartmentCatalogListing.query.all()

        def _is_loch_row_visible(row):
            return (Section.is_visible_by_default(row, include_empty_sections)
                    or row['course_number'] in supplemental_section_ids or row['course_number'] == section_id)

        visible_loch_rows_by_course_number = {}
        for course_number in sorted(sections_by_number.keys()):
            visible_loch_rows = [r for r in sections_by_number[course_number] if _is_loch_row_visible(r)]
            if len(visible_loch_rows):
                visible_loch_rows_by_course_number[course_number] = visible_loch_rows

        # If we're fetching the whole department, stash the set of visible course numbers to filter down cross-listings.
        visible_course_numbers = None
        if not section_id:
            visible_course_numbers = visible_loch_rows_by_course_number.keys()

        for course_number, visible_loch_rows in visible_loch_rows_by_course_number.items():
            section_evaluations = evaluations.get(course_number, [])
            sections.append(Section(
                visible_loch_rows,
                section_evaluations,
                all_catalog_listings,
                all_eval_types,
                instructors,
                visible_course_numbers,
            ))

        return {'sections': sections, 'instructors': instructors}

    def get_evaluation_exports(self, term_id, evaluation_ids):
        exports = {
            'evaluations': {},
            'instructors': {},
            'sections': {},
        }
        vs = self.get_visible_sections(term_id, include_empty_sections=True)
        cached_department = self.fetch_summary_feed(term_id)

        for s in vs['sections']:
            section_evaluation_exports = s.get_evaluation_exports(
                department_id=self.id,
                evaluation_ids=evaluation_ids,
                uses_midterm_forms=cached_department.get('usesMidtermForms'),
            )
            exports['evaluations'].update(section_evaluation_exports)
            exports['sections'][s.course_number] = s

            for instructor_uid_set in section_evaluation_exports.values():
                for uid in instructor_uid_set:
                    if uid not in exports['instructors']:
                        exports['instructors'][uid] = vs['instructors'].get(uid)

        return exports

    def evaluations_feed(self, term_id=None, section_id=None, evaluation_ids=None):
        term_id = term_id or get_current_term_id()
        sections_cache = fetch_all_sections(self.id, term_id)
        uses_midterm_forms = self.uses_midterm_forms(term_id)
        app.logger.debug(
            f'Generating evaluations feed (dept_id={self.id}, term_id={term_id}, section_id={section_id}, evaluation_ids={evaluation_ids}')
        feed = []

        for s in self.get_visible_sections(term_id, section_id)['sections']:
            feed.extend(
                s.get_evaluation_feed(
                    department_id=self.id,
                    uses_midterm_forms=uses_midterm_forms,
                    sections_cache=sections_cache,
                    evaluation_ids=evaluation_ids,
                ),
            )

        if not section_id and not evaluation_ids:
            self.cache_summary_feed(term_id, uses_midterm_forms, feed)

        return feed

    def cache_summary_feed(self, term_id, uses_midterm_forms, feed):
        feed = {
            'lastUpdated': isoformat(Evaluation.get_last_update(self.id, term_id)),
            'totalBlockers': len([e for e in feed if e['status'] == 'confirmed' and not e['valid']]),
            'totalConfirmed': len([e for e in feed if e['status'] == 'confirmed' and e['valid']]),
            'totalInError': len([e for e in feed if not e['valid']]),
            'totalEvaluations': len(feed),
            'usesMidtermForms': uses_midterm_forms,
        }
        clear_department_cache(self.id, term_id)
        set_department_cache(self.id, term_id, feed)
        return feed

    def fetch_summary_feed(self, term_id):
        summary_feed = fetch_department_cache(self.id, term_id)
        # A missing summary requires the underlying evaluations feed to be regenerated.
        if not summary_feed:
            self.evaluations_feed(term_id)
            summary_feed = fetch_department_cache(self.id, term_id)
        return summary_feed

    def to_api_json(
        self,
        term_id,
        include_contacts=False,
        include_evaluations=False,
        include_sections=False,
        include_status=False,
        departments_cache=None,
        notes_cache=None,
    ):
        cached_department = departments_cache.get(self.id) if departments_cache else None
        if not cached_department:
            cached_department = self.fetch_summary_feed(term_id)

        feed = {
            'id': self.id,
            'deptName': self.dept_name,
            'isEnrolled': self.is_enrolled,
            'catalogListings': self.catalog_listings_map(term_id),
            'createdAt': isoformat(self.created_at),
            'enrolledTerms': self.enrolled_terms(),
            'updatedAt': isoformat(self.updated_at),
            'usesMidtermForms': cached_department.get('usesMidtermForms'),
        }

        note = None
        if notes_cache:
            note = notes_cache.get(self.id)
        else:
            from damien.models.department_note import DepartmentNote
            note = DepartmentNote.find_by_department_term(self.id, term_id)
        feed['note'] = note.to_api_json() if note else None

        if include_contacts:
            feed['contacts'] = sorted([user.to_api_json() for user in self.members if user.user], key=lambda m: m['lastName'])

        if include_evaluations:
            evaluations = self.evaluations_feed(term_id)
            feed['evaluations'] = evaluations

        if include_status:
            feed.update(cached_department)

        if include_sections:
            feed['totalSections'] = cached_department.get('totalEvaluations')
        return feed

    def uses_midterm_forms(self, term_id):
        params = {
            'department_id': self.id,
            'term_id': term_id,
        }
        query = text(
            """SELECT *
                FROM department_forms df
                JOIN department_catalog_listings dcl ON df.name = dcl.subject_area || '_MID'
                WHERE df.name LIKE '%_MID'
                AND df.deleted_at IS NULL
                AND dcl.department_id = :department_id
                AND (dcl.start_term_id IS NULL OR dcl.start_term_id <= :term_id)
                AND (dcl.end_term_id IS NULL OR dcl.end_term_id >= :term_id)
            """,
        )
        result = db.session.execute(query, params).fetchone()
        app.logger.info(f'Department uses_midterm_forms query returned {len(result or [])} rows: {query}\n{params}')
        return result is not None


def _get_instructors(all_sections, evaluations):
    instructor_uids = set(s['instructor_uid'] for s in all_sections if s['instructor_uid'] and s['instructor_uid'].strip())
    for v in evaluations.values():
        instructor_uids.update(e.instructor_uid for e in v if e.instructor_uid)
    instructors = {}
    for i in SupplementalInstructor.find_by_uids(list(instructor_uids)):
        instructors[i.ldap_uid] = {
            'uid': i.ldap_uid,
            'sisId': i.sis_id,
            'firstName': i.first_name,
            'lastName': i.last_name,
            'emailAddress': i.email_address,
        }
        instructor_uids.remove(i.ldap_uid)
    loch_instructors = get_loch_instructors(list(instructor_uids))
    for row in loch_instructors:
        instructors[row['ldap_uid']] = {
            'uid': row['ldap_uid'],
            'sisId': row['sis_id'],
            'firstName': row['first_name'],
            'lastName': row['last_name'],
            'emailAddress': row['email_address'],
            'affiliations': row['affiliations'],
        }
        instructor_uids.remove(row['ldap_uid'])
    for uid in instructor_uids:
        instructors[uid] = {
            'uid': uid,
            'sisId': None,
            'firstName': None,
            'lastName': None,
            'emailAddress': None,
        }
    return instructors

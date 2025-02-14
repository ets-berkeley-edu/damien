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
import re

from damien.lib.cache import fetch_section_cache, set_section_cache
from damien.lib.queries import get_loch_sections_by_ids
from damien.models.evaluation import Evaluation


class Section:

    def __init__(
        self,
        loch_rows,
        evaluations=(),
        catalog_listings=(),
        evaluation_types=None,
        instructors=None,
        visible_course_numbers=None,
    ):
        self.term_id = loch_rows[0].term_id
        self.course_number = loch_rows[0].course_number
        self.subject_area = loch_rows[0].subject_area
        self.catalog_id = loch_rows[0].catalog_id
        self.instruction_format = loch_rows[0].instruction_format
        self.section_num = loch_rows[0].section_num
        self.course_title = loch_rows[0].course_title
        self.is_primary = loch_rows[0].is_primary

        self.start_date = min((r['meeting_start_date'] for r in loch_rows if r['meeting_start_date']), default=None)
        self.end_date = max((r['meeting_end_date'] for r in loch_rows if r['meeting_end_date']), default=None)

        self.loch_rows = loch_rows
        self.evaluations = evaluations
        self.instructors = instructors or {}

        self.set_cross_listed_status(loch_rows, visible_course_numbers)
        self.set_defaults(catalog_listings, evaluation_types)

    def __repr__(self):
        return f"""<Section term_id={self.term_id},
                    course_number={self.course_number},
                    subject_area={self.subject_area},
                    catalog_id={self.catalog_id},
                    instruction_format={self.instruction_format},
                    section_num={self.section_num},
                    course_title={self.course_title},
                    is_primary={self.is_primary},
                    start_date={self.start_date},
                    end_date={self.end_date},
                    default_evaluation_types={self.default_evaluation_types},
                    default_form={self.default_form},
                    cross_listed_with={self.cross_listed_with},
                    room_shared_with={self.room_shared_with},
                    foreign_department_course={self.foreign_department_course}>
                """

    @classmethod
    def is_visible_by_default(cls, loch_row, include_empty_sections=False):
        return (
            (loch_row.enrollment_count or include_empty_sections)
            and loch_row.instructor_role_code != 'ICNT'
            and loch_row.instruction_format not in {'CLC', 'GRP', 'IND', 'SUP', 'VOL'}
        )

    @classmethod
    def for_id(cls, term_id, course_number):
        section = None
        loch_rows = get_loch_sections_by_ids(term_id, [course_number])
        if loch_rows:
            section = cls(loch_rows)
        if section:
            return section.to_api_json()

    def set_cross_listed_status(self, loch_rows, visible_course_numbers):
        self.cross_listed_with = set()
        self.room_shared_with = set()
        self.foreign_department_course = True
        for r in loch_rows:
            # Any row with a room-share or cross-listing notation applies to the whole section.
            clw = getattr(r, 'cross_listed_with', None)
            if clw and (not visible_course_numbers or clw in visible_course_numbers):
                self.cross_listed_with.add(clw)
            rsw = getattr(r, 'room_shared_with', None)
            if rsw and (not visible_course_numbers or rsw in visible_course_numbers):
                self.room_shared_with.add(rsw)
            # But a section is treated as belonging to a foreign department only if all rows have the notation.
            fdc = getattr(r, 'foreign_department_course', None)
            if not fdc:
                self.foreign_department_course = False
        self.cross_listed_with = sorted(self.cross_listed_with)
        self.room_shared_with = sorted(self.room_shared_with)

    def find_catalog_listing(self, catalog_listings):
        candidate_catalog_listings = list(
            c for c in catalog_listings
            if c.subject_area in (self.subject_area, '') and (c.catalog_id is None or re.match(f'^{c.catalog_id}$', self.catalog_id))
        )
        # Exact matches on catalog id take precedence.
        exact_catalog_id_match = next((c for c in candidate_catalog_listings if c.catalog_id and re.match(c.catalog_id, self.catalog_id)), None)
        if exact_catalog_id_match:
            return exact_catalog_id_match
        # Otherwise return any match on subject area.
        elif len(candidate_catalog_listings):
            return candidate_catalog_listings[0]

    def set_defaults(self, catalog_listings, evaluation_types):
        catalog_listing = self.find_catalog_listing(catalog_listings)

        # Apply a default form value to courses not cross-listed or room shared.
        if catalog_listing and not self.cross_listed_with and not self.room_shared_with:
            self.default_form = catalog_listing.default_form
        else:
            self.default_form = None

        # Apply default evaluation types unless the catalog listing uses custom types.
        if catalog_listing and not catalog_listing.custom_evaluation_types:
            self.default_evaluation_types = evaluation_types
        else:
            self.default_evaluation_types = None

    def merge_evaluations(self, department_id, uses_midterm_forms):
        merged_evaluations = []

        # Multiple loch rows for a single section-instructor pairing are possible.
        loch_rows_by_instructor_uid = {k: list(v) for k, v in groupby(self.loch_rows, key=lambda r: r['instructor_uid'])}
        merged_evaluation_uids = set()
        self.uids_with_midterm_and_final = set()

        home_dept_evals = []
        foreign_dept_evals_by_uid = {}

        def _stash_foreign_evals(eval_rows, key):
            if eval_rows:
                if key not in foreign_dept_evals_by_uid:
                    foreign_dept_evals_by_uid[key] = []
                foreign_dept_evals_by_uid[key].extend(eval_rows)

        sorted_evaluations = sorted(self.evaluations, key=lambda e: (e.instructor_uid or ''))
        for instructor_uid, evaluations_for_instructor_uid in groupby(sorted_evaluations, key=lambda e: e.instructor_uid):
            evaluations_for_instructor_uid = list(evaluations_for_instructor_uid)
            has_midterm_evals = False
            has_final_evals = False
            foreign_dept_evals_midterm = []
            foreign_dept_evals_final = []

            for evaluation in evaluations_for_instructor_uid:
                if evaluation.is_midterm() and not uses_midterm_forms:
                    continue
                if evaluation.is_midterm():
                    has_midterm_evals = True
                else:
                    has_final_evals = True

                if evaluation.department_id == department_id:
                    home_dept_evals.append(evaluation)
                elif evaluation.is_midterm():
                    foreign_dept_evals_midterm.append(evaluation)
                else:
                    foreign_dept_evals_final.append(evaluation)

            # Course-instructor pairings with both midterm and final evaluations in the database require special handling.
            if has_midterm_evals and has_final_evals:
                self.uids_with_midterm_and_final.add(instructor_uid)
                _stash_foreign_evals(foreign_dept_evals_midterm, f'{instructor_uid}-midterm')
                _stash_foreign_evals(foreign_dept_evals_final, f'{instructor_uid}-final')
            # Otherwise, if midterm-and-final special handling is not needed, we stash all foreign department evals together under the instructor UID.
            else:
                _stash_foreign_evals((foreign_dept_evals_midterm + foreign_dept_evals_final), instructor_uid)

        self.merge_home_dept_evaluations(
            merged_evaluations,
            home_dept_evals,
            loch_rows_by_instructor_uid,
            foreign_dept_evals_by_uid,
            merged_evaluation_uids,
        )
        self.merge_loch_evaluations(
            merged_evaluations,
            loch_rows_by_instructor_uid,
            foreign_dept_evals_by_uid,
            merged_evaluation_uids,
        )
        self.merge_foreign_dept_evaluations(
            merged_evaluations,
            loch_rows_by_instructor_uid,
            foreign_dept_evals_by_uid,
            merged_evaluation_uids,
        )

        return merged_evaluations

    def merge_home_dept_evaluations(
        self,
        merged_evaluations,
        home_dept_evals,
        loch_rows_by_instructor_uid,
        foreign_dept_evals_by_uid,
        merged_evaluation_uids,
    ):
        # Create one API feed element per visible saved evaluation, merging in data from SIS as needed.
        for evaluation in home_dept_evals:
            if not evaluation.is_visible():
                continue
            # When merging evaluation data for a specific instructor, we prefer in order: 1) loch rows for that specific
            # instructor; 2) loch rows with no instructor; 3) any loch rows available.
            loch_rows_for_uid = loch_rows_by_instructor_uid.get(evaluation.instructor_uid) or loch_rows_by_instructor_uid.get(None) or self.loch_rows

            merged_evaluation_uids.add(evaluation.instructor_uid)
            if evaluation.instructor_uid in self.uids_with_midterm_and_final:
                evals_key = f'{evaluation.instructor_uid}-midterm' if evaluation.is_midterm() else f'{evaluation.instructor_uid}-final'
                merged_evaluation_uids.add(evals_key)
            else:
                evals_key = evaluation.instructor_uid

            merged_evaluations.append(Evaluation.merge_transient(
                evaluation.instructor_uid,
                loch_rows_for_uid,
                saved_evaluation=evaluation,
                foreign_dept_evaluations=foreign_dept_evals_by_uid.get(evals_key, []),
                instructor=self.instructors.get(evaluation.instructor_uid),
                default_form=self.default_form,
                default_evaluation_types=self.default_evaluation_types,
            ))

    def merge_loch_evaluations(
        self,
        merged_evaluations,
        loch_rows_by_instructor_uid,
        foreign_dept_evals_by_uid,
        merged_evaluation_uids,
    ):
        # Supplement with SIS-only rows.
        for instructor_uid, loch_rows_for_uid in loch_rows_by_instructor_uid.items():
            # Ignore instructor UIDs already handled under saved evaluations.
            if instructor_uid in merged_evaluation_uids:
                continue
            # Ignore rows without an instructor unless we have no saved evaluations.
            if instructor_uid is None and len(self.evaluations):
                continue

            eval_key = f'{instructor_uid}-final' if instructor_uid in self.uids_with_midterm_and_final else instructor_uid
            merged_evaluation_uids.add(eval_key)

            merged_evaluations.append(Evaluation.merge_transient(
                instructor_uid,
                loch_rows_for_uid,
                saved_evaluation=None,
                foreign_dept_evaluations=foreign_dept_evals_by_uid.get(eval_key, []),
                instructor=self.instructors.get(instructor_uid),
                default_form=self.default_form,
                default_evaluation_types=self.default_evaluation_types,
            ))

    def merge_foreign_dept_evaluations(
        self,
        merged_evaluations,
        loch_rows_by_instructor_uid,
        foreign_dept_evals_by_uid,
        merged_evaluation_uids,
    ):
        # Add foreign department rows.
        for eval_key, evaluations_for_instructor_uid in foreign_dept_evals_by_uid.items():
            # Ignore instructor UIDs already handled under saved evaluations.
            if eval_key in merged_evaluation_uids:
                continue

            # In the case of midterm-and-final special handling, the "-midterm" or "-final" suffix needs to be chopped off the instructor UID.
            if eval_key and not eval_key.startswith('None'):
                instructor_uid = eval_key.split('-')[0]
            else:
                instructor_uid = None
            loch_rows_for_uid = loch_rows_by_instructor_uid.get(instructor_uid) or loch_rows_by_instructor_uid.get(None) or self.loch_rows

            merged_evaluations.append(Evaluation.merge_transient(
                instructor_uid,
                loch_rows_for_uid,
                saved_evaluation=None,
                foreign_dept_evaluations=evaluations_for_instructor_uid,
                instructor=self.instructors.get(instructor_uid),
                default_form=self.default_form,
                default_evaluation_types=self.default_evaluation_types,
            ))

    def to_api_json(self):
        feed = {
            'termId': self.term_id,
            'courseNumber': self.course_number,
            'subjectArea': self.subject_area,
            'catalogId': self.catalog_id,
            'instructionFormat': self.instruction_format,
            'sectionNumber': self.section_num,
            'courseTitle': self.course_title,
        }
        if self.cross_listed_with:
            feed['crossListedWith'] = self.cross_listed_with
        elif self.room_shared_with:
            feed['roomSharedWith'] = self.room_shared_with
        if self.foreign_department_course:
            feed['foreignDepartmentCourse'] = True
        return feed

    def get_evaluation_exports(self, department_id, evaluation_ids, uses_midterm_forms):
        exports = {}
        merged_evaluations = self.merge_evaluations(department_id=department_id, uses_midterm_forms=uses_midterm_forms)
        for e in merged_evaluations:
            if e.get_id() not in evaluation_ids:
                continue
            export_key = e.to_export_key()
            if export_key not in exports:
                exports[export_key] = set()
            exports[export_key].add(e.instructor_uid)
        return exports

    def get_evaluation_feed(self, department_id, uses_midterm_forms, sections_cache=None, evaluation_ids=None):
        if sections_cache:
            evaluation_feed = sections_cache.get(self.course_number)
        else:
            evaluation_feed = fetch_section_cache(department_id, self.term_id, self.course_number)

        if not evaluation_feed:
            merged_evaluations = self.merge_evaluations(department_id=department_id, uses_midterm_forms=uses_midterm_forms)
            evaluation_feed = [e.to_api_json(section=self) for e in merged_evaluations]
            set_section_cache(department_id, self.term_id, self.course_number, evaluation_feed)

        if evaluation_ids:
            evaluation_feed = [e for e in evaluation_feed if e['id'] in evaluation_ids]

        def _sort_key(evaluation):
            course_number = evaluation.get('courseNumber', '')
            evaluation_type = (evaluation.get('evaluationType') or {}).get('name', '')
            department_form = (evaluation.get('departmentForm') or {}).get('name', '')
            instructor = evaluation.get('instructor')
            instructor_name = f"{instructor.get('lastName', '')}, {instructor.get('firstName', '')}" if instructor else ''
            start_date = evaluation.get('startDate', '')
            return f'{course_number}_{evaluation_type}_{department_form}_{instructor_name}_{start_date}'

        evaluation_feed.sort(key=_sort_key)
        return evaluation_feed

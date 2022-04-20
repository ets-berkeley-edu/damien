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
import re

from damien.lib.queries import get_loch_sections_by_ids
from damien.models.evaluation import Evaluation


class Section:

    def __init__(
        self,
        loch_rows,
        evaluations=(),
        instructors=None,
        catalog_listings=(),
        evaluation_type_cache=None,
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
        self.evaluation_type_cache = evaluation_type_cache

        self.set_cross_listed_status(loch_rows)
        self.set_default_form(catalog_listings)

    @classmethod
    def is_visible_by_default(cls, loch_row):
        return (
            loch_row.enrollment_count
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

    def set_cross_listed_status(self, loch_rows):
        self.cross_listed_with = None
        self.room_shared_with = None
        self.foreign_department_course = True
        for r in loch_rows:
            # Any row with a room-share or cross-listing notation applies to the whole section.
            clw = getattr(r, 'cross_listed_with', None)
            if clw and not self.cross_listed_with:
                self.cross_listed_with = clw
            rsw = getattr(r, 'room_shared_with', None)
            if rsw and not self.room_shared_with:
                self.room_shared_with = rsw
            # But a section is treated as belonging to a foreign department only if all rows have the notation.
            fdc = getattr(r, 'foreign_department_course', None)
            if not fdc:
                self.foreign_department_course = False

    def set_default_form(self, catalog_listings):
        # Apply a default form value to courses not cross-listed or room shared.
        self.default_form = None
        if not self.cross_listed_with and not self.room_shared_with:
            for c in catalog_listings:
                if c.subject_area in (self.subject_area, '') and (c.catalog_id is None or re.match(c.catalog_id, self.catalog_id)):
                    self.default_form = c.default_form
                    break

    def merge_evaluations(self, department):
        merged_evaluations = []

        # Multiple loch rows for a single section-instructor pairing are possible.
        loch_rows_by_instructor_uid = {k: list(v) for k, v in groupby(self.loch_rows, key=lambda r: r['instructor_uid'])}
        evaluation_uids = set()

        home_dept_evals = []
        foreign_dept_evals_by_uid = {}

        for instructor_uid, evaluations_for_instructor_uid in groupby(self.evaluations, key=lambda e: e.instructor_uid):
            evaluations_for_instructor_uid = list(evaluations_for_instructor_uid)
            foreign_dept_evals = []
            check_for_conflicts = False
            for evaluation in evaluations_for_instructor_uid:
                if evaluation.department == department:
                    home_dept_evals.append(evaluation)
                else:
                    foreign_dept_evals.append(evaluation)
                if evaluation.status in ('marked', 'confirmed'):
                    check_for_conflicts = True
            if check_for_conflicts:
                if instructor_uid not in foreign_dept_evals_by_uid:
                    foreign_dept_evals_by_uid[instructor_uid] = []
                foreign_dept_evals_by_uid[instructor_uid].extend(foreign_dept_evals)

        # Create one API feed element per visible saved evaluation, merging in data from SIS as needed.
        for evaluation in home_dept_evals:
            evaluation_uids.add(evaluation.instructor_uid)
            if not evaluation.is_visible():
                continue
            # When merging evaluation data for a specific instructor, we prefer in order: 1) loch rows for that specific
            # instructor; 2) loch rows with no instructor; 3) any loch rows available.
            loch_rows_for_uid = loch_rows_by_instructor_uid.get(evaluation.instructor_uid) or loch_rows_by_instructor_uid.get(None) or self.loch_rows
            merged_evaluations.append(Evaluation.merge_transient(
                evaluation.instructor_uid,
                loch_rows_for_uid,
                saved_evaluation=evaluation,
                foreign_dept_evaluations=foreign_dept_evals_by_uid.get(evaluation.instructor_uid, []),
                instructor=self.instructors.get(evaluation.instructor_uid),
                default_form=self.default_form,
                evaluation_type_cache=self.evaluation_type_cache,
            ))

        # Supplement with SIS-only rows.
        for instructor_uid, loch_rows_for_uid in loch_rows_by_instructor_uid.items():
            # Ignore instructor UIDs already handled under saved evaluations.
            if instructor_uid in evaluation_uids:
                continue
            # Ignore rows without an instructor unless we have no saved evaluations.
            if instructor_uid is None and len(self.evaluations):
                continue
            merged_evaluations.append(Evaluation.merge_transient(
                instructor_uid,
                loch_rows_for_uid,
                saved_evaluation=None,
                foreign_dept_evaluations=foreign_dept_evals_by_uid.get(instructor_uid, []),
                instructor=self.instructors.get(instructor_uid),
                default_form=self.default_form,
                evaluation_type_cache=self.evaluation_type_cache,
            ))

        return merged_evaluations

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

    def get_evaluation_exports(self, department, evaluation_ids):
        exports = {}
        merged_evaluations = self.merge_evaluations(department=department)
        for e in merged_evaluations:
            if e.get_id() not in evaluation_ids:
                continue
            export_key = e.to_export_key()
            if export_key not in exports:
                exports[export_key] = set()
            exports[export_key].add(e.instructor_uid)
        return exports

    def get_evaluation_feed(self, department, evaluation_ids=None):
        merged_evaluations = self.merge_evaluations(department=department)
        return [e.to_api_json(section=self) for e in merged_evaluations if not evaluation_ids or e.get_id() in evaluation_ids]

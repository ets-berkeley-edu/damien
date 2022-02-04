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

from damien.lib.util import safe_strftime
from damien.models.evaluation import Evaluation


class Section:

    def __init__(
        self,
        loch_rows,
        evaluations,
        instructors,
        dept_form_cache=None,
        evaluation_type_cache=None,
    ):
        self.term_id = loch_rows[0].term_id
        self.course_number = loch_rows[0].course_number
        self.subject_area = loch_rows[0].subject_area
        self.catalog_id = loch_rows[0].catalog_id
        self.instruction_format = loch_rows[0].instruction_format
        self.section_num = loch_rows[0].section_num
        self.course_title = loch_rows[0].course_title

        self.instructors = instructors
        self.merged_evaluations = []

        # Multiple loch rows for a single section-instructor pairing are possible.
        loch_rows_by_instructor_uid = {k: list(v) for k, v in groupby(loch_rows, key=lambda r: r['instructor_uid'])}

        # Database constraints ensure only one saved evaluation per section-instructor pairing.
        evaluations_by_instructor_uid = {e.instructor_uid: e for e in evaluations}

        instructor_uids = set(loch_rows_by_instructor_uid.keys())
        instructor_uids.update(evaluations_by_instructor_uid.keys())

        for uid in instructor_uids:
            # Skip rows without an instructor if we have an instructor elsewhere.
            if not uid and len(instructor_uids) > 1:
                continue

            # When merging evaluation data for a specific instructor, we prefer in order: 1) loch rows for that specific
            # instructor; 2) loch rows with no instructor; 3) any loch rows available.
            loch_rows_for_uid = loch_rows_by_instructor_uid.get(uid) or loch_rows_by_instructor_uid.get(None) or loch_rows

            # If we have no saved evaluation data for this section-instructor pairing, check for saved evaluation data with no
            # instructor.
            evaluation_for_uid = evaluations_by_instructor_uid.get(uid) or evaluations_by_instructor_uid.get(None)

            # Omit evaluations explicitly marked deleted.
            if evaluation_for_uid and not evaluation_for_uid.is_visible():
                continue

            self.merged_evaluations.append(
                Evaluation.merge_transient(
                    uid,
                    loch_rows_for_uid,
                    evaluation_for_uid,
                    dept_form_cache=dept_form_cache,
                    evaluation_type_cache=evaluation_type_cache,
                ),
            )

    @classmethod
    def is_visible_by_default(cls, loch_row):
        return (
            loch_row.enrollment_count
            and loch_row.instructor_role_code != 'ICNT'
            and loch_row.instruction_format not in {'CLC', 'GRP', 'IND', 'SUP', 'VOL'}
        )

    def to_api_json(self):
        evaluation_feed = []
        for evaluation in self.merged_evaluations:
            dept_form_feed = evaluation.department_form.to_api_json() if evaluation.department_form else None
            eval_type_feed = evaluation.evaluation_type.to_api_json() if evaluation.evaluation_type else None
            evaluation_feed.append({
                'status': evaluation.status,
                'instructor': self.instructors.get(evaluation.instructor_uid),
                'departmentForm': dept_form_feed,
                'evaluationType': eval_type_feed,
                'startDate': safe_strftime(evaluation.start_date, '%Y-%m-%d'),
                'endDate': safe_strftime(evaluation.end_date, '%Y-%m-%d'),
            })
        return {
            'termId': self.term_id,
            'courseNumber': self.course_number,
            'subjectArea': self.subject_area,
            'catalogId': self.catalog_id,
            'instructionFormat': self.instruction_format,
            'sectionNumber': self.section_num,
            'courseTitle': self.course_title,
            'evaluations': evaluation_feed,
        }

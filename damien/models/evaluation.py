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
from damien.lib.util import safe_strftime
from damien.models.base import Base
from damien.models.department_form import DepartmentForm
from damien.models.evaluation_type import EvaluationType
from sqlalchemy.dialects.postgresql import ENUM


evaluation_status_enum = ENUM(
    'marked',
    'confirmed',
    'deleted',
    name='evaluation_status',
    create_type=False,
)


class Evaluation(Base):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)  # noqa: A003
    term_id = db.Column(db.String(4), nullable=False, primary_key=True)
    course_number = db.Column(db.String(5), nullable=False, primary_key=True)
    instructor_uid = db.Column(db.String(80), primary_key=True)
    status = db.Column(evaluation_status_enum)
    department_form_id = db.Column(db.Integer, db.ForeignKey('department_forms.id'))
    evaluation_type_id = db.Column(db.Integer, db.ForeignKey('evaluation_types.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_by = db.Column(db.String(80))
    updated_by = db.Column(db.String(80))

    department_form = db.relationship(
        DepartmentForm.__name__,
        lazy='joined',
    )
    evaluation_type = db.relationship(
        EvaluationType.__name__,
        lazy='joined',
    )

    def __init__(
        self,
        term_id,
        course_number,
        instructor_uid=None,
        status=None,
        department_form_id=None,
        evaluation_type_id=None,
        start_date=None,
        end_date=None,
        created_by=None,
        updated_by=None,
    ):
        self.term_id = term_id
        self.course_number = course_number
        self.instructor_uid = instructor_uid
        self.status = status
        self.department_form_id = department_form_id
        self.evaluation_type_id = evaluation_type_id
        self.start_date = start_date
        self.end_date = end_date
        self.created_by = created_by
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<Evaluation id={self.id},
                    term_id={self.term_id},
                    course_number={self.course_number},
                    instructor_uid={self.instructor_uid},
                    status={self.status},
                    department_form_id={self.department_form_id},
                    evaluation_type_id={self.evaluation_type_id},
                    start_date={self.start_date},
                    end_date={self.end_date},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at},
                    updated_by={self.updated_by}>
                """

    @classmethod
    def create(
            cls,
            term_id,
            course_number,
            instructor_uid=None,
            status=None,
            department_form_id=None,
            evaluation_type_id=None,
            start_date=None,
            end_date=None,
            created_by=None,
            updated_by=None,
    ):
        evaluation = cls(
            term_id=term_id,
            course_number=course_number,
            instructor_uid=instructor_uid,
            status=status,
            department_form_id=department_form_id,
            evaluation_type_id=evaluation_type_id,
            start_date=start_date,
            end_date=end_date,
            created_by=created_by,
            updated_by=updated_by,
        )
        db.session.add(evaluation)
        std_commit()
        return evaluation

    @classmethod
    def merge_transient(
        cls,
        uid,
        loch_rows,
        saved_evaluation=None,
        instructor=None,
        default_form=None,
        evaluation_type_cache=None,
    ):
        transient_evaluation = cls(
            term_id=loch_rows[0].term_id,
            course_number=loch_rows[0].course_number,
            instructor_uid=uid,
        )

        if saved_evaluation:
            transient_evaluation.id = saved_evaluation.id

        if saved_evaluation and saved_evaluation.status:
            transient_evaluation.status = saved_evaluation.status
        else:
            transient_evaluation.status = None

        all_eval_types = evaluation_type_cache or {et.name: et for et in EvaluationType.query.all()}

        transient_evaluation.set_department_form(saved_evaluation, default_form)
        transient_evaluation.set_evaluation_type(saved_evaluation, instructor, all_eval_types)
        transient_evaluation.set_start_date(loch_rows, saved_evaluation)
        transient_evaluation.set_end_date(loch_rows, saved_evaluation)
        transient_evaluation.set_last_updated(loch_rows, saved_evaluation)

        return transient_evaluation

    @classmethod
    def fetch_by_course_numbers(cls, term_id, course_numbers):
        results = cls.query.filter(cls.term_id == term_id, cls.course_number.in_(course_numbers)).order_by(cls.course_number).all()
        return {k: list(v) for k, v in groupby(results, key=lambda r: r.course_number)}

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id)
        return query.first()

    @classmethod
    def duplicate_bulk(cls, evaluation_ids):
        # TODO
        pass

    @classmethod
    def update_bulk(cls, evaluation_ids, status):
        evaluations = []
        for evaluation_id in evaluation_ids:
            evaluation = None
            parsed = _parse_transient_id(evaluation_id)
            if parsed:
                evaluation = cls(**parsed)
            else:
                try:
                    evaluation = cls.find_by_id(int(evaluation_id))
                except ValueError:
                    evaluation = None
            if not evaluation:
                continue
            evaluation.status = status
            db.session.add(evaluation)
            evaluations.append(evaluation)
        std_commit()
        return [evaluation.id for e in evaluations]

    def is_visible(self):
        return self.status != 'deleted'

    def set_department_form(self, saved_evaluation, default_form):
        if saved_evaluation and saved_evaluation.department_form:
            self.department_form = saved_evaluation.department_form
        elif default_form:
            # TODO Do not set if cross-listed
            self.department_form = default_form

    def set_evaluation_type(self, saved_evaluation, instructor, all_eval_types):
        if saved_evaluation and saved_evaluation.evaluation_type:
            self.evaluation_type = saved_evaluation.evaluation_type
        else:
            # TODO Leave blank if department_form above is set to LAW or SPANISH, otherwise set based on instructor affiliation.
            if self.department_form and self.department_form.name in ('LAW', 'SPANISH'):
                return
            elif instructor and 'STUDENT-TYPE' in instructor['affiliations']:
                self.evaluation_type = all_eval_types.get('G')
            elif instructor and 'ACADEMIC' in instructor['affiliations']:
                self.evaluation_type = all_eval_types.get('F')

    def set_start_date(self, loch_rows, saved_evaluation):
        if saved_evaluation and saved_evaluation.start_date:
            self.start_date = saved_evaluation.start_date
        else:
            self.start_date = min((r['meeting_start_date'] for r in loch_rows if r['meeting_start_date']), default=None)

    def set_end_date(self, loch_rows, saved_evaluation):
        if saved_evaluation and saved_evaluation.end_date:
            self.end_date = saved_evaluation.end_date
        else:
            self.end_date = max((r['meeting_end_date'] for r in loch_rows if r['meeting_end_date']), default=None)

    def set_last_updated(self, loch_rows, saved_evaluation):
        updates = [r['created_at'] for r in loch_rows]
        if saved_evaluation:
            updates.append(saved_evaluation.updated_at)
        self.last_updated = max(updates)

    def get_id(self):
        if self.id:
            return self.id
        else:
            # Fallback id string for Evaluation instances that are created for the department/section API but not saved to the database.
            return f'_{self.term_id}_{self.course_number}_{self.instructor_uid}'

    def to_api_json(self, section):
        dept_form_feed = self.department_form.to_api_json() if self.department_form else None
        eval_type_feed = self.evaluation_type.to_api_json() if self.evaluation_type else None
        feed = section.to_api_json()
        feed.update({
            'id': self.get_id(),
            'status': self.status,
            'instructor': section.instructors.get(self.instructor_uid),
            'departmentForm': dept_form_feed,
            'evaluationType': eval_type_feed,
            'startDate': safe_strftime(self.start_date, '%Y-%m-%d'),
            'endDate': safe_strftime(self.end_date, '%Y-%m-%d'),
            'lastUpdated': safe_strftime(self.last_updated, '%Y-%m-%d'),
        })
        return feed


def _parse_transient_id(transient_id):
    if not isinstance(transient_id, str):
        return None
    components = transient_id.split('_')
    if len(components) != 4:
        return None
    return {
        'term_id': components[1],
        'course_number': components[2],
        'instructor_uid': components[3],
    }

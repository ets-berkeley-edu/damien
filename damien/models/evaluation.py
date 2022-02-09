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
        return f"""<Evaluation term_id={self.term_id},
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
        dept_form_cache=None,
        evaluation_type_cache=None,
    ):
        transient_evaluation = cls(
            term_id=loch_rows[0].term_id,
            course_number=loch_rows[0].course_number,
            instructor_uid=uid,
        )

        if saved_evaluation and saved_evaluation.status:
            transient_evaluation.status = saved_evaluation.status
        else:
            transient_evaluation.status = None

        all_dept_forms = dept_form_cache or {df.name: df for df in DepartmentForm.query.all()}
        all_eval_types = evaluation_type_cache or {et.name: et for et in EvaluationType.query.all()}

        transient_evaluation.set_department_form(loch_rows, saved_evaluation, all_dept_forms)
        transient_evaluation.set_evaluation_type(loch_rows, saved_evaluation, all_eval_types)
        transient_evaluation.set_start_date(loch_rows, saved_evaluation)
        transient_evaluation.set_end_date(loch_rows, saved_evaluation)
        transient_evaluation.set_last_updated(loch_rows, saved_evaluation)

        return transient_evaluation

    @classmethod
    def fetch_by_course_numbers(cls, term_id, course_numbers):
        results = cls.query.filter(cls.term_id == term_id, cls.course_number.in_(course_numbers)).all()
        return {r.course_number: r for r in results}

    def is_visible(self):
        return self.status != 'deleted'

    def set_department_form(self, loch_rows, saved_evaluation, all_dept_forms):
        if saved_evaluation and saved_evaluation.department_form_id:
            self.department_form_id = saved_evaluation.department_form_id
        else:
            # TODO set department form for non-cross-listed courses
            self.department_form_id = None

    def set_evaluation_type(self, loch_rows, saved_evaluation, all_eval_types):
        if saved_evaluation and saved_evaluation.evaluation_type_id:
            self.evaluation_type_id = saved_evaluation.evaluation_type_id
        else:
            # TODO Leave blank if department_form above is set to LAW or SPANISH, otherwise set based on instructor affiliation.
            self.evaluation_type_id = None

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
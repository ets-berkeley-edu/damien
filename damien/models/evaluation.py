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

from collections import namedtuple
from datetime import timedelta
from itertools import groupby

from damien import db, std_commit
from damien.lib.queries import get_default_meeting_dates, refresh_additional_instructors
from damien.lib.util import safe_strftime
from damien.models.base import Base
from damien.models.department_form import DepartmentForm
from damien.models.evaluation_type import EvaluationType
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import and_, orm, update
from sqlalchemy.dialects.postgresql import ENUM


evaluation_status_enum = ENUM(
    'marked',
    'confirmed',
    'deleted',
    'ignore',
    name='evaluation_status',
    create_type=False,
)


"""
Department form, evaluation type, and end date are the three attributes that may be assigned multiple distinct values for
the same course number. When it comes time to export, we avoid conflicts in Blue by generating additional dynamic course ids
in cases where these attributes vary. To keep these multiple courses from getting confused, we key evaluations by a data structure
derived from the course number plus variable attributes.
"""

EvaluationExportKey = namedtuple('EvaluationExportKey', ['course_number', 'department_form', 'evaluation_type', 'start_date', 'end_date'])


class Evaluation(Base):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)  # noqa: A003
    term_id = db.Column(db.String(4), nullable=False, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True)
    course_number = db.Column(db.String(5), nullable=False, primary_key=True)
    instructor_uid = db.Column(db.String(80))
    status = db.Column(evaluation_status_enum)
    department_form_id = db.Column(db.Integer, db.ForeignKey('department_forms.id'))
    evaluation_type_id = db.Column(db.Integer, db.ForeignKey('evaluation_types.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    valid = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String(80))
    updated_by = db.Column(db.String(80))

    department = db.relationship('Department', back_populates='evaluations', lazy='joined')

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
        department_id=None,
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
        self.department_id = department_id
        self.instructor_uid = instructor_uid if instructor_uid != 'None' else None
        self.status = status
        self.department_form_id = department_form_id
        self.evaluation_type_id = evaluation_type_id
        self.start_date = start_date
        self.end_date = end_date
        self.created_by = created_by
        self.updated_by = updated_by
        self._init_on_load()

    @orm.reconstructor
    def _init_on_load(self):
        self.conflicts = {
            'departmentForm': [],
            'evaluationType': [],
            'evaluationPeriod': [],
        }
        self.meeting_start_date = None
        self.meeting_end_date = None

    def __repr__(self):
        return f"""<Evaluation id={self.id},
                    term_id={self.term_id},
                    department_id={self.department_id},
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
            department_id=None,
            instructor_uid=None,
            status=None,
            department_form_id=None,
            evaluation_type_id=None,
            start_date=None,
            end_date=None,
    ):
        evaluation = cls(
            term_id=term_id,
            course_number=course_number,
            department_id=department_id,
            instructor_uid=instructor_uid,
            status=status,
            department_form_id=department_form_id,
            evaluation_type_id=evaluation_type_id,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.get_uid(),
            updated_by=current_user.get_uid(),
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
        foreign_dept_evaluations=(),
        instructor=None,
        default_form=None,
        evaluation_type_cache=None,
    ):
        transient_evaluation = cls(
            term_id=loch_rows[0].term_id,
            course_number=loch_rows[0].course_number,
            instructor_uid=uid,
        )

        transient_evaluation.set_status(saved_evaluation, foreign_dept_evaluations)

        if saved_evaluation and saved_evaluation.department_id:
            transient_evaluation.department_id = saved_evaluation.department_id
        else:
            transient_evaluation.department_id = None

        all_eval_types = evaluation_type_cache or {et.name: et for et in EvaluationType.query.all()}

        transient_evaluation.set_department_form(saved_evaluation, foreign_dept_evaluations, default_form)
        transient_evaluation.set_evaluation_type(saved_evaluation, foreign_dept_evaluations, instructor, all_eval_types)
        transient_evaluation.set_dates(loch_rows, foreign_dept_evaluations, saved_evaluation)
        transient_evaluation.set_last_updated(loch_rows, saved_evaluation)

        transient_evaluation.update_validity(saved_evaluation, foreign_dept_evaluations)

        if saved_evaluation:
            transient_evaluation.id = saved_evaluation.id
            # Underscore hack needed because setting the "department" relationship on a transient evaluation results
            # in an attempted save and a primary-key conflict.
            transient_evaluation._department = saved_evaluation.department

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
    def from_id(cls, evaluation_id):
        evaluation = None
        parsed = _parse_transient_id(evaluation_id)
        if parsed:
            evaluation = cls(**parsed)
        else:
            try:
                evaluation = cls.find_by_id(int(evaluation_id))
            except ValueError:
                evaluation = None
        return evaluation

    @classmethod
    def duplicate_bulk(cls, department_id, evaluation_ids, department, fields=None):
        original_feed = []
        if fields:
            original_feed = department.evaluations_feed(app.config['CURRENT_TERM_ID'], evaluation_ids=evaluation_ids)

        evaluations = []
        for evaluation_id in evaluation_ids:
            evaluation = cls.from_id(evaluation_id)
            if not evaluation:
                continue

            duplicate = evaluation.duplicate()
            if fields:
                filtered_fields = {k: v for k, v in fields.items() if k != 'status'}
                original_evaluation_feed = next((f for f in original_feed if f['id'] == evaluation_id), None)
                duplicate.set_fields(filtered_fields, original_evaluation_feed)

            if not evaluation.department_id:
                evaluation.department_id = department_id
            duplicate.department_id = department_id

            duplicate.created_by = current_user.get_uid()
            duplicate.updated_by = current_user.get_uid()

            db.session.add(evaluation)
            db.session.add(duplicate)
            evaluations.extend([evaluation, duplicate])
        std_commit()
        return [e.id for e in evaluations]

    @classmethod
    def update_bulk(cls, department_id, evaluation_ids, fields):
        evaluations = []
        for evaluation_id in evaluation_ids:
            evaluation = cls.from_id(evaluation_id)
            if not evaluation:
                continue
            evaluation.set_fields(fields)
            evaluation.department_id = department_id
            evaluation.updated_by = current_user.get_uid()
            db.session.add(evaluation)
            evaluations.append(evaluation)
        std_commit()
        return [e.id for e in evaluations]

    @classmethod
    def update_evaluation_status(cls, term_id, course_number, instructor_uid, status):
        # Keep evaluation status from different departments in sync per term/course/instructor, unless that
        # status is 'ignore' (or, if enabled, 'deleted'), which is confined to individual departments.
        db.session.execute(update(cls).where(and_(
            cls.term_id == term_id,
            cls.course_number == course_number,
            cls.instructor_uid == instructor_uid,
            cls.status.in_(['confirmed', 'marked', None]),
        )).values(status=status))

    @classmethod
    def get_confirmed(cls, term_id):
        filters = [cls.term_id == term_id, cls.status == 'confirmed']
        return cls.query.where(and_(*filters)).all()

    @classmethod
    def get_invalid(cls, term_id, status=None, evaluation_ids=None):
        filters = [cls.term_id == term_id, cls.valid == False]  # noqa: E712
        if status:
            filters.append(cls.status == status)
        if evaluation_ids:
            filters.append(cls.id.in_(evaluation_ids))
        return cls.query.where(and_(*filters)).all()

    def is_transient(self):
        return self.id is None

    def is_visible(self):
        return self.status != 'deleted'

    def duplicate(self):
        return self.__class__(
            term_id=self.term_id,
            course_number=self.course_number,
            department_id=self.department_id,
            instructor_uid=self.instructor_uid,
            status=None,
            department_form_id=self.department_form_id,
            evaluation_type_id=self.evaluation_type_id,
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def set_fields(self, fields, original_evaluation_feed=None):
        if 'departmentForm' in fields:
            self.department_form = fields['departmentForm']
        if 'startDate' in fields:
            self.start_date = fields['startDate']
        if 'evaluationType' in fields:
            self.evaluation_type = fields['evaluationType']
        if 'instructorUid' in fields:
            self.instructor_uid = fields['instructorUid']
            refresh_additional_instructors([self.instructor_uid])
        if 'status' in fields:
            self.status = fields['status']
            if fields['status'] in ('marked', 'confirmed', None):
                self.__class__.update_evaluation_status(self.term_id, self.course_number, self.instructor_uid, fields['status'])

        if fields.get('midterm'):
            if original_evaluation_feed and original_evaluation_feed.get('departmentForm'):
                midterm_form = DepartmentForm.find_by_name(original_evaluation_feed['departmentForm']['name'] + '_MID')
                if midterm_form:
                    self.department_form = midterm_form

    def set_department_form(self, saved_evaluation, foreign_dept_evaluations, default_form):
        if saved_evaluation and saved_evaluation.department_form:
            self.department_form = saved_evaluation.department_form
            for fde in foreign_dept_evaluations:
                if fde.department_form and fde.department_form != self.department_form:
                    self.mark_conflict(fde, 'departmentForm', saved_evaluation, self.department_form.name, fde.department_form.name)
        else:
            for fde in foreign_dept_evaluations:
                if fde.department_form:
                    self.department_form = fde.department_form
                    break
        if default_form and not self.department_form:
            self.department_form = default_form

    def set_evaluation_type(self, saved_evaluation, foreign_dept_evaluations, instructor, all_eval_types):
        if saved_evaluation and saved_evaluation.evaluation_type:
            self.evaluation_type = saved_evaluation.evaluation_type
            for fde in foreign_dept_evaluations:
                if fde.evaluation_type and fde.evaluation_type != self.evaluation_type:
                    self.mark_conflict(fde, 'evaluationType', saved_evaluation, self.evaluation_type.name, fde.evaluation_type.name)
        else:
            for fde in foreign_dept_evaluations:
                if fde.evaluation_type:
                    self.evaluation_type = fde.evaluation_type
                    break
        if not self.evaluation_type:
            # TODO Leave blank if department_form above is set to LAW or SPANISH, otherwise set based on instructor affiliation.
            if self.department_form and self.department_form.name in ('LAW', 'SPANISH'):
                return
            elif instructor and 'STUDENT-TYPE' in instructor.get('affiliations', []):
                self.evaluation_type = all_eval_types.get('G')
            elif instructor and 'ACADEMIC' in instructor.get('affiliations', []):
                self.evaluation_type = all_eval_types.get('F')

    def set_dates(self, loch_rows, foreign_dept_evaluations, saved_evaluation):
        self.meeting_start_date = min((r['meeting_start_date'] for r in loch_rows if r['meeting_start_date']), default=None)
        self.meeting_end_date = max((r['meeting_end_date'] for r in loch_rows if r['meeting_end_date']), default=None)
        default_meeting_dates = get_default_meeting_dates(self.term_id)
        if not self.meeting_start_date:
            self.meeting_start_date = default_meeting_dates['start_date']
        if not self.meeting_end_date:
            self.meeting_end_date = default_meeting_dates['end_date']

        if saved_evaluation and saved_evaluation.start_date:
            self.start_date = saved_evaluation.start_date
            for fde in foreign_dept_evaluations:
                if fde.start_date and fde.start_date != self.start_date:
                    self.mark_conflict(
                        fde,
                        'evaluationPeriod',
                        saved_evaluation,
                        safe_strftime(self.start_date, '%Y-%m-%d'),
                        safe_strftime(fde.start_date, '%Y-%m-%d'),
                    )
        else:
            for fde in foreign_dept_evaluations:
                if fde.start_date:
                    self.start_date = fde.start_date
                    break

        if self.start_date:
            if (self.start_date - self.meeting_start_date < timedelta(days=76)):
                self.end_date = self.start_date + timedelta(days=13)
            else:
                self.end_date = self.start_date + timedelta(days=20)
        else:
            self.end_date = self.meeting_end_date

            # The most common meeting end date is the Friday before finals week. During Spring and Fall terms, we bump these two days forward
            # to the Sunday before finals.
            if self.end_date == default_meeting_dates['end_date'] and self.term_id[-1:] in {'2', '8'}:
                self.end_date = self.end_date + timedelta(days=2)

            if (self.end_date - self.meeting_start_date) < timedelta(days=90):
                self.start_date = self.end_date - timedelta(days=13)
            else:
                self.start_date = self.end_date - timedelta(days=20)

    def set_status(self, saved_evaluation, foreign_dept_evaluations):
        if saved_evaluation and saved_evaluation.status:
            self.status = saved_evaluation.status
        else:
            for fde in foreign_dept_evaluations:
                if fde.status == 'marked' and self.status is None:
                    self.status = 'marked'
                elif fde.status == 'confirmed' and self.status in ('confirmed', None):
                    self.status = 'confirmed'

    def set_last_updated(self, loch_rows, saved_evaluation):
        updates = [r['created_at'] for r in loch_rows]
        if saved_evaluation:
            updates.append(saved_evaluation.updated_at)
        self.last_updated = max(updates)

    def mark_conflict(self, foreign_dept_evaluation, key, saved_evaluation, self_value, other_value):
        self.conflicts[key].append({'department': foreign_dept_evaluation.department.dept_name, 'value': other_value})
        foreign_dept_evaluation.conflicts[key].append({'department': saved_evaluation.department.dept_name, 'value': self_value})

    def update_validity(self, saved_evaluation, foreign_dept_evaluations):
        self.valid = True
        if saved_evaluation:
            updated_validity = True
            if self.status in ('marked', 'confirmed'):
                if not self.department_form or not self.evaluation_type:
                    updated_validity = False
                if next((v for v in self.conflicts.values() if len(v)), None):
                    updated_validity = False
            if updated_validity != saved_evaluation.valid:
                saved_evaluation.valid = updated_validity
                db.session.add(saved_evaluation)
            self.valid = saved_evaluation.valid
        for fde in foreign_dept_evaluations:
            updated_validity = True
            if self.status in ('marked', 'confirmed'):
                if next((v for v in fde.conflicts.values() if len(v)), None):
                    updated_validity = False
                if not self.department_form and not fde.department_form:
                    updated_validity = False
                if not self.evaluation_type and not fde.evaluation_type:
                    updated_validity = False
            if updated_validity != fde.valid:
                fde.valid = updated_validity
                db.session.add(fde)
        std_commit()

    # Fallback id string for Evaluation instances that are created for the department/section API but not saved to the database.
    def transient_id(self):
        return f'_{self.term_id}_{self.course_number}_{self.instructor_uid}'

    def get_id(self):
        return self.id or self.transient_id()

    def to_api_json(self, section):
        dept_form_feed = self.department_form.to_api_json() if self.department_form else None
        eval_type_feed = self.evaluation_type.to_api_json() if self.evaluation_type else None

        feed_status = 'review' if self.status == 'marked' else self.status

        feed = section.to_api_json()
        feed.update({
            'id': self.get_id(),
            'transientId': self.transient_id(),
            'status': feed_status,
            'instructor': section.instructors.get(self.instructor_uid),
            'departmentForm': dept_form_feed,
            'evaluationType': eval_type_feed,
            'startDate': safe_strftime(self.start_date, '%Y-%m-%d'),
            'endDate': safe_strftime(self.end_date, '%Y-%m-%d'),
            'meetingDates': {
                'start': safe_strftime(self.meeting_start_date, '%Y-%m-%d'),
                'end': safe_strftime(self.meeting_end_date, '%Y-%m-%d'),
            },
            'modular': is_modular(self.start_date, self.end_date),
            'lastUpdated': safe_strftime(self.last_updated, '%Y-%m-%d'),
            'conflicts': {},
            'valid': self.valid,
        })
        dept = self.department or (hasattr(self, '_department') and self._department)
        if dept:
            feed['department'] = {
                'id': dept.id,
                'name': dept.dept_name,
            }
        for k, v in self.conflicts.items():
            if v:
                feed['conflicts'][k] = v
        return feed

    def to_export_key(self):
        return EvaluationExportKey(
            course_number=self.course_number,
            department_form=self.department_form.name,
            evaluation_type=self.evaluation_type.name,
            start_date=self.start_date,
            end_date=self.end_date,
        )


def is_modular(start_date, end_date):
    return True if start_date and end_date and end_date - start_date < timedelta(days=20) else False


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

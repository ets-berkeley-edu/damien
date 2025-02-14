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

from collections import namedtuple
from datetime import date, timedelta
from itertools import groupby

from damien import db, std_commit
from damien.lib.cache import clear_department_cache, clear_section_cache
from damien.lib.queries import get_default_meeting_dates, refresh_additional_instructors
from damien.lib.util import isoformat, safe_strftime
from damien.models.base import Base
from damien.models.department_form import DepartmentForm
from damien.models.evaluation_type import EvaluationType
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import and_, func, orm, text, update
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
                    valid={self.valid},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at},
                    updated_by={self.updated_by}>
                """

    @classmethod
    def update_evaluation_status(cls, term_id, course_number, instructor_uid, status):
        # Keep evaluation status from different departments in sync per term/course/instructor, unless that
        # status is 'ignore' (or, if enabled, 'deleted'), which is confined to individual departments.
        conditions = and_(
            cls.term_id == term_id,
            cls.course_number == course_number,
            cls.instructor_uid == instructor_uid,
            cls.status.in_(['confirmed', 'marked', None]),
        )
        dept_ids = set([r.department_id for r in cls.query.filter(conditions).with_entities(cls.department_id).all()])
        db.session.execute(update(cls).where(conditions).values(status=status))
        for dept_id in dept_ids:
            clear_department_cache(dept_id, term_id)
        clear_section_cache(term_id, course_number)

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
    def duplicate_bulk(cls, department, term_id, evaluation_ids, fields=None):
        original_feed = []
        if fields:
            original_feed = department.evaluations_feed(term_id, evaluation_ids=evaluation_ids)
        evaluations = []
        for evaluation_id in evaluation_ids:
            evaluation = cls.from_id(evaluation_id)
            if not evaluation:
                continue

            original_evaluation_feed = next((f for f in original_feed if f['id'] == evaluation_id), None)
            duplicate = evaluation.duplicate()
            if fields:
                filtered_fields = {k: v for k, v in fields.items() if k != 'status'}
                duplicate.set_fields(filtered_fields, original_evaluation_feed)

            if not evaluation.department_id:
                evaluation.department_id = department.id
            duplicate.department_id = department.id

            if original_evaluation_feed:
                _set_defaults(evaluation, original_evaluation_feed)
                _set_defaults(duplicate, original_evaluation_feed)

            if not evaluation.created_by:
                evaluation.created_by = current_user.get_uid()
            evaluation.updated_by = current_user.get_uid()
            duplicate.created_by = current_user.get_uid()
            duplicate.updated_by = current_user.get_uid()

            db.session.add(evaluation)
            db.session.add(duplicate)
            evaluations.extend([evaluation, duplicate])

            clear_section_cache(term_id, evaluation.course_number)

        clear_department_cache(department.id, term_id)
        std_commit()
        return [e.id for e in evaluations]

    @classmethod
    def fetch_by_course_numbers(cls, term_id, course_numbers):
        results = cls.query.filter(cls.term_id == term_id, cls.course_number.in_(course_numbers)).order_by(cls.course_number).all()
        return {k: list(v) for k, v in groupby(results, key=lambda r: r.course_number)}

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id)
        return query.first()

    @classmethod
    def find_potential_conflicts(cls, evaluation_ids, fields, defaults):
        if defaults and len(defaults):
            defaults_cte = f"""
                    default_values (evaluation_id, department_form_id, evaluation_type_id, start_date) AS (
                        VALUES {','.join([str(v) for v in defaults])}
                    ),"""
            defaults_join = 'LEFT JOIN default_values d ON e.id = d.evaluation_id'
            existing = {
                'department_form_id': 'COALESCE(e.department_form_id, d.department_form_id)',
                'evaluation_type_id': 'COALESCE(e.evaluation_type_id, d.evaluation_type_id)',
                'start_date': 'COALESCE(e.start_date, DATE(d.start_date))',
            }
        else:
            defaults_cte = ''
            defaults_join = ''
            existing = {
                'department_form_id': 'e.department_form_id',
                'evaluation_type_id': 'e.evaluation_type_id',
                'start_date': 'e.start_date',
            }
        params = {'evaluation_ids': evaluation_ids}
        confirming = {
            'department_form_id': existing['department_form_id'],
            'evaluation_type_id': existing['evaluation_type_id'],
            'instructor_uid': 'c.instructor_uid',
            'start_date': existing['start_date'],
        }
        if fields.get('departmentForm'):
            params.update({'department_form_id': fields.get('departmentForm').id})
            confirming.update({'department_form_id': ':department_form_id'})
        if fields.get('evaluationType'):
            params.update({'evaluation_type_id': fields.get('evaluationType').id})
            confirming.update({'evaluation_type_id': ':evaluation_type_id'})
        if fields.get('instructorUid'):
            params.update({'instructor_uid': f"{fields.get('instructorUid')}"})
            confirming.update({'instructor_uid': ':instructor_uid'})
        if fields.get('startDate'):
            params.update({'start_date': f"{fields.get('startDate')}"})
            confirming.update({'start_date': 'DATE(:start_date)'})

        query = f"""WITH {defaults_cte}
                    confirming AS (
                        SELECT e.id, e.term_id, e.course_number, e.instructor_uid, e.status, e.department_id,
                                {confirming['department_form_id']} AS department_form_id,
                                {confirming['evaluation_type_id']} AS evaluation_type_id,
                                {confirming['start_date']} AS start_date,
                                df.name AS department_form_name
                        FROM evaluations e
                        {defaults_join}
                        JOIN department_forms df ON {confirming['department_form_id']} = df.id
                        WHERE e.id = ANY(:evaluation_ids)
                    )
                    SELECT * FROM evaluations e
                    {defaults_join}
                    JOIN confirming c
                      ON e.term_id = c.term_id
                      AND e.course_number = c.course_number
                      AND e.instructor_uid = {confirming['instructor_uid']}
                      AND NOT e.id = c.id
                      AND (
                          {existing['department_form_id']} != c.department_form_id
                          OR {existing['evaluation_type_id']} != c.evaluation_type_id
                          OR {existing['start_date']} != c.start_date
                      )
                    JOIN department_forms edf ON {existing['department_form_id']} = edf.id
                    WHERE (
                        e.status IN ('marked', 'confirmed')
                        OR (e.status IS NULL AND e.department_id <> c.department_id)
                        OR e.id = ANY(:evaluation_ids)
                    )
                    AND (
                        edf.name <> c.department_form_name || '_MID' AND c.department_form_name <> edf.name || '_MID'
                    )"""
        results = db.session.execute(query, params).fetchall()
        app.logger.info(f'Evaluation find_potential_conflicts query returned {len(results)} results: {query}\n{params}')
        return results

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
    def get_confirmed(cls, term_id):
        filters = [cls.term_id == term_id, cls.status == 'confirmed']
        return cls.query.where(and_(*filters)).order_by(cls.department_id, cls.id).all()

    @classmethod
    def get_duplicates(cls, evaluation, default_form):
        department_form = evaluation.department_form or default_form
        if not department_form:
            return []
        params = {
            'department_form_name': department_form.name,
            'department_form_name_mid': f'{department_form.name}_MID',
            'evaluation_id': evaluation.id,
            'term_id': evaluation.term_id,
            'course_number': evaluation.course_number,
            'department_id': evaluation.department_id,
            'instructor_uid': evaluation.instructor_uid,
        }
        query = text(
            """SELECT e.id, e.term_id, e.course_number, e.instructor_uid, e.status, e.department_form_id, e.evaluation_type_id,
                e.start_date, e.end_date, e.created_at, e.created_by, e.updated_at, e.updated_by, e.department_id, e.valid,
                df.id AS df_department_form_id,
                df.name AS department_form_name,
                df.created_at AS department_form_created_at,
                df.updated_at AS department_form_updated_at,
                df.deleted_at AS department_form_deleted_at,
                et.id AS et_evaluation_type_id,
                et.name AS evaluation_type_name,
                et.created_at AS evaluation_type_created_at,
                et.updated_at AS evaluation_type_updated_at,
                et.deleted_at AS evaluation_type_deleted_at
            FROM evaluations e
            LEFT JOIN department_forms df
                ON e.department_form_id = df.id
            LEFT JOIN evaluation_types et
                ON e.evaluation_type_id = et.id
            WHERE e.id <> :evaluation_id
            AND e.term_id = :term_id
            AND e.course_number = :course_number
            AND e.department_id = :department_id
            AND e.instructor_uid = :instructor_uid
            AND e.status IN ('confirmed', 'marked')
            AND NOT (df.name = :department_form_name_mid OR df.name || '_MID' = :department_form_name)
            """,
        ).columns(
            Evaluation.id,
            Evaluation.term_id,
            Evaluation.course_number,
            Evaluation.instructor_uid,
            Evaluation.status,
            Evaluation.department_form_id,
            Evaluation.evaluation_type_id,
            Evaluation.start_date,
            Evaluation.end_date,
            Evaluation.created_at,
            Evaluation.created_by,
            Evaluation.updated_at,
            Evaluation.updated_by,
            Evaluation.department_id,
            Evaluation.valid,
            DepartmentForm.id,
            DepartmentForm.name,
            DepartmentForm.created_at,
            DepartmentForm.updated_at,
            DepartmentForm.deleted_at,
            EvaluationType.id,
            EvaluationType.name,
            EvaluationType.created_at,
            EvaluationType.updated_at,
            EvaluationType.deleted_at,
        ).bindparams(**params)
        orm_sql = cls.query.from_statement(query).options(
            orm.contains_eager(Evaluation.department_form),
        ).options(
            orm.contains_eager(Evaluation.evaluation_type),
        )
        results = orm_sql.all()
        if len(results):
            app.logger.info(f'Evaluation get_duplicates query returned {len(results)} results: {query}\n{params}')
        return results

    @classmethod
    def get_invalid(cls, term_id, status=None, evaluation_ids=None):
        filters = [cls.term_id == term_id, cls.valid == False]  # noqa: E712
        if status:
            filters.append(cls.status == status)
        if evaluation_ids:
            filters.append(cls.id.in_(evaluation_ids))
        return cls.query.where(and_(*filters)).all()

    @classmethod
    def get_last_update(cls, department_id, term_id):
        filters = [
            cls.department_id == department_id,
            cls.term_id == term_id,
        ]
        return db.session.query(func.max(cls.updated_at)).where(and_(*filters)).scalar()

    @classmethod
    def merge_transient(
        cls,
        uid,
        loch_rows,
        saved_evaluation=None,
        foreign_dept_evaluations=(),
        instructor=None,
        default_form=None,
        default_evaluation_types=None,
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

        related_evaluations = foreign_dept_evaluations
        if saved_evaluation and transient_evaluation.status in ['marked', 'confirmed']:
            related_evaluations = related_evaluations + cls.get_duplicates(saved_evaluation, default_form)

        transient_evaluation.set_department_form(saved_evaluation, related_evaluations, default_form)
        transient_evaluation.set_evaluation_type(saved_evaluation, related_evaluations, instructor, default_evaluation_types)
        transient_evaluation.set_dates(loch_rows, related_evaluations, saved_evaluation)
        transient_evaluation.set_last_updated(loch_rows, saved_evaluation)
        transient_evaluation.update_validity(saved_evaluation, related_evaluations)

        if saved_evaluation:
            transient_evaluation.id = saved_evaluation.id
            # Underscore hack needed because setting the "department" relationship on a transient evaluation results
            # in an attempted save and a primary-key conflict.
            transient_evaluation._department = saved_evaluation.department

        return transient_evaluation

    @classmethod
    def update_bulk(cls, department_id, evaluation_ids, fields, evaluations_feed=None):
        evaluations = []
        term_id = None
        for evaluation_id in evaluation_ids:
            evaluation = cls.from_id(evaluation_id)
            if not evaluation:
                app.logger.info(f'Evaluation with ID {evaluation_id} not found.')
                continue
            original_evaluation_feed = next((f for f in evaluations_feed if f['id'] == evaluation_id), None) if evaluations_feed else None
            evaluation.set_fields(fields, original_evaluation_feed)
            if not evaluation.created_by:
                evaluation.created_by = current_user.get_uid()
            evaluation.department_id = department_id
            evaluation.updated_by = current_user.get_uid()
            db.session.add(evaluation)
            evaluations.append(evaluation)
            clear_section_cache(evaluation.term_id, evaluation.course_number)
            term_id = evaluation.term_id

        if term_id:
            clear_department_cache(department_id, term_id)

        std_commit()
        return [e.id for e in evaluations]

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

    def get_default_evaluation_dates(self, default_meeting_dates):
        end_date = self.meeting_end_date or default_meeting_dates['end_date']
        # The most common meeting end date is the Friday before finals week. During Spring and Fall terms, we bump these two days forward
        # to the Sunday before finals.
        if end_date == default_meeting_dates['end_date'] and self.term_id[-1:] in {'2', '8'}:
            end_date = end_date + timedelta(days=2)
        if (end_date - (self.meeting_start_date or default_meeting_dates['start_date'])) < timedelta(days=90):
            start_date = end_date - timedelta(days=13)
        else:
            start_date = end_date - timedelta(days=20)
        return (start_date, end_date)

    def get_id(self):
        return self.id or self.transient_id()

    def is_midterm(self):
        return True if self.department_form and self.department_form.name.endswith('_MID') else False

    def is_transient(self):
        return self.id is None

    def is_valid(self, foreign_department_evaluation=None):
        if self.status in ('marked', 'confirmed'):
            if next((v for v in (foreign_department_evaluation or self).conflicts.values() if len(v)), None):
                return False
            if not (self.department_form or (foreign_department_evaluation and foreign_department_evaluation.department_form)):
                return False
            if not (self.evaluation_type or (foreign_department_evaluation and foreign_department_evaluation.evaluation_type)):
                return False
            if not (self.instructor_uid or (foreign_department_evaluation and foreign_department_evaluation.instructor_uid)):
                return False
        return True

    def is_visible(self):
        return self.status != 'deleted'

    def mark_conflict(self, other_evaluation, key, saved_evaluation, self_value, other_value):
        if other_evaluation.status != 'ignore':
            self.conflicts[key].append({'department': other_evaluation.department.dept_name, 'value': other_value})
        if self.status != 'ignore':
            other_evaluation.conflicts[key].append({'department': saved_evaluation.department.dept_name, 'value': self_value})
        clear_department_cache(other_evaluation.department_id, self.term_id)
        clear_section_cache(self.term_id, self.course_number)

    def set_dates(self, loch_rows, foreign_dept_evaluations, saved_evaluation):
        self.meeting_start_date = min((r['meeting_start_date'] for r in loch_rows if r['meeting_start_date']), default=None)
        self.meeting_end_date = max((r['meeting_end_date'] for r in loch_rows if r['meeting_end_date']), default=None)
        default_meeting_dates = get_default_meeting_dates(term_ids=[self.term_id])[0]
        if not self.meeting_start_date:
            self.meeting_start_date = default_meeting_dates['start_date']
        if not self.meeting_end_date:
            self.meeting_end_date = default_meeting_dates['end_date']

        if saved_evaluation and saved_evaluation.start_date:
            self.start_date = saved_evaluation.start_date
            for fde in foreign_dept_evaluations:
                fde_start_date = fde.start_date
                if fde_start_date and fde_start_date != self.start_date:
                    self.mark_conflict(
                        fde,
                        'evaluationPeriod',
                        saved_evaluation,
                        safe_strftime(self.start_date, '%Y-%m-%d'),
                        safe_strftime(fde_start_date, '%Y-%m-%d'),
                    )
                else:
                    fde.start_date = self.start_date
        else:
            for fde in foreign_dept_evaluations:
                if fde.start_date and self.department_id != fde.department_id:
                    self.start_date = fde.start_date
                    break

        if self.start_date:
            if (self.start_date - self.meeting_start_date < timedelta(days=70)):
                self.end_date = self.start_date + timedelta(days=13)
            else:
                self.end_date = self.start_date + timedelta(days=20)
        else:
            self.start_date, self.end_date = self.get_default_evaluation_dates(default_meeting_dates)

    def set_department_form(self, saved_evaluation, foreign_dept_evaluations, default_form):
        if saved_evaluation and saved_evaluation.department_form:
            self.department_form = saved_evaluation.department_form
            for fde in foreign_dept_evaluations:
                if fde.department_form and fde.department_form.id != self.department_form.id:
                    self.mark_conflict(fde, 'departmentForm', saved_evaluation, self.department_form.name, fde.department_form.name)
        else:
            for fde in foreign_dept_evaluations:
                # If the other department has marked their row 'Ignore', we prefer the default form unless none exists.
                if (fde.department_form
                        and self.department_id != fde.department_id
                        and (fde.status != 'ignore' or not default_form)):
                    self.department_form = fde.department_form
                    break
        if default_form and not self.department_form:
            self.department_form = default_form
        if self.department_form and self.status != 'confirmed' and self.department_form.deleted_at:
            self.department_form = None

    def set_evaluation_type(self, saved_evaluation, foreign_dept_evaluations, instructor, default_evaluation_types):
        if saved_evaluation and saved_evaluation.evaluation_type:
            self.evaluation_type = saved_evaluation.evaluation_type
            for fde in foreign_dept_evaluations:
                if fde.evaluation_type and fde.evaluation_type.id != self.evaluation_type.id:
                    self.mark_conflict(fde, 'evaluationType', saved_evaluation, self.evaluation_type.name, fde.evaluation_type.name)
        else:
            for fde in foreign_dept_evaluations:
                # If the other department has marked their row 'Ignore', we prefer the default evaluation type unless none exists.
                if (fde.evaluation_type
                        and self.department_id != fde.department_id
                        and (fde.status != 'ignore' or not default_evaluation_types)):
                    self.evaluation_type = fde.evaluation_type
                    break
        if not self.evaluation_type:
            # Set default based on instructor affiliations, unless default types weren't passed in from the section object.
            if not default_evaluation_types:
                return
            elif instructor and 'STUDENT-TYPE' in instructor.get('affiliations', []):
                self.evaluation_type = default_evaluation_types.get('G')
            elif instructor and 'ACADEMIC' in instructor.get('affiliations', []):
                self.evaluation_type = default_evaluation_types.get('F')

    def set_fields(self, fields, original_evaluation_feed=None):
        if 'midterm' in fields:
            self.set_midterm_form(original_evaluation_feed)
        elif 'departmentForm' in fields:
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
        if original_evaluation_feed:
            _set_defaults(self, original_evaluation_feed)

    def set_last_updated(self, loch_rows, saved_evaluation):
        updates = [r['created_at'] for r in loch_rows]
        if saved_evaluation:
            updates.append(saved_evaluation.updated_at)
        self.last_updated = max(updates)

    def set_midterm_form(self, original_evaluation_feed):
        if original_evaluation_feed and original_evaluation_feed.get('departmentForm'):
            midterm_form = DepartmentForm.find_by_name(original_evaluation_feed['departmentForm']['name'] + '_MID')
            if midterm_form:
                self.department_form = midterm_form

    def set_status(self, saved_evaluation, foreign_dept_evaluations):
        if saved_evaluation and saved_evaluation.status:
            self.status = saved_evaluation.status
        else:
            for fde in foreign_dept_evaluations:
                if fde.status == 'marked' and self.status is None:
                    self.status = 'marked'
                elif fde.status == 'confirmed' and self.status in ('confirmed', None):
                    self.status = 'confirmed'

    def to_api_json(self, section):
        default_dept_form_feed = section.default_form.to_api_json() if section.default_form and not section.default_form.deleted_at else None
        dept_form_feed = self.department_form.to_api_json() if self.department_form else None
        eval_type_feed = self.evaluation_type.to_api_json() if self.evaluation_type else None

        feed_status = 'review' if self.status == 'marked' else self.status

        transient_id = self.transient_id()
        if self.instructor_uid in section.uids_with_midterm_and_final:
            if self.is_midterm():
                transient_id = transient_id + '_midterm'
            else:
                transient_id = transient_id + '_final'

        feed = section.to_api_json()
        feed.update({
            'id': self.id or transient_id,
            'transientId': transient_id,
            'status': feed_status,
            'instructor': section.instructors.get(self.instructor_uid),
            'defaultDepartmentForm': default_dept_form_feed,
            'departmentForm': dept_form_feed,
            'evaluationType': eval_type_feed,
            'startDate': safe_strftime(self.start_date, '%Y-%m-%d'),
            'endDate': safe_strftime(self.end_date, '%Y-%m-%d'),
            'meetingDates': {
                'start': safe_strftime(self.meeting_start_date, '%Y-%m-%d'),
                'end': safe_strftime(self.meeting_end_date, '%Y-%m-%d'),
            },
            'modular': is_modular(self.start_date, self.end_date),
            'lastUpdated': isoformat(self.last_updated),
            'conflicts': {},
            'valid': self.valid,
        })
        dept = self.department or (hasattr(self, '_department') and self._department)
        if dept:
            feed['department'] = {
                'id': dept.id,
                'name': dept.dept_name,
            }
        for field, conflicts in self.conflicts.items():
            if conflicts:
                feed['conflicts'][field] = list({v['department']: v for v in conflicts}.values())
        return feed

    def to_export_key(self):
        return EvaluationExportKey(
            course_number=self.course_number,
            department_form=self.department_form.name,
            evaluation_type=self.evaluation_type.name,
            start_date=self.start_date,
            end_date=self.end_date,
        )

    # Fallback id string for Evaluation instances that are created for the department/section API but not saved to the database.
    def transient_id(self):
        return f'_{self.term_id}_{self.course_number}_{self.instructor_uid}'

    def update_validity(self, saved_evaluation, foreign_dept_evaluations):
        self.valid = True
        updated = False
        if saved_evaluation:
            updated_validity = self.is_valid()
            if updated_validity != saved_evaluation.valid:
                saved_evaluation.valid = updated_validity
                db.session.add(saved_evaluation)
                updated = True
                clear_department_cache(self.department_id, self.term_id)
            self.valid = saved_evaluation.valid
        for fde in foreign_dept_evaluations:
            updated_validity = self.is_valid(fde)
            if updated_validity != fde.valid:
                fde.valid = updated_validity
                db.session.add(fde)
                updated = True
                clear_department_cache(fde.department_id, self.term_id)
        if updated:
            clear_section_cache(self.term_id, self.course_number)
            std_commit()


def is_modular(start_date, end_date):
    return True if start_date and end_date and end_date - start_date < timedelta(days=20) else False


def _parse_transient_id(transient_id):
    if not isinstance(transient_id, str):
        return None
    components = transient_id.split('_')
    if len(components) < 4:
        return None
    return {
        'term_id': components[1],
        'course_number': components[2],
        'instructor_uid': components[3],
    }


def _set_defaults(evaluation, evaluation_feed):
    if not evaluation.department_form_id and evaluation_feed['departmentForm']:
        evaluation.department_form_id = evaluation_feed['departmentForm']['id']
    if not evaluation.evaluation_type_id and evaluation_feed['evaluationType']:
        evaluation.evaluation_type_id = evaluation_feed['evaluationType']['id']
    if not evaluation.start_date and evaluation_feed['startDate']:
        evaluation.start_date = date.fromisoformat(evaluation_feed['startDate'])

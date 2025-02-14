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

from damien import db, std_commit
from damien.models.base import Base
from damien.models.department_form import DepartmentForm


class UserDepartmentForm(Base):
    __tablename__ = 'user_department_forms'

    department_form_id = db.Column(
        db.Integer,
        db.ForeignKey('department_forms.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )

    def __init__(
        self,
        department_form_id,
        user_id,
    ):
        self.department_form_id = department_form_id
        self.user_id = user_id

    def __repr__(self):
        return f"""<UserDepartmentForm department_form_id={self.department_form_id},
                    user_id={self.user_id},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>"""

    @classmethod
    def create(
            cls,
            department_form_id,
            user_id,
    ):
        user_department_form = cls(department_form_id=department_form_id, user_id=user_id)
        db.session.add(user_department_form)
        std_commit()
        return user_department_form

    @classmethod
    def delete(cls, department_form_id, user_id):
        user_department_form = cls.query.filter_by(department_form_id=department_form_id, user_id=user_id).first()
        db.session.delete(user_department_form)
        std_commit()

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def update(cls, department_form_ids, user):
        department_form_ids = set(department_form_ids)
        existing_department_form_ids = set(udf.department_form_id for udf in cls.find_by_user_id(user.id))
        department_form_ids_to_delete = existing_department_form_ids - department_form_ids
        department_form_ids_to_add = department_form_ids - existing_department_form_ids

        for department_form_id in department_form_ids_to_delete:
            df = DepartmentForm.find_by_id(department_form_id, include_deleted=True)
            user.department_forms.remove(df)
            db.session.flush()
        for department_form_id in department_form_ids_to_add:
            df = DepartmentForm.find_by_id(department_form_id, include_deleted=True)
            user.department_forms.add(df)
        std_commit()

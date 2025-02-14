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
from damien.lib.util import utc_now
from damien.models.base import Base
from damien.models.department import Department


class DepartmentMember(Base):
    __tablename__ = 'department_members'

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    can_receive_communications = db.Column(db.Boolean, nullable=False, default=True)

    department = db.relationship(Department.__name__, back_populates='members', lazy='joined')
    user = db.relationship(
        'User',
        back_populates='department_memberships',
        primaryjoin='and_(User.id==DepartmentMember.user_id, User.deleted_at==None)',
    )

    def __init__(
        self,
        department_id,
        user_id,
        can_receive_communications=True,
    ):
        self.department_id = department_id
        self.user_id = user_id
        self.can_receive_communications = can_receive_communications

    def __repr__(self):
        return f"""<DepartmentMember department_id={self.department_id},
                    user_id={self.user_id},
                    can_receive_communications={self.can_receive_communications},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>"""

    @classmethod
    def create(
            cls,
            department_id,
            user_id,
            can_receive_communications=True,
    ):
        department_member = cls(
            department_id=department_id,
            user_id=user_id,
            can_receive_communications=can_receive_communications,
        )
        db.session.add(department_member)
        std_commit()
        return department_member

    @classmethod
    def find_by_department_and_user(cls, department_id, user_id):
        return cls.query.filter_by(department_id=department_id, user_id=user_id).first()

    @classmethod
    def upsert(
        cls,
        blue_permissions,
        can_receive_communications,
        department_id,
        email,
        user_id,
    ):
        department_member = cls.query.filter_by(department_id=department_id, user_id=user_id).first()
        if not department_member:
            department_member = cls(department_id=department_id, user_id=user_id)
            db.session.add(department_member)
            std_commit()
        department_member.can_receive_communications = can_receive_communications
        department_member.user.blue_permissions = blue_permissions
        department_member.user.email = email
        std_commit()
        return department_member

    @classmethod
    def delete(cls, department_id, user_id):
        dc = cls.query.filter_by(department_id=department_id, user_id=user_id).first()
        if dc:
            db.session.delete(dc)
            # Add a deleted_at timestamp to orphaned user objects.
            if not dc.user.is_admin and len(dc.user.department_memberships) == 1:
                dc.user.deleted_at = utc_now()
            std_commit()

    def to_api_json(self):
        return {
            'userId': self.user_id,
            'departmentId': self.department_id,
            'canReceiveCommunications': self.can_receive_communications,
            **self.user.to_api_json(),
        }

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

from datetime import datetime

from damien import db, std_commit
from damien.lib.util import isoformat, parse_search_snippet
from damien.models.base import Base
from damien.models.department_form import DepartmentForm
from damien.models.department_member import DepartmentMember
from sqlalchemy.dialects.postgresql import ENUM


blue_permissions_enum = ENUM(
    'reports_only',
    'response_rates',
    name='user_blue_permissions',
    create_type=False,
)


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    csid = db.Column(db.String(255))
    uid = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=None)
    blue_permissions = db.Column(blue_permissions_enum)
    deleted_at = db.Column(db.DateTime)
    login_at = db.Column(db.DateTime)

    department_forms = db.relationship(
        DepartmentForm.__name__,
        back_populates='users',
        collection_class=set,
        secondary='user_department_forms',
    )
    department_memberships = db.relationship(
        DepartmentMember.__name__,
        back_populates='user',
        lazy='joined',
    )

    def __init__(
        self,
        csid,
        uid,
        first_name,
        last_name,
        email,
        is_admin=False,
        blue_permissions=None,
    ):
        self.csid = csid
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.blue_permissions = blue_permissions

    def __repr__(self):
        return f"""<User id={self.id},
                    csid={self.csid},
                    uid={self.uid},
                    first_name={self.first_name},
                    last_name={self.last_name},
                    email={self.email},
                    is_admin={self.is_admin},
                    blue_permissions={self.blue_permissions},
                    created_at={self.created_at},
                    updated_at={self.updated_at},
                    deleted_at={self.deleted_at},
                    login_at={self.login_at}>
                """

    @classmethod
    def create_or_restore(
            cls,
            csid,
            uid,
            first_name,
            last_name,
            email,
            is_admin=False,
            blue_permissions=None,
            db_id=None,
    ):
        user = None
        if db_id:
            user = cls.query.filter_by(id=db_id).first()
        if not user:
            user = cls.query.filter_by(uid=uid).first()
        if user:
            user.deleted_at = None
            user.email = email
            user.blue_permissions = blue_permissions
        else:
            user = cls(
                csid=csid,
                uid=uid,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_admin=is_admin,
                blue_permissions=blue_permissions,
            )
        db.session.add(user)
        std_commit()
        return user

    @classmethod
    def find_by_id(cls, db_id):
        query = cls.query.filter_by(id=db_id, deleted_at=None)
        return query.first()

    @classmethod
    def find_by_uid(cls, uid):
        query = cls.query.filter_by(uid=uid, deleted_at=None)
        return query.first()

    @classmethod
    def record_login(cls, db_id):
        user = cls.query.filter_by(id=db_id, deleted_at=None).first()
        user.login_at = datetime.now()
        std_commit()

    @classmethod
    def search(cls, snippet, exclude_uids):
        if not snippet:
            return []
        query_filter, params = parse_search_snippet(snippet, uid_col='uid')
        if exclude_uids:
            params['uids'] = exclude_uids
            query_filter += ' AND NOT uid = ANY(:uids)'
        query = f"""SELECT uid, csid, first_name, last_name, email
                    FROM users
                    {query_filter}
                    LIMIT 20"""
        results = db.session.execute(query, params)
        keys = results.keys()
        return [dict(zip(keys, row)) for row in results.fetchall()]

    @classmethod
    def get_dept_contacts_with_blue_permissions(cls):
        query = cls.query.filter(
            cls.is_admin.is_not(True),
            cls.blue_permissions.is_not(None),
            cls.deleted_at.is_(None),
        ).order_by(cls.uid)
        return query.all()

    def can_view_response_rates(self):
        return self.blue_permissions == 'response_rates'

    def to_api_json(self):
        return {
            'id': self.id,
            'csid': self.csid,
            'uid': self.uid,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'isAdmin': self.is_admin,
            'canViewReports': self.blue_permissions is not None,
            'canViewResponseRates': self.can_view_response_rates(),
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
            'deletedAt': isoformat(self.deleted_at),
            'lastLoginAt': isoformat(self.login_at),
            'departmentForms': [df.to_api_json() for df in self.department_forms],
        }

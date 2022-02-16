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
from damien.lib.util import isoformat
from damien.models.base import Base
from damien.models.department_member import DepartmentMember
from sqlalchemy import or_


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    csid = db.Column(db.String(255))
    uid = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=None)
    can_receive_communications = db.Column(db.Boolean, default=None)
    can_view_response_rates = db.Column(db.Boolean, default=None)
    deleted_at = db.Column(db.DateTime)

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
        can_receive_communications=False,
        can_view_response_rates=False,
    ):
        self.csid = csid
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.can_receive_communications = can_receive_communications
        self.can_view_response_rates = can_view_response_rates

    def __repr__(self):
        return f"""<User id={self.id},
                    csid={self.csid},
                    uid={self.uid},
                    first_name={self.first_name},
                    last_name={self.last_name},
                    email={self.email},
                    is_admin={self.is_admin},
                    can_receive_communications={self.can_receive_communications},
                    can_view_response_rates={self.can_view_response_rates},
                    created_at={self.created_at},
                    updated_at={self.updated_at},
                    deleted_at={self.deleted_at}>
                """

    @classmethod
    def create(
            cls,
            csid,
            uid,
            first_name,
            last_name,
            email,
            is_admin=False,
            can_receive_communications=False,
            can_view_response_rates=False,
    ):
        user = cls(
            csid=csid,
            uid=uid,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_admin=is_admin,
            can_receive_communications=can_receive_communications,
            can_view_response_rates=can_view_response_rates,
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
    def search(cls, snippet):
        like_csid_snippet = cls.csid.like(f'%{snippet}%')
        like_uid_snippet = cls.uid.like(f'%{snippet}%')
        criteria = or_(like_csid_snippet, like_uid_snippet)
        return cls.query.filter(criteria).all()

    def to_api_json(self):
        return {
            'id': self.id,
            'csid': self.csid,
            'uid': self.uid,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'isAdmin': self.is_admin,
            'canReceiveCommunications': self.can_receive_communications,
            'canViewResponseRates': self.can_view_response_rates,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
            'deletedAt': isoformat(self.deleted_at),
        }

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

import re

from damien import db, std_commit
from damien.lib.util import isoformat, utc_now
from damien.models.base import Base
from sqlalchemy import and_, or_


class SupplementalInstructor(Base):
    __tablename__ = 'supplemental_instructors'

    ldap_uid = db.Column(db.String(80), nullable=False, primary_key=True)
    sis_id = db.Column(db.String(80))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80), nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime)

    def __init__(
        self,
        ldap_uid,
        sis_id,
        first_name,
        last_name,
        email_address,
    ):
        self.ldap_uid = ldap_uid
        self.sis_id = sis_id
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address

    def __repr__(self):
        return f"""<SupplementalInstructor ldap_uid={self.ldap_uid},
                    sis_id={self.sis_id}>
                    first_name={self.first_name}>
                    last_name={self.last_name}
                    email_address={self.email_address}
                    deleted_at={self.deleted_at}>
                """

    @classmethod
    def create_or_restore(
            cls,
            ldap_uid,
            sis_id,
            first_name,
            last_name,
            email_address,
    ):
        instructor = cls.query.filter_by(ldap_uid=ldap_uid).first()
        if instructor:
            instructor.deleted_at = None
            instructor.sis_id = sis_id
            instructor.first_name = first_name
            instructor.last_name = last_name
            instructor.email_address = email_address
        else:
            instructor = cls(
                ldap_uid=ldap_uid,
                sis_id=sis_id,
                first_name=first_name,
                last_name=last_name,
                email_address=email_address,
            )
        db.session.add(instructor)
        std_commit()
        return instructor

    @classmethod
    def delete(cls, ldap_uid):
        now = utc_now()
        instructor = cls.query.filter_by(ldap_uid=ldap_uid).first()
        if instructor:
            instructor.deleted_at = now
            db.session.add(instructor)
            std_commit()
            return instructor
        else:
            return None

    @classmethod
    def find_by_uid(cls, ldap_uid):
        query = cls.query.filter_by(ldap_uid=ldap_uid, deleted_at=None)
        return query.first()

    @classmethod
    def find_by_uids(cls, ldap_uids):
        query = cls.query.filter(and_(cls.ldap_uid.in_(ldap_uids), cls.deleted_at == None))  # noqa: E711
        return query.all()

    @classmethod
    def search(cls, snippet):
        words = list(set(snippet.upper().split()))
        criteria = [cls.deleted_at == None]  # noqa: E711
        # A single numeric string indicates a UID search.
        if len(words) == 1 and re.match(r'^\d+$', words[0]):
            criteria.append(cls.ldap_uid.ilike(f'{words[0]}%'))
        # Otherwise search by name.
        else:
            for word in words:
                word = ''.join(re.split('\W', word))
                criteria.append(or_(cls.first_name.ilike(f'{word}%'), cls.last_name.ilike(f'{word}%')))
        criteria = and_(*criteria)
        return cls.query.filter(criteria).all()

    def to_api_json(self):
        return {
            'uid': self.ldap_uid,
            'csid': self.sis_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email_address,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }

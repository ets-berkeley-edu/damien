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
from damien.lib.util import utc_now
from damien.models.base import Base


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
                    first_name={self.courfirst_namese_number}>
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
        query = cls.query.filter_by(uid=ldap_uid, deleted_at=None)
        return query.first()

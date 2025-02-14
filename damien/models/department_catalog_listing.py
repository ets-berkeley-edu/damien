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

from damien import db
from damien.lib.berkeley import get_current_term_id, term_ids_range
from damien.models.base import Base
from flask import current_app as app
from sqlalchemy import func


class DepartmentCatalogListing(Base):
    __tablename__ = 'department_catalog_listings'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    subject_area = db.Column(db.String(255), nullable=False)
    catalog_id = db.Column(db.String(255))
    default_form_id = db.Column(db.Integer, db.ForeignKey('department_forms.id'), nullable=False)
    custom_evaluation_types = db.Column(db.Boolean, nullable=False, default=False)
    start_term_id = db.Column(db.String(4))
    end_term_id = db.Column(db.String(4))

    department = db.relationship('Department', back_populates='catalog_listings')
    default_form = db.relationship('DepartmentForm', back_populates='catalog_listings')

    def __init__(
        self,
        department_id,
        subject_area,
        catalog_id,
        default_form_id,
        custom_evaluation_types,
        start_term_id,
        end_term_id,
    ):
        self.department_id = department_id
        self.subject_area = subject_area
        self.catalog_id = catalog_id
        self.default_form_id = default_form_id
        self.custom_evaluation_types = custom_evaluation_types
        self.start_term_id = start_term_id
        self.end_term_id = end_term_id

    def __repr__(self):
        return f"""<DepartmentCatalogListing id={self.id},
                    department_id={self.department_id},
                    subject_area={self.subject_area},
                    catalog_id={self.catalog_id},
                    default_form_id={self.default_form_id},
                    custom_evaluation_type={self.custom_evaluation_types},
                    start_term_id={self.start_term_id},
                    end_term_id={self.end_term_id}>
                """

    @classmethod
    def catalog_ids_to_exclude(cls, department_id, subject_area):
        results = cls.query.filter(cls.subject_area.in_([subject_area, '']), cls.department_id != department_id).all()
        return [r.catalog_id for r in results if r.catalog_id]

    @classmethod
    def department_terms(cls, department_id):
        results = db.session.query(
            func.coalesce(cls.start_term_id, app.config['EARLIEST_TERM_ID']),
            func.coalesce(cls.end_term_id, get_current_term_id()),
        ).filter(cls.department_id == department_id).all()
        term_ids = []
        for r in results:
            term_ids.extend(term_ids_range(*r))
        return sorted(list(set(term_ids)))

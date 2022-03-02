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

from damien import db
from flask import current_app as app
from sqlalchemy.sql import text


def get_cross_listings(term_id, course_numbers):
    query = """SELECT *
            FROM unholy_loch.sis_sections
            WHERE term_id = :term_id AND course_number IN (
              SELECT cross_listing_number
              FROM unholy_loch.cross_listings
              WHERE term_id = :term_id AND course_number = ANY(:course_numbers)
            )
            ORDER BY course_number, instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id, 'course_numbers': course_numbers},
    ).all()
    app.logger.info(f'Unholy loch cross-listing query returned {len(results)} results: {query}')
    return results


def get_room_shares(term_id, course_numbers):
    query = """SELECT *
            FROM unholy_loch.sis_sections
            WHERE term_id = :term_id AND course_number IN (
              SELECT room_share_number
              FROM unholy_loch.co_schedulings
              WHERE term_id = :term_id AND course_number = ANY(:course_numbers)
            )
            ORDER BY course_number, instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id, 'course_numbers': course_numbers},
    ).all()
    app.logger.info(f'Unholy loch room share query returned {len(results)} results: {query}')
    return results


def get_loch_instructors(uids):
    query = """SELECT distinct *
            FROM unholy_loch.sis_instructors i
            WHERE ldap_uid = ANY(:uids)
        """
    results = db.session().execute(
        text(query),
        {'uids': uids},
    ).all()
    app.logger.info(f'Unholy loch instructor query returned {len(results)} results for {len(uids)} uids')
    return results


def get_loch_sections(term_id, conditions):
    query = f"""SELECT *
            FROM unholy_loch.sis_sections
            WHERE term_id = :term_id AND ({' OR '.join(conditions)})
            ORDER BY course_number, instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id},
    ).all()
    app.logger.info(f'Unholy loch course query returned {len(results)} results: {query}')
    return results


def get_loch_sections_by_ids(term_id, course_numbers):
    query = """SELECT *
            FROM unholy_loch.sis_sections
            WHERE term_id = :term_id AND course_number = ANY(:course_numbers)
            ORDER BY course_number, instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id, 'course_numbers': course_numbers},
    ).all()
    app.logger.info(f'Unholy loch course query returned {len(results)} results: {query}')
    return results

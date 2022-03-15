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

import json
import os

from damien import db
from damien.lib.util import parse_search_snippet
from flask import current_app as app
from sqlalchemy.sql import text


# Refresh attributes in loch for evaluated instructors without instructor assignments in SIS data. These additional instructors
# are _not_ the same as the separately maintained table of "supplemental instructors"; those are manually added records for
# people who don't appear in SIS data at all.
def refresh_additional_instructors(uids=None):
    if os.environ.get('DAMIEN_ENV') == 'test':
        return True

    if uids:
        uid_source = 'unnest(:uids) AS instructor_uid'
        uid_params = {'uids': uids}
    else:
        uid_source = 'evaluations'
        uid_params = {}
    uid_query = f"""
        SELECT DISTINCT instructor_uid FROM {uid_source}
        WHERE instructor_uid NOT IN
        (SELECT ldap_uid FROM unholy_loch.sis_instructors)"""

    uids_to_refresh = [r['instructor_uid'] for r in db.session().execute(text(uid_query), uid_params).all()]

    refresh_query = f"""INSERT INTO unholy_loch.sis_instructors
        (ldap_uid, sis_id, first_name, last_name, email_address, affiliations, created_at)
        (SELECT * FROM dblink('{app.config['DBLINK_NESSIE_RDS']}',$NESSIE$
          SELECT DISTINCT
            ba.ldap_uid, ba.sid AS sis_id, ba.first_name, ba.last_name, ba.email_address, ba.affiliations,
            now() AS created_at
          FROM sis_data.basic_attributes ba
          WHERE ba.ldap_uid = ANY(:uids_to_refresh)
          $NESSIE$)
          AS nessie_sis_instructors (
            ldap_uid VARCHAR(80),
            sis_id VARCHAR(80),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email_address VARCHAR(255),
            affiliations TEXT,
            created_at TIMESTAMP WITH TIME ZONE
          )
        )"""

    try:
        db.session().execute(text(refresh_query), {'uids_to_refresh': uids_to_refresh})
        return True
    except Exception as e:
        app.logger.exception(e)
        return False


def get_loch_basic_attributes_by_uid_or_name(snippet, limit=20, exclude_uids=None):
    if not snippet:
        return []
    if os.environ.get('DAMIEN_ENV') == 'test':
        fixture_path = f"{app.config['FIXTURES_PATH']}/loch_ness/basic_attributes_for_snippet_{snippet}.json"
        results = []
        if os.path.isfile(fixture_path):
            with open(fixture_path) as f:
                results = json.load(f)
        return results

    query_filter, params = parse_search_snippet(snippet)
    params['limit'] = limit
    if exclude_uids:
        params['uids'] = exclude_uids
        query_filter += ' AND NOT ldap_uid = ANY(:uids)'
    query = f"""SELECT * FROM dblink('{app.config['DBLINK_NESSIE_RDS']}',$NESSIE$
                SELECT ldap_uid, sid, first_name, last_name, email_address
                  FROM sis_data.basic_attributes
                  {query_filter}
                  LIMIT :limit
            $NESSIE$)
            AS nessie_basic_attributes (
                uid VARCHAR,
                csid VARCHAR,
                first_name VARCHAR,
                last_name VARCHAR,
                email VARCHAR
            )
            LIMIT 20
            """
    try:
        results = db.session().execute(text(query), params).all()
        app.logger.info(f'Loch Ness basic attributes query returned {len(results)} results (snippet={snippet}).')
        return results
    except Exception as e:
        app.logger.exception(e)


def get_cross_listings(term_id, course_numbers):
    query = """SELECT
                ss.*,
                cl.course_number AS cross_listed_with,
                TRUE AS foreign_department_course
            FROM unholy_loch.sis_sections ss
            JOIN unholy_loch.cross_listings cl
            ON cl.term_id = :term_id AND ss.term_id = :term_id
            AND ss.course_number = cl.cross_listing_number
            AND cl.course_number = ANY(:course_numbers)
            ORDER BY ss.course_number, ss.instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id, 'course_numbers': course_numbers},
    ).all()
    app.logger.info(f'Unholy loch cross-listing query returned {len(results)} results: {query}')
    return results


def get_room_shares(term_id, course_numbers):
    query = """SELECT
                ss.*,
                cs.course_number AS room_shared_with,
                TRUE AS foreign_department_course
            FROM unholy_loch.sis_sections ss
            JOIN unholy_loch.co_schedulings cs
            ON cs.term_id = :term_id AND ss.term_id = :term_id
            AND ss.course_number = cs.room_share_number
            AND cs.course_number = ANY(:course_numbers)
            ORDER BY ss.course_number, ss.instructor_uid
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


def get_loch_instructors_for_snippet(snippet, limit, exclude_uids):
    if not snippet:
        return []
    query_filter, params = parse_search_snippet(snippet)
    if exclude_uids:
        params['uids'] = exclude_uids
        query_filter += ' AND NOT ldap_uid = ANY(:uids)'
    params['limit'] = limit
    query = f"""SELECT ldap_uid AS uid, sis_id AS csid, first_name, last_name, email_address AS email
            FROM unholy_loch.sis_instructors
            {query_filter} LIMIT :limit"""
    return db.session().execute(text(query), params).all()


def get_loch_sections(term_id, conditions):
    query = f"""SELECT
                s.*,
                cl.cross_listing_number AS cross_listed_with,
                cs.room_share_number AS room_shared_with
            FROM unholy_loch.sis_sections s
            LEFT JOIN unholy_loch.cross_listings cl
                ON cl.term_id = :term_id AND s.term_id = :term_id
                AND s.course_number = cl.course_number
            LEFT JOIN unholy_loch.co_schedulings cs
                ON cs.term_id = :term_id AND s.term_id = :term_id
                AND s.course_number = cs.course_number
            WHERE s.term_id = :term_id AND ({' OR '.join(conditions)})
            ORDER BY s.course_number, s.instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id},
    ).all()
    app.logger.info(f'Unholy loch course query returned {len(results)} results: {query}')
    return results


def get_loch_sections_by_ids(term_id, course_numbers):
    query = """SELECT
                s.*,
                cl.cross_listing_number AS cross_listed_with,
                cs.room_share_number AS room_shared_with
            FROM unholy_loch.sis_sections s
            LEFT JOIN unholy_loch.cross_listings cl
                ON cl.term_id = :term_id AND s.term_id = :term_id
                AND s.course_number = cl.course_number
            LEFT JOIN unholy_loch.co_schedulings cs
                ON cs.term_id = :term_id AND s.term_id = :term_id
                AND s.course_number = cs.course_number
            WHERE s.term_id = :term_id AND s.course_number = ANY(:course_numbers)
            ORDER BY s.course_number, s.instructor_uid
        """
    results = db.session().execute(
        text(query),
        {'term_id': term_id, 'course_numbers': course_numbers},
    ).all()
    app.logger.info(f'Unholy loch course query returned {len(results)} results: {query}')
    return results

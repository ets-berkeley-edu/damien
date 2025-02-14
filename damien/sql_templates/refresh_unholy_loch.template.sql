/**
 * Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

CREATE TABLE tmp_sis_sections AS SELECT * FROM unholy_loch.sis_sections WHERE term_id = '{term_id}';
CREATE TABLE tmp_sis_instructors AS SELECT * FROM unholy_loch.sis_instructors;

--

DELETE FROM public.json_cache WHERE term_id = '{term_id}';

--

TRUNCATE unholy_loch.sis_terms;

INSERT INTO unholy_loch.sis_terms(term_id, term_name, term_begins, term_ends)
(SELECT * FROM
  dblink('{dblink_nessie_rds}',$NESSIE$
    SELECT term_id, term_name, term_begins, term_ends
    FROM terms.term_definitions
  $NESSIE$)
  AS nessie_sis_terms (
    term_id VARCHAR(4),
    term_name VARCHAR(80),
    term_begins DATE,
    term_ends DATE
  )
);

--

DELETE FROM unholy_loch.sis_sections WHERE term_id = '{term_id}';

INSERT INTO unholy_loch.sis_sections (term_id, course_number,
                          subject_area, catalog_id, instruction_format, section_num,
                          course_title, is_primary,
                          instructor_uid, instructor_role_code,
                          meeting_location, meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date,
                          created_at)
   (SELECT * FROM dblink('{dblink_nessie_rds}',$NESSIE$
    SELECT
        sis_term_id AS term_id, sis_section_id AS course_number,
        (string_to_array(sis_course_name, ' '))[1] AS subject_area,
        (string_to_array(sis_course_name, ' '))[2] AS catalog_id,
        sis_instruction_format AS instruction_format,
        sis_section_num AS section_num,
        sis_course_title AS course_title,
        is_primary,
        instructor_uid, instructor_role_code,
        meeting_location, meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date,
        now() AS created_at
    FROM sis_data.sis_sections
    WHERE sis_term_id='{term_id}'
  $NESSIE$)
  AS nessie_sis_sections (
    term_id VARCHAR(4),
    course_number VARCHAR(5),
    subject_area VARCHAR(80),
    catalog_id VARCHAR(80),
    instruction_format VARCHAR(80),
    section_num VARCHAR(80),
    course_title VARCHAR,
    is_primary BOOLEAN,
    instructor_uid VARCHAR(80),
    instructor_role_code VARCHAR(80),
    meeting_location VARCHAR,
    meeting_days VARCHAR(80),
    meeting_start_time VARCHAR(80),
    meeting_end_time VARCHAR(80),
    meeting_start_date DATE,
    meeting_end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE
  )
);

-- Our source data may use blank spaces for UIDs that should be null.
UPDATE unholy_loch.sis_sections SET instructor_uid = NULL WHERE instructor_uid = '';

-- Preserve older created_at timestamps where present.
UPDATE unholy_loch.sis_sections s
SET created_at = t.created_at
FROM tmp_sis_sections t
WHERE s.term_id = t.term_id AND s.course_number = t.course_number;

-- Restore deleted sections, with deleted_at set to now() if no previous value.
INSERT INTO unholy_loch.sis_sections (term_id, course_number,
                          subject_area, catalog_id, instruction_format, section_num,
                          course_title, is_primary,
                          instructor_uid, instructor_role_code,
                          meeting_location, meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date,
                          created_at, deleted_at)
  (SELECT term_id, course_number,
          subject_area, catalog_id, instruction_format, section_num,
          course_title, is_primary,
          instructor_uid, instructor_role_code,
          meeting_location, meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date,
          created_at, COALESCE(deleted_at, now()) AS deleted_at
    FROM tmp_sis_sections
    WHERE term_id || '-' || course_number NOT IN
    (SELECT term_id || '-' || course_number FROM unholy_loch.sis_sections)
  );

DROP TABLE tmp_sis_sections;

--

TRUNCATE unholy_loch.sis_instructors;

INSERT INTO unholy_loch.sis_instructors
  (ldap_uid, sis_id, first_name, last_name, email_address, affiliations, created_at)
  (SELECT * FROM dblink('{dblink_nessie_rds}',$NESSIE$
    SELECT DISTINCT
        ba.ldap_uid, ba.sid AS sis_id, ba.first_name, ba.last_name, ba.email_address, ba.affiliations,
        now() AS created_at
    FROM sis_data.basic_attributes ba
    JOIN sis_data.sis_sections s
      ON s.sis_term_id='{term_id}'
      AND s.instructor_uid = ba.ldap_uid
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
  );

-- Preserve older created_at timestamps where present.
UPDATE unholy_loch.sis_instructors i
SET created_at = t.created_at
FROM tmp_sis_instructors t
WHERE i.ldap_uid = t.ldap_uid;

-- Restore deleted instructors, with deleted_at set to now().
INSERT INTO unholy_loch.sis_instructors
  (ldap_uid, sis_id, first_name, last_name, email_address, affiliations, created_at, deleted_at)
  (SELECT ldap_uid, sis_id, first_name, last_name, email_address, affiliations,
      created_at, COALESCE(deleted_at, now()) AS deleted_at
    FROM tmp_sis_instructors
    WHERE ldap_uid NOT IN
    (SELECT ldap_uid FROM unholy_loch.sis_instructors)
  );

DROP TABLE tmp_sis_instructors;

-- Any current-term evaluations not yet confirmed or marked which refer to deleted instructors should have the instructor UID removed.
UPDATE evaluations
  SET instructor_uid = NULL, updated_by = '0'
  WHERE term_id = '{term_id}'
  AND id IN (
  SELECT e.id FROM evaluations e
    JOIN unholy_loch.sis_instructors i
      ON i.ldap_uid = e.instructor_uid
      AND i.deleted_at IS NOT NULL
      AND (e.status IS NULL OR e.status NOT IN ('confirmed', 'marked'))
    LEFT JOIN supplemental_instructors si
      ON i.ldap_uid = si.ldap_uid
      WHERE si.ldap_uid IS NULL OR si.deleted_at IS NOT NULL
);

--

DELETE FROM unholy_loch.sis_enrollments WHERE term_id = '{term_id}';

INSERT INTO unholy_loch.sis_enrollments
  (term_id, course_number, ldap_uid)
  (SELECT * FROM dblink('{dblink_nessie_rds}',$NESSIE$
    SELECT
        sis_term_id AS term_id,
        sis_section_id AS course_number,
        ldap_uid
    FROM sis_data.sis_enrollments e
    WHERE e.sis_term_id='{term_id}'
  $NESSIE$)
  AS nessie_sis_enrollments (
    term_id VARCHAR(4),
    course_number VARCHAR(5),
    ldap_uid VARCHAR(80)
  )
);

WITH ec AS (
  SELECT s.term_id, s.course_number, COUNT(DISTINCT e.ldap_uid) as enrollment_count
  FROM unholy_loch.sis_sections s
  LEFT JOIN unholy_loch.sis_enrollments e
  ON s.term_id = e.term_id
  AND s.course_number = e.course_number
  GROUP BY s.term_id, s.course_number
)
UPDATE unholy_loch.sis_sections s
SET enrollment_count = ec.enrollment_count
FROM ec
WHERE s.term_id = ec.term_id AND s.course_number = ec.course_number;

--

-- In the special case of a confirmed evaluation for a zero-enrollment course, ensure the section is present
-- in the supplemental_sections table so that it will appear in the Damien UI.

INSERT INTO supplemental_sections (term_id, course_number, department_id)
SELECT eval.term_id, eval.course_number, eval.department_id
  FROM evaluations eval
  LEFT JOIN unholy_loch.sis_enrollments enr
    ON enr.term_id = eval.term_id
    AND enr.course_number = eval.course_number
  WHERE
    eval.term_id = '{term_id}'
    AND eval.status = 'confirmed'
    AND enr.course_number IS NULL
    AND eval.course_number NOT IN (
      SELECT course_number FROM supplemental_sections WHERE term_id = '{term_id}' AND deleted_at IS NULL);

--

DELETE FROM unholy_loch.co_schedulings WHERE term_id = '{term_id}';

WITH schedules AS (
  SELECT
      term_id,
      course_number,
      trim(concat(
          meeting_days,
          meeting_end_date,
          meeting_end_time,
          meeting_location,
          meeting_start_date,
          meeting_start_time
      )) as schedule
  FROM unholy_loch.sis_sections
  WHERE
      term_id = '{term_id}'
      AND meeting_days <> ''
      AND meeting_end_date IS NOT NULL
      AND meeting_end_time <> ''
      AND meeting_location IS NOT NULL
      AND meeting_location NOT IN ('', 'Internet/Online', 'Off Campus', 'Requested General Assignment')
      AND meeting_start_date IS NOT NULL
      AND meeting_start_time <> ''
      AND deleted_at IS NULL
)
INSERT INTO unholy_loch.co_schedulings(term_id, course_number, room_share_number)
SELECT s1.term_id, s1.course_number, s2.course_number AS room_share_number
FROM schedules s1 JOIN schedules s2
ON s1.schedule = s2.schedule
AND s1.course_number != s2.course_number;

DELETE FROM unholy_loch.cross_listings WHERE term_id = '{term_id}';

WITH course_listings AS (
  (SELECT * FROM dblink('{dblink_nessie_rds}',$NESSIE$
    SELECT
      sis_section_id AS course_number,
      cs_course_id,
      session_code,
      sis_section_num
    FROM sis_data.sis_sections
    WHERE sis_term_id='{term_id}'
  $NESSIE$)
  AS nessie_course_listings (
    course_number VARCHAR(5),
    cs_course_id VARCHAR(80),
    session_code VARCHAR(5),
    sis_section_num VARCHAR(5)
  )))
INSERT INTO unholy_loch.cross_listings(term_id, course_number, cross_listing_number)
SELECT '{term_id}' AS term_id, cl1.course_number, cl2.course_number AS cross_listing_number
FROM course_listings cl1 JOIN course_listings cl2
ON cl1.cs_course_id = cl2.cs_course_id
AND cl1.session_code = cl2.session_code
AND cl1.sis_section_num = cl2.sis_section_num
AND cl1.course_number != cl2.course_number;

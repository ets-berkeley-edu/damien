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

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

CREATE SCHEMA unholy_loch;

-- SIS section and instructor data includes modification timestamps and soft-delete handling so as not to lose cancelled listings.

CREATE TABLE unholy_loch.sis_sections (
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    subject_area VARCHAR(80),
    catalog_id VARCHAR(80),
    instruction_format VARCHAR(80),
    section_num VARCHAR(80),
    course_title VARCHAR,
    is_primary BOOLEAN NOT NULL,
    instructor_uid VARCHAR(80),
    instructor_role_code VARCHAR(80),
    meeting_location VARCHAR,
    meeting_days VARCHAR(80),
    meeting_start_time VARCHAR(80),
    meeting_end_time VARCHAR(80),
    meeting_start_date DATE,
    meeting_end_date DATE,
    enrollment_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

--

CREATE TABLE unholy_loch.sis_instructors (
    ldap_uid VARCHAR(80) NOT NULL,
    sis_id VARCHAR(80),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email_address VARCHAR(255),
    affiliations TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- SIS enrollment data is loaded by a simple wipe-and-refresh and doesn't require timestamp tracking.

CREATE TABLE unholy_loch.sis_enrollments (
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    ldap_uid VARCHAR(80) NOT NULL
);

CREATE TABLE unholy_loch.sis_terms
(
    term_id VARCHAR(4) NOT NULL,
    term_name VARCHAR NOT NULL,
    term_begins DATE NOT NULL,
    term_ends DATE NOT NULL
);

-- Translation tables keep track of cross listings and room shares.

CREATE TABLE unholy_loch.cross_listings (
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    cross_listing_number VARCHAR(5) NOT NULL
);

CREATE TABLE unholy_loch.co_schedulings (
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    room_share_number VARCHAR(5) NOT NULL
);

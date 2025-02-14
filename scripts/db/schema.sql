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

--

CREATE TABLE department_catalog_listings (
    id integer NOT NULL,
    department_id integer NOT NULL,
    subject_area VARCHAR(255) NOT NULL,
    catalog_id VARCHAR(255),
    default_form_id integer,
    custom_evaluation_types boolean NOT NULL DEFAULT FALSE,
    start_term_id VARCHAR(4),
    end_term_id VARCHAR(4),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE department_catalog_listings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE department_catalog_listings_id_seq OWNED BY department_catalog_listings.id;
ALTER TABLE ONLY department_catalog_listings ALTER COLUMN id SET DEFAULT nextval('department_catalog_listings_id_seq'::regclass);

ALTER TABLE ONLY department_catalog_listings
    ADD CONSTRAINT department_catalog_listings_pkey PRIMARY KEY (id);

CREATE INDEX department_catalog_listings_department_id_idx ON department_catalog_listings USING btree (department_id);
CREATE INDEX department_catalog_listings_subject_area_idx ON department_catalog_listings USING btree (subject_area);

--

CREATE TABLE department_forms (
    id integer NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);

CREATE SEQUENCE department_forms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE department_forms_id_seq OWNED BY department_forms.id;
ALTER TABLE ONLY department_forms ALTER COLUMN id SET DEFAULT nextval('department_forms_id_seq'::regclass);

ALTER TABLE ONLY department_forms
    ADD CONSTRAINT department_forms_pkey PRIMARY KEY (id);
ALTER TABLE ONLY department_forms
    ADD CONSTRAINT department_forms_name_unique UNIQUE (name);

--

CREATE TABLE department_members (
    department_id integer NOT NULL,
    user_id integer NOT NULL,
    can_receive_communications boolean NOT NULL DEFAULT TRUE,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY department_members
    ADD CONSTRAINT department_members_pkey PRIMARY KEY (department_id, user_id);

--

CREATE TABLE department_notes (
    department_id integer NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY department_notes
    ADD CONSTRAINT department_notes_pkey PRIMARY KEY (department_id, term_id);

--

CREATE TABLE departments (
    id integer NOT NULL,
    dept_name character varying(255) NOT NULL,
    is_enrolled boolean NOT NULL DEFAULT FALSE,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE departments_id_seq OWNED BY departments.id;
ALTER TABLE ONLY departments ALTER COLUMN id SET DEFAULT nextval('departments_id_seq'::regclass);

ALTER TABLE ONLY departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);

--

CREATE TYPE export_status AS ENUM ('started', 'success', 'error');

CREATE TABLE exports (
    term_id VARCHAR(4) NOT NULL,
    s3_path VARCHAR(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status export_status
);

--

CREATE TABLE evaluation_types (
    id integer NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);

CREATE SEQUENCE evaluation_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE evaluation_types_id_seq OWNED BY evaluation_types.id;
ALTER TABLE ONLY evaluation_types ALTER COLUMN id SET DEFAULT nextval('evaluation_types_id_seq'::regclass);

ALTER TABLE ONLY evaluation_types
    ADD CONSTRAINT evaluation_types_pkey PRIMARY KEY (id);
ALTER TABLE ONLY evaluation_types
    ADD CONSTRAINT evaluation_types_name_unique UNIQUE (name);

--

CREATE TYPE evaluation_status AS ENUM ('marked', 'confirmed', 'deleted', 'ignore');

CREATE TABLE evaluations (
    id integer NOT NULL,
    department_id INTEGER NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    instructor_uid VARCHAR(80),
    status evaluation_status,
    department_form_id INTEGER,
    evaluation_type_id INTEGER,
    start_date DATE,
    end_date DATE,
    valid boolean NOT NULL DEFAULT TRUE,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying(255),
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by character varying(255)
);

CREATE SEQUENCE evaluations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE evaluations_id_seq OWNED BY evaluations.id;
ALTER TABLE ONLY evaluations ALTER COLUMN id SET DEFAULT nextval('evaluations_id_seq'::regclass);

ALTER TABLE ONLY evaluations
    ADD CONSTRAINT evaluations_pkey PRIMARY KEY (id);

CREATE INDEX evaluations_term_id_idx ON evaluations USING btree (term_id);
CREATE INDEX evaluations_course_number_idx ON evaluations USING btree (course_number);
CREATE INDEX evaluations_instructor_uid_idx ON evaluations USING btree (instructor_uid);

--

CREATE TABLE evaluation_terms (
    term_id VARCHAR(4) NOT NULL,
    is_locked boolean NOT NULL DEFAULT FALSE,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by character varying(255)
);

ALTER TABLE ONLY evaluation_terms ADD CONSTRAINT evaluation_terms_pkey PRIMARY KEY (term_id);

--

CREATE TABLE json_cache (
    id integer NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    department_id INTEGER NOT NULL,
    course_number VARCHAR(5),
    json jsonb,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);

CREATE SEQUENCE json_cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE json_cache_id_seq OWNED BY json_cache.id;
ALTER TABLE ONLY json_cache ALTER COLUMN id SET DEFAULT nextval('json_cache_id_seq'::regclass);

ALTER TABLE ONLY json_cache
    ADD CONSTRAINT json_cache_pkey PRIMARY KEY (id);

CREATE UNIQUE INDEX json_cache_idx ON json_cache USING btree(term_id, department_id, course_number);

--

CREATE TABLE supplemental_instructors (
    ldap_uid VARCHAR(80) NOT NULL,
    sis_id VARCHAR(80),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email_address VARCHAR(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);

ALTER TABLE ONLY supplemental_instructors
    ADD CONSTRAINT supplemental_instructors_pkey PRIMARY KEY (ldap_uid);

--

CREATE TABLE supplemental_sections (
    id integer NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    course_number VARCHAR(5) NOT NULL,
    department_id INTEGER NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);

CREATE SEQUENCE supplemental_sections_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE supplemental_sections_id_seq OWNED BY supplemental_sections.id;
ALTER TABLE ONLY supplemental_sections ALTER COLUMN id SET DEFAULT nextval('supplemental_sections_id_seq'::regclass);

ALTER TABLE ONLY supplemental_sections
    ADD CONSTRAINT supplemental_sections_pkey PRIMARY KEY (id);

CREATE INDEX supplemental_sections_term_id_idx ON supplemental_sections USING btree (term_id);
CREATE INDEX supplemental_sections_course_number_idx ON supplemental_sections USING btree (course_number);
CREATE INDEX supplemental_sections_department_id_idx ON supplemental_sections USING btree (department_id);

--

CREATE TABLE tool_settings (
    id integer NOT NULL,
    key character varying NOT NULL,
    value character varying NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
CREATE SEQUENCE tool_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE tool_settings_id_seq OWNED BY tool_settings.id;
ALTER TABLE ONLY tool_settings ALTER COLUMN id SET DEFAULT nextval('tool_settings_id_seq'::regclass);
ALTER TABLE ONLY tool_settings
    ADD CONSTRAINT tool_settings_key_unique_constraint UNIQUE (key);
ALTER TABLE ONLY tool_settings
    ADD CONSTRAINT tool_settings_pkey PRIMARY KEY (id);
CREATE INDEX tool_settings_key_idx ON tool_settings USING btree (key);

--

CREATE TABLE user_department_forms (
    id integer NOT NULL,
    user_id integer NOT NULL,
    department_form_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE user_department_forms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE user_department_forms_id_seq OWNED BY user_department_forms.id;
ALTER TABLE ONLY user_department_forms ALTER COLUMN id SET DEFAULT nextval('user_department_forms_id_seq'::regclass);

ALTER TABLE ONLY user_department_forms
    ADD CONSTRAINT user_department_forms_pkey PRIMARY KEY (id);

CREATE INDEX user_department_forms_user_id_idx ON user_department_forms USING btree (user_id);
CREATE INDEX user_department_forms_department_form_id_idx ON user_department_forms USING btree (department_form_id);

--

CREATE TYPE user_blue_permissions AS ENUM ('reports_only', 'response_rates');

CREATE TABLE users (
    id integer NOT NULL,
    csid character varying(255),
    uid character varying(255) NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    is_admin boolean,
    blue_permissions user_blue_permissions,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    login_at timestamp with time zone
);

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE users_id_seq OWNED BY users.id;
ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);

ALTER TABLE ONLY users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY users ADD CONSTRAINT users_uid_unique_key UNIQUE (uid);

--

ALTER TABLE ONLY department_catalog_listings
    ADD CONSTRAINT department_catalog_listings_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;
ALTER TABLE ONLY department_catalog_listings
    ADD CONSTRAINT department_catalog_listings_default_form_id_fkey FOREIGN KEY (default_form_id) REFERENCES department_forms(id) ON DELETE CASCADE;

ALTER TABLE ONLY department_members
    ADD CONSTRAINT department_members_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;
ALTER TABLE ONLY department_members
    ADD CONSTRAINT department_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE ONLY department_notes
    ADD CONSTRAINT department_notes_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;

ALTER TABLE ONLY evaluations
    ADD CONSTRAINT evaluations_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;
ALTER TABLE ONLY evaluations
    ADD CONSTRAINT evaluations_department_form_id_fkey FOREIGN KEY (department_form_id) REFERENCES department_forms(id) ON DELETE CASCADE;
ALTER TABLE ONLY evaluations
    ADD CONSTRAINT evaluations_evaluation_type_fkey FOREIGN KEY (evaluation_type_id) REFERENCES evaluation_types(id) ON DELETE CASCADE;

ALTER TABLE ONLY supplemental_sections
    ADD CONSTRAINT supplemental_sections_department_id_fkey FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;

ALTER TABLE ONLY user_department_forms
    ADD CONSTRAINT user_department_forms_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE ONLY user_department_forms
    ADD CONSTRAINT user_department_forms_department_form_id_fkey FOREIGN KEY (department_form_id) REFERENCES department_forms(id) ON DELETE CASCADE;

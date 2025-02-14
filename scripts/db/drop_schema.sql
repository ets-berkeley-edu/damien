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

--

ALTER TABLE IF EXISTS ONLY public.department_catalog_listings DROP CONSTRAINT IF EXISTS department_catalog_listings_department_id_fkey;
ALTER TABLE IF EXISTS ONLY public.department_catalog_listings DROP CONSTRAINT IF EXISTS department_catalog_listings_default_form_id_fkey;
ALTER TABLE IF EXISTS ONLY public.department_forms DROP CONSTRAINT IF EXISTS department_forms_name_unique;
ALTER TABLE IF EXISTS ONLY public.evaluation_types DROP CONSTRAINT IF EXISTS evaluation_types_name_unique;
ALTER TABLE IF EXISTS ONLY public.evaluations DROP CONSTRAINT IF EXISTS evaluations_department_form_id_fkey;
ALTER TABLE IF EXISTS ONLY public.evaluations DROP CONSTRAINT IF EXISTS evaluations_department_id_fkey;
ALTER TABLE IF EXISTS ONLY public.evaluations DROP CONSTRAINT IF EXISTS evaluations_evaluation_type_fkey;
ALTER TABLE IF EXISTS ONLY public.supplemental_sections DROP CONSTRAINT IF EXISTS supplemental_sections_department_id_fkey;

ALTER TABLE IF EXISTS ONLY public.department_members DROP CONSTRAINT IF EXISTS department_members_department_id_fkey;
ALTER TABLE IF EXISTS ONLY public.department_members DROP CONSTRAINT IF EXISTS department_members_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.department_notes DROP CONSTRAINT IF EXISTS department_notes_department_id_fkey;

ALTER TABLE IF EXISTS ONLY public.user_department_forms DROP CONSTRAINT IF EXISTS user_department_forms_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_department_forms DROP CONSTRAINT IF EXISTS user_department_forms_department_form_id_fkey;

--

ALTER TABLE IF EXISTS ONLY public.department_catalog_listings DROP CONSTRAINT IF EXISTS department_catalog_listings_pkey;
ALTER TABLE IF EXISTS public.department_catalog_listings ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.department_forms DROP CONSTRAINT IF EXISTS department_forms_pkey;
ALTER TABLE IF EXISTS public.department_forms ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.department_members DROP CONSTRAINT IF EXISTS department_members_pkey;

ALTER TABLE IF EXISTS ONLY public.department_notes DROP CONSTRAINT IF EXISTS department_notes_pkey;

ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_pkey;
ALTER TABLE IF EXISTS public.departments ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.evaluation_terms DROP CONSTRAINT IF EXISTS evaluation_terms_pkey;

ALTER TABLE IF EXISTS ONLY public.evaluation_types DROP CONSTRAINT IF EXISTS evaluation_types_pkey;
ALTER TABLE IF EXISTS public.evaluation_types ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.evaluations DROP CONSTRAINT IF EXISTS evaluations_pkey;

ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_pkey;
ALTER TABLE IF EXISTS public.json_cache ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.supplemental_sections DROP CONSTRAINT IF EXISTS supplemental_sections_pkey;
ALTER TABLE IF EXISTS public.supplemental_sections ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.supplemental_instructors DROP CONSTRAINT IF EXISTS supplemental_instructors_pkey;

ALTER TABLE IF EXISTS ONLY public.department_catalog_listings DROP CONSTRAINT IF EXISTS department_catalog_listings_pkey;
ALTER TABLE IF EXISTS public.department_catalog_listings ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.tool_settings DROP CONSTRAINT IF EXISTS tool_settings_key_unique_constraint;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.user_department_forms DROP CONSTRAINT IF EXISTS user_department_forms_pkey;
ALTER TABLE IF EXISTS public.user_department_forms ALTER COLUMN id DROP DEFAULT;

--

DROP TABLE IF EXISTS public.exports CASCADE;

DROP SEQUENCE IF EXISTS public.department_catalog_listings_id_seq;
DROP TABLE IF EXISTS public.department_catalog_listings CASCADE;

DROP SEQUENCE IF EXISTS public.user_department_forms_id_seq;
DROP TABLE IF EXISTS public.user_department_forms CASCADE;

DROP SEQUENCE IF EXISTS public.department_forms_id_seq;
DROP TABLE IF EXISTS public.department_forms CASCADE;

DROP TABLE IF EXISTS public.department_members CASCADE;

DROP TABLE IF EXISTS public.department_notes CASCADE;

DROP SEQUENCE IF EXISTS public.departments_id_seq;
DROP TABLE IF EXISTS public.departments CASCADE;

DROP TABLE IF EXISTS public.evaluation_terms CASCADE;

DROP SEQUENCE IF EXISTS public.evaluation_types_id_seq;
DROP TABLE IF EXISTS public.evaluation_types CASCADE;

DROP SEQUENCE IF EXISTS public.evaluations_id_seq CASCADE;
DROP TABLE IF EXISTS public.evaluations CASCADE;

DROP SEQUENCE IF EXISTS public.json_cache_id_seq CASCADE;
DROP TABLE IF EXISTS public.json_cache CASCADE;

DROP TABLE IF EXISTS public.supplemental_instructors CASCADE;

DROP SEQUENCE IF EXISTS public.supplemental_sections_id_seq;
DROP TABLE IF EXISTS public.supplemental_sections CASCADE;

DROP SEQUENCE IF EXISTS public.tool_settings_id_seq CASCADE;
DROP TABLE IF EXISTS public.tool_settings CASCADE;

DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users CASCADE;

--

DROP TYPE IF EXISTS public.evaluation_status;
DROP TYPE IF EXISTS public.export_status;
DROP TYPE IF EXISTS public.user_blue_permissions;

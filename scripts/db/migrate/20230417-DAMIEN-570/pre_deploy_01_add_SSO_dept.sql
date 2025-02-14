/**
 * Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies, TRUE),
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue, TRUE),
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu, TRUE),
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, TRUE),
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, TRUE),
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

BEGIN;

INSERT INTO departments (dept_name, is_enrolled, created_at, updated_at) VALUES
    ('Summer Sessions Online', TRUE, now(), now());

INSERT INTO department_catalog_listings (department_id, subject_area, catalog_id, default_form_id, custom_evaluation_types, start_term_id, created_at, updated_at) (
    SELECT d.id, '', '[^[A-Z0-9]*]', NULL, FALSE, '2235', now(), now()
    FROM departments d
    WHERE d.dept_name = 'Summer Sessions Online'
);

COMMIT;

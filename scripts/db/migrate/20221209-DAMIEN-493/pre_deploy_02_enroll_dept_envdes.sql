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

BEGIN;

UPDATE departments SET is_enrolled = true WHERE dept_name = 'Environmental Design';
UPDATE department_catalog_listings SET end_term_id = '2228' WHERE subject_area = 'ENVDES' AND department_id = (SELECT id FROM departments WHERE dept_name = 'Architecture');
INSERT INTO department_catalog_listings (department_id, subject_area, catalog_id, default_form_id, custom_evaluation_types, start_term_id, created_at, updated_at) (
    SELECT d.id, dcl.subject_area, dcl.catalog_id, dcl.default_form_id, dcl.custom_evaluation_types, '2232', now(), now()
    FROM departments d, department_catalog_listings dcl
    WHERE d.dept_name = 'Environmental Design'
    AND dcl.subject_area = 'ENVDES' AND dcl.department_id = (SELECT id FROM departments WHERE dept_name = 'Architecture')
);

COMMIT;
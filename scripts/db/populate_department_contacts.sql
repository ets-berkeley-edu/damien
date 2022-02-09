/**
 * Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.
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

TRUNCATE TABLE department_members;
DELETE FROM users WHERE NOT is_admin;

WITH contacts AS (
  INSERT INTO users (csid, uid, first_name, last_name, email, is_admin, can_receive_communications, can_view_response_rates, created_at, updated_at, deleted_at) VALUES
  ('100100100', '100', 'Father', 'Brennan', 'fatherbrennan@berkeley.edu', FALSE, FALSE, FALSE, now(), now(), NULL),
  ('300300300', '300', 'Robert', 'Thorn', 'rt@berkeley.edu', FALSE, FALSE, FALSE, now(), now(), NULL),
  ('400400400', '400', 'Kathy', 'Thorn', 'kt@berkeley.edu', FALSE, FALSE, TRUE, now(), now(), NULL),
  (NULL, '500', 'Keith', 'Jennings', 'kj@berkeley.edu', FALSE, FALSE, TRUE, now(), now(), NULL)
  RETURNING id
)
INSERT INTO department_members (department_id, user_id, created_at, updated_at)
SELECT
  departments.id, contacts.id, now(), now()
FROM
  departments, contacts
WHERE
  departments.dept_name = 'Philosophy'
;

COMMIT;
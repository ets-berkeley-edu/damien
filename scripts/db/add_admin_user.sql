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

--
-- Register UID as Damien admin
--
-- USAGE:
--   psql ... -v csid=123456789 -v uid=123456 -v first_name=Keith -v last_name=Jennings -v email=kj@berkeley.edu -f scripts/db/add_admin_user.sql
--

-- Create admin user
INSERT INTO users (csid, uid, first_name, last_name, email, is_admin, blue_permissions, created_at, updated_at)
  SELECT :'csid', :'uid', :'first_name', :'last_name', :'email', true, NULL, now(), now()
  WHERE NOT EXISTS (SELECT id FROM users WHERE uid = :'uid');

-- If the UID represents an existing user, ensure deleted_at is null and permissions are granted.
UPDATE users SET deleted_at = NULL WHERE uid = :'uid';
UPDATE users SET is_admin = true WHERE uid = :'uid';

-- Done

COMMIT;
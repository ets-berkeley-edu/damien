"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from damien.models.json_cache import JsonCache
from flask import current_app as app


def clear_department_cache(department_id, term_id):
    app.logger.debug(f'Clearing department cache (department_id={department_id}, term_id={term_id})')
    JsonCache.clear_department(term_id, department_id)


def clear_department_section_cache(department_id, term_id, course_number):
    app.logger.debug(f'Clearing department section cache (department_id={department_id}, term_id={term_id}, course_number={course_number})')
    JsonCache.clear_department_section(term_id, department_id, course_number)


def clear_section_cache(term_id, course_number):
    app.logger.debug(f'Clearing section cache (term_id={term_id}, course_number={course_number})')
    JsonCache.clear_section(term_id, course_number)


def delete_from_cache(token):
    app.logger.debug(f'Deleting from cache (json LIKE {token})')
    JsonCache.delete_matching(token)


def fetch_all_departments(term_id):
    app.logger.debug(f'Fetching departments (term_id={term_id})')
    return {d.department_id: d.json for d in JsonCache.fetch_all_departments(term_id)}


def fetch_all_sections(department_id, term_id):
    app.logger.debug(f'Fetching department sections (department_id={department_id}, term_id={term_id})')
    return {s.course_number: s.json for s in JsonCache.fetch_all_sections(term_id, department_id)}


def fetch_department_cache(department_id, term_id):
    app.logger.debug(f'Fetching department cache (department_id={department_id}, term_id={term_id})')
    return JsonCache.fetch_department(term_id, department_id)


def fetch_section_cache(department_id, term_id, course_number):
    app.logger.debug(f'Fetching section cache (department_id={department_id}, term_id={term_id}, course_number={course_number})')
    return JsonCache.fetch_section(term_id, department_id, course_number)


def set_department_cache(department_id, term_id, cached):
    app.logger.debug(f'Setting department cache (department_id={department_id}, term_id={term_id})')
    JsonCache.set_department(term_id, department_id, cached)


def set_section_cache(department_id, term_id, course_number, cached):
    app.logger.debug(f'Setting section cache (department_id={department_id}, term_id={term_id}, course_number={course_number})')
    JsonCache.set_section(term_id, department_id, course_number, cached)

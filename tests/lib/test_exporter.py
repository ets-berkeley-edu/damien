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

from unittest import mock

from damien.lib.exporter import _carry_forward_course_rows, _carry_forward_students

# 2021-D is the term code for SIS term id 2218.
past_term_export_path = 'exports/2218/2021_12_21_03_03_03'


def _csv_lines(rows):
    """Simulate what stream_object_text returns: an iterable of raw CSV lines."""
    return iter(rows)


class TestCarryForwardCourseRows:
    """Only rows belonging to the immediate past term should be carried forward."""

    def test_no_previous_term(self):
        # When there's no previous term (e.g., the earliest supported term), nothing is carried forward.
        with mock.patch('damien.lib.exporter.stream_object_text') as mock_stream:
            assert _carry_forward_course_rows(past_term_export_path, 'courses.csv', None) == []
            mock_stream.assert_not_called()

    def test_filters_by_previous_term_course_id_prefix(self):
        rows = _csv_lines([
            'COURSE_ID,LDAP_UID\n',
            '2021-D-12345,11111\n',
            '2021-D-12345,22222\n',
            '2021-C-99999,33333\n',
        ])
        with mock.patch('damien.lib.exporter.stream_object_text', return_value=rows):
            result = _carry_forward_course_rows(past_term_export_path, 'course_students.csv', '2218')
        assert result == [
            {'COURSE_ID': '2021-D-12345', 'LDAP_UID': '11111'},
            {'COURSE_ID': '2021-D-12345', 'LDAP_UID': '22222'},
        ]

    def test_missing_past_export_file(self):
        with mock.patch('damien.lib.exporter.stream_object_text', return_value=None):
            assert _carry_forward_course_rows(past_term_export_path, 'courses.csv', '2218') == []


class TestCarryForwardStudents:
    """students.csv rows must stay unique by LDAP_UID.

    Only past-term students who are also present in the carried-forward course_students.csv rows are carried
    forward, with current-term rows winning on conflict.
    """

    def test_carries_forward_only_students_matching_course_students_uids(self):
        rows = _csv_lines([
            'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS\n',
            '11111,12311111,Old,Carriedforward,old11111@berkeley.edu\n',
            '55555,12355555,Uncarried,Notincoursestudents,old55555@berkeley.edu\n',
        ])
        current_term_students = [{'LDAP_UID': '88888', 'SIS_ID': '12388888', 'FIRST_NAME': 'New', 'LAST_NAME': 'Student', 'EMAIL_ADDRESS': 'n@b.edu'}]
        with mock.patch('damien.lib.exporter.stream_object_text', return_value=rows):
            result = _carry_forward_students(past_term_export_path, {'11111'}, current_term_students)
        assert result == [
            {'LDAP_UID': '11111', 'SIS_ID': '12311111', 'FIRST_NAME': 'Old', 'LAST_NAME': 'Carriedforward', 'EMAIL_ADDRESS': 'old11111@berkeley.edu'},
            {'LDAP_UID': '88888', 'SIS_ID': '12388888', 'FIRST_NAME': 'New', 'LAST_NAME': 'Student', 'EMAIL_ADDRESS': 'n@b.edu'},
        ]

    def test_current_term_rows_overwrite_past_term_rows_on_conflict(self):
        rows = _csv_lines([
            'LDAP_UID,SIS_ID,FIRST_NAME,LAST_NAME,EMAIL_ADDRESS\n',
            '77777,OLDSTALE,Stale,Shouldbeoverwritten,stale77777@berkeley.edu\n',
        ])
        current_term_students = [
            {'LDAP_UID': '77777', 'SIS_ID': '12377777', 'FIRST_NAME': 'Sutherland', 'LAST_NAME': 'Northen', 'EMAIL_ADDRESS': 'snorthen@berkeley.edu'},
        ]
        with mock.patch('damien.lib.exporter.stream_object_text', return_value=rows):
            result = _carry_forward_students(past_term_export_path, {'77777'}, current_term_students)
        assert result == [
            {'LDAP_UID': '77777', 'SIS_ID': '12377777', 'FIRST_NAME': 'Sutherland', 'LAST_NAME': 'Northen', 'EMAIL_ADDRESS': 'snorthen@berkeley.edu'},
        ]

    def test_missing_past_export_file(self):
        current_term_students = [{'LDAP_UID': '88888', 'SIS_ID': '12388888', 'FIRST_NAME': 'New', 'LAST_NAME': 'Student', 'EMAIL_ADDRESS': 'n@b.edu'}]
        with mock.patch('damien.lib.exporter.stream_object_text', return_value=None):
            result = _carry_forward_students(past_term_export_path, {'11111'}, current_term_students)
        assert result == current_term_students

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

from datetime import datetime
import re

from flask import current_app as app
import pytz


def camelize(string):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in string.split('_'))


def extract_int(string):
    numeric_only = ''.join(filter(str.isdigit, string)) if string else None
    return to_int(numeric_only) or 0


def get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def get_eb_environment():
    return app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None


def isoformat(value):
    return value and value.astimezone(pytz.timezone(app.config['TIMEZONE'])).isoformat()


def parse_search_snippet(snippet, uid_col='ldap_uid'):
    params = {}
    words = list(set(snippet.upper().split()))
    # A single numeric string indicates a UID search.
    if len(words) == 1 and re.match(r'^\d+$', words[0]):
        query_filter = f' WHERE {uid_col} LIKE :uid_prefix'
        params.update({'uid_prefix': f'{words[0]}%'})
    # Otherwise search by name.
    else:
        query_filter = ' WHERE TRUE'
        for i, word in enumerate(words):
            query_filter += f' AND (first_name ILIKE :name_phrase_{i} OR last_name ILIKE :name_phrase_{i})'
            params.update({f'name_phrase_{i}': f'%{word}%'})
    return query_filter, params


def resolve_sql_template_string(template_string, **kwargs):
    """Our DDL template files are simple enough to use standard Python string formatting."""
    template_data = {
        'dblink_nessie_rds': app.config['DBLINK_NESSIE_RDS'],
    }
    # Kwargs may be passed in to modify default template data.
    template_data.update(kwargs)
    return template_string.format(**template_data)


def resolve_sql_template(sql_filename, **kwargs):
    with open(app.config['BASE_DIR'] + f'/damien/sql_templates/{sql_filename}', encoding='utf-8') as file:
        template_string = file.read()
    # Let's leave the preprended copyright and license text out of this.
    template_string = re.sub(r'^/\*.*?\*/\s*', '', template_string, flags=re.DOTALL)
    return resolve_sql_template_string(template_string, **kwargs)


def safe_strftime(date, date_format):
    return datetime.strftime(date, date_format) if date else None


def to_bool_or_none(arg):
    """
    On the principle of "no decision is a decision," this util has three possible outcomes: True, False and None.

    If arg is type string, handle 'true'/'false' values or return None.
    If arg is NOT type string and NOT None, fall back to Python's bool().
    """
    s = arg
    if isinstance(arg, str):
        s = arg.strip().lower()
        s = True if s == 'true' else s
        s = False if s == 'false' else s
        s = None if s not in [True, False] else s
    return None if s is None else bool(s)


def to_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

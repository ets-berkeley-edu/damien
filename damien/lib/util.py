"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

from dateutil.tz import tzutc
from flask import current_app as app
import pytz


def get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


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


def to_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

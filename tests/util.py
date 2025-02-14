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

from contextlib import contextmanager

import boto3
import moto


@contextmanager
def mock_s3_bucket(app):
    with moto.mock_s3():
        bucket = app.config['AWS_S3_BUCKET']
        s3 = boto3.resource('s3', app.config['AWS_S3_REGION'])
        bucket = s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': app.config['AWS_S3_REGION']})

        # Fall 2021 export data to be picked up by Spring 2022 jobs.
        with open(f"{app.config['FIXTURES_PATH']}/legacy_course_instructors.csv", 'rb') as f:
            bucket.put_object(Key='exports/2218/2021_12_21_03_03_03/course_instructors.csv', Body=f)

        yield s3


@contextmanager
def override_config(app, key, value):
    """Temporarily override an app config value."""
    old_value = app.config[key]
    app.config[key] = value
    try:
        yield
    finally:
        app.config[key] = old_value

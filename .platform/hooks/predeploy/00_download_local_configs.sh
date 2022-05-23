#!/bin/bash
PYTHONPATH='' aws s3 cp s3://damien-deploy-configs/damien/${EB_ENVIRONMENT}.py config/production-local.py
printf "\nEB_ENVIRONMENT = '${EB_ENVIRONMENT}'\n\n" >> config/production-local.py
chown webapp config/production-local.py
chmod 400 config/production-local.py

PYTHONPATH='' aws s3 cp s3://damien-deploy-configs/damien/${EB_ENVIRONMENT}_rsa config/damien_rsa
chown webapp config/damien_rsa
chmod 400 config/damien_rsa

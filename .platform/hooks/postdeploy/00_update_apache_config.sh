#!/bin/bash
sudo mv /tmp/damien.conf /etc/httpd/conf.d/damien.conf
sudo /bin/systemctl restart httpd.service

#!/bin/bash

#create folders
mkdir -p /home/webuser/docker_data/microcalendar/database
mkdir -p /home/webuser/docker_data/microcalendar/key

chown webuser:www-data /home/webuser/docker_data
chown webuser:www-data /home/webuser/docker_data/microcalendar
chown webuser:www-data /home/webuser/docker_data/microcalendar/database
chmod u=rwx,g=rx,o-rwx /home/webuser/docker_data
chmod u=rwx,g=rx,o-rwx /home/webuser/docker_data/microcalendar
chmod u=rwx,g=rx,o-rwx /home/webuser/docker_data/microcalendar/database

chown root:root /home/webuser/docker_data/microcalendar/key


#generate ssl key
openssl req -new -x509 -days 20000 -keyout server.key -out server.pem

cp server.key{,.orig}
openssl rsa -in server.key.orig -out server.key
rm server.key.orig

#put key to folder
mv --force ./server.key /home/webuser/docker_data/microcalendar/key
mv --force ./server.pem /home/webuser/docker_data/microcalendar/key

chmod u=rx,g-rwx,o-rwx /home/webuser/docker_data/microcalendar/key
chmod u=r,g-rwx,o-rwx /home/webuser/docker_data/microcalendar/key/server.key
chmod u=r,g-rwx,o-rwx /home/webuser/docker_data/microcalendar/key/server.pem

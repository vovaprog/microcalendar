#!/bin/bash

docker run -d -p 9000:443 -v /home/webuser/docker_data/microcalendar:/home/webuser/data/microcalendar microcalendar


#!/bin/bash

docker run -i -t -p 9000:443 --entrypoint /bin/bash -v /home/webuser/docker_data/microcalendar:/home/webuser/data/microcalendar microcalendar


FROM debian

RUN apt-get update && apt-get -y install apache2 python-flask libapache2-mod-wsgi git python-flaskext.wtf
RUN apt-get -y install mc

RUN useradd -m -G www-data webuser

RUN a2enmod rewrite
RUN a2enmod ssl
RUN a2ensite default-ssl

RUN mkdir /home/webuser/applications && \
    mkdir -p /home/webuser/data/microcalendar

# change echo message to clone new version of program
RUN git clone https://github.com/vovaprog/microcalendar /home/webuser/applications/microcalendar && echo "git clone 1"

COPY ./config/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf
COPY ./config/microcalendar.wsgi /var/www/microcalendar/microcalendar.wsgi
COPY ./config/settings.py /home/webuser/applications/microcalendar/settings.py

RUN chown --recursive webuser:www-data /home/webuser/applications/microcalendar && \
    chown webuser:www-data /home/webuser/applications && \
    chown --recursive webuser:www-data /home/webuser/data && \
    chown webuser:www-data /home/webuser/data && \
    chown --recursive webuser:www-data /var/www/microcalendar && \
    find /home/webuser/applications/microcalendar -type d -exec chmod u=rx,g=rx,o-rwx {} \; && \
    find /home/webuser/applications/microcalendar -type f -exec chmod u=r,g=r,o-rwx {} \; && \
    chmod u=rx,g=rx,o-rwx /home/webuser/applications && \
    chmod u=rx,g=rx,o-rwx /var/www/microcalendar && \
    chmod u=r,g=r,o-rwx /var/www/microcalendar/microcalendar.wsgi

EXPOSE 443

ENTRYPOINT /usr/sbin/apache2ctl -D FOREGROUND


FROM mysql:8.0
# Copy config and init folders
COPY mysql/conf.d /etc/mysql/conf.d
COPY mysql/init    /docker-entrypoint-initdb.d
# Copy our wrapper and make it the new ENTRYPOINT
COPY mysql/docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh
ENTRYPOINT ["docker-entrypoint-wrapper.sh"]
CMD ["mysqld"] 
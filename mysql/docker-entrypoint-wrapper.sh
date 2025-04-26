#!/bin/bash
set -e
export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"

# background the official entrypoint (this will
# initialize an empty DB and then exec mysqld)
docker-entrypoint.sh "$@" &
pid=$!

echo "waiting for MySQL to come up…"
until mysqladmin ping -uroot --silent; do
  sleep 1
done

echo "re-applying init scripts…"
for f in /docker-entrypoint-initdb.d/*; do
  case "$f" in
    *.sql) echo "running $f"; mysql -uroot "$MYSQL_DATABASE" < "$f" ;;
    *.sh)  echo "sourcing $f"; . "$f" ;;
    *)     echo "skipping $f" ;;
  esac
done

wait "$pid"
#!/bin/bash

set -e

setup_passwords() {
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        \set postgres_pwd '${POSTGRES_PWD//\'/\'\'}'
        \set app_pwd '${POSTGRES_ADMIN_PWD//\'/\'\'}'
        
        ALTER ROLE postgres WITH PASSWORD :'postgres_pwd';
        
        CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD :'app_pwd';
        CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};
        
        \echo 'Passwords successfully updated'
EOSQL
}

if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
    echo "First run, setting up passwords..."
    setup_passwords
else
    echo "Data directory exists, skipping password setup"
fi

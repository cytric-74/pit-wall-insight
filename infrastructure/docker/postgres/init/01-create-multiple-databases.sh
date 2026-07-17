#!/bin/bash
# Runs automatically on first container boot via docker-entrypoint-initdb.d.
# POSTGRES_DB (raw layer) is created by the base postgres image itself;
# this script creates any additional databases listed in POSTGRES_MULTIPLE_DATABASES
# (comma-separated), e.g. the analytics/gold layer database.
set -e
set -u

function create_database() {
	local database=$1
	echo "Creating database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE DATABASE "$database";
	EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
		create_database "$db"
	done
	echo "Multiple databases created"
fi

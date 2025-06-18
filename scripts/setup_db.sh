#!/bin/bash
set -e

until sudo -u postgres pg_isready; do sleep 1; done

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'outline'" | grep -q 1 || sudo -u postgres createdb outline
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'outline'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER outline WITH PASSWORD 'outline_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE outline TO outline;"
#!/bin/bash
set -e

echo "🗄️  Initializing PostgreSQL for Outline..."

if [ ! -f /var/lib/postgresql/main/PG_VERSION ]; then
  echo "   Creating database cluster..."
  cd /var/lib/postgresql
  sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/main --auth-local=trust --auth-host=md5 --no-sync
  
  echo "   Configuring PostgreSQL..."
  # Configure PostgreSQL for local connections
  sudo -u postgres tee /var/lib/postgresql/main/postgresql.conf > /dev/null << EOF
# PostgreSQL configuration for Outline development
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
log_line_prefix = '%t [%p]: '
log_statement = 'none'
log_min_duration_statement = 1000
EOF

  # Configure authentication for both IPv4 and IPv6
  sudo -u postgres tee /var/lib/postgresql/main/pg_hba.conf > /dev/null << EOF
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
EOF

  echo "✅ PostgreSQL initialized and configured"
else
  echo "✅ PostgreSQL already initialized"
fi
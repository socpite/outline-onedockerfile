#!/bin/bash
set -e

# Ensure we're in the right directory
cd /var/lib/postgresql

# Initialize database if it doesn't exist
if [ ! -f /var/lib/postgresql/main/PG_VERSION ]; then
    echo "Initializing PostgreSQL database..."
    /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/main --auth-local=trust --auth-host=md5 --no-sync
    
    # Configure PostgreSQL
    cat > /var/lib/postgresql/main/postgresql.conf << EOF
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
log_line_prefix = '%t [%p]: '
EOF

    cat > /var/lib/postgresql/main/pg_hba.conf << EOF
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF
    
    echo "PostgreSQL initialized successfully"
fi

# Start PostgreSQL
exec /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/main
#!/bin/bash
set -e

# Initialize if needed
if [ ! -f /var/lib/postgresql/main/PG_VERSION ]; then
    echo "Initializing PostgreSQL..."
    cd /var/lib/postgresql
    /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/main --auth-local=trust --auth-host=md5
    
    # Basic config
    cat >> /var/lib/postgresql/main/postgresql.conf << EOF
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
EOF
fi

# Start postgres
exec /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/main
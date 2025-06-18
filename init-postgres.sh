#!/bin/bash
set -e

echo "🗄️  Manual PostgreSQL Initialization Script"
echo "=========================================="

# Check if running in container
if [ ! -f /.dockerenv ]; then
    echo "❌ This script should be run inside the Docker container"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "👤 Current user: $(whoami)"

# Navigate to postgres directory
cd /var/lib/postgresql

echo "🔍 Checking PostgreSQL status..."
if [ -f /var/lib/postgresql/main/PG_VERSION ]; then
    echo "✅ PostgreSQL already initialized"
    echo "📄 Version: $(cat /var/lib/postgresql/main/PG_VERSION)"
else
    echo "🚀 Initializing PostgreSQL database..."
    
    # Initialize with no-sync to avoid hanging
    sudo -u postgres /usr/lib/postgresql/15/bin/initdb \
        -D /var/lib/postgresql/main \
        --auth-local=trust \
        --auth-host=md5 \
        --no-sync
    
    echo "⚙️  Configuring PostgreSQL..."
    
    # Create basic config
    sudo -u postgres tee /var/lib/postgresql/main/postgresql.conf > /dev/null << 'EOF'
# PostgreSQL configuration for Outline
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
log_line_prefix = '%t [%p]: '
log_statement = 'none'
EOF

    # Create authentication config
    sudo -u postgres tee /var/lib/postgresql/main/pg_hba.conf > /dev/null << 'EOF'
# PostgreSQL Client Authentication Configuration
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

    echo "✅ PostgreSQL initialized successfully"
fi

echo ""
echo "🧪 Testing PostgreSQL startup..."

# Test if postgres can start
sudo -u postgres /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/main &
PG_PID=$!

# Wait a moment for startup
sleep 3

# Check if it's running
if kill -0 $PG_PID 2>/dev/null; then
    echo "✅ PostgreSQL started successfully (PID: $PG_PID)"
    
    # Test connection
    sleep 2
    if sudo -u postgres pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        echo "✅ PostgreSQL is accepting connections"
        
        # Create outline database and user
        echo "🔧 Setting up Outline database..."
        sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'outline'" | grep -q 1 || \
            sudo -u postgres createdb outline
        
        sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'outline'" | grep -q 1 || \
            sudo -u postgres psql -c "CREATE USER outline WITH PASSWORD 'outline_password';"
        
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE outline TO outline;"
        sudo -u postgres psql -d outline -c "GRANT ALL ON SCHEMA public TO outline;"
        
        echo "✅ Outline database setup complete"
    else
        echo "❌ PostgreSQL not accepting connections"
    fi
    
    # Stop the test instance
    kill $PG_PID 2>/dev/null || true
    wait $PG_PID 2>/dev/null || true
    echo "🛑 Test PostgreSQL instance stopped"
else
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

echo ""
echo "🎉 PostgreSQL initialization complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Start PostgreSQL: sudo -u postgres /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/main &"
echo "   2. Or use dinit: dinitctl start postgres"
echo "   3. Check status: sudo -u postgres pg_isready -h localhost -p 5432"
echo ""
echo "🔗 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: outline"
echo "   User: outline"
echo "   Password: outline_password"
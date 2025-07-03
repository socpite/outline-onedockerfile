#!/usr/bin/env node
// Outline Simple Import Script - Improved Version
// Fixed encoding issues, foreign key handling, and error handling

const { Sequelize } = require('sequelize');
const fs = require('fs');
const path = require('path');

// Change to Outline directory to access node_modules
process.chdir('/home/ubuntu/outline');

const args = process.argv.slice(2);
const importDir = args[0];
const force = args.includes('--force');
const verbose = args.includes('--verbose');

function log(message) {
    console.log(`[${new Date().toISOString()}] ${message}`);
}

function error(message) {
    console.error(`❌ ERROR: ${message}`);
    process.exit(1);
}

function warn(message) {
    console.warn(`⚠️  WARNING: ${message}`);
}

if (!importDir) {
    console.error('Usage: outline-import-simple-v2 <import-directory> [--force] [--verbose]');
    process.exit(1);
}

if (!process.env.DATABASE_URL) {
    error('DATABASE_URL environment variable is required');
}

async function importData() {
    const sequelize = new Sequelize(process.env.DATABASE_URL, {
        dialect: 'postgres',
        logging: verbose ? console.log : false
    });

    try {
        log('🔗 Connecting to database...');
        await sequelize.authenticate();

        // Check if data exists
        const [existingTeams] = await sequelize.query('SELECT COUNT(*) as count FROM teams');
        const [existingUsers] = await sequelize.query('SELECT COUNT(*) as count FROM users');
        const [existingDocs] = await sequelize.query('SELECT COUNT(*) as count FROM documents');
        
        const hasData = existingTeams[0].count > 0 || existingUsers[0].count > 0 || existingDocs[0].count > 0;
        
        if (hasData && !force) {
            console.log('⚠️  Existing data found:');
            console.log(`   Teams: ${existingTeams[0].count}`);
            console.log(`   Users: ${existingUsers[0].count}`);
            console.log(`   Documents: ${existingDocs[0].count}`);
            console.log('');
            console.log('Use --force to overwrite existing data');
            process.exit(1);
        }

        // Load export data
        const jsonFile = path.join(importDir, 'workspace.json');
        if (!fs.existsSync(jsonFile)) {
            error('workspace.json not found in import directory');
        }

        log('📊 Loading export data...');
        let exportData;
        try {
            const rawData = fs.readFileSync(jsonFile, 'utf8');
            exportData = JSON.parse(rawData);
        } catch (e) {
            error(`Failed to parse JSON: ${e.message}`);
        }
        
        log(`📅 Export from: ${exportData.exportedAt || 'Unknown'}`);

        // Import in dependency order
        const tables = [
            'teams', 'users', 'collections', 'groups', 'documents', 
            'attachments', 'shares', 'stars', 'pins', 'views', 
            'memberships', 'group_users'
        ];

        log('🗃️  Importing database...');
        
        for (const table of tables) {
            const data = exportData[table] || [];
            
            if (data.length === 0) {
                log(`   ${table}: no data`);
                continue;
            }

            log(`   ${table}: importing ${data.length} records...`);
            
            // Clear existing data if force mode
            if (force) {
                try {
                    await sequelize.query(`TRUNCATE TABLE "${table}" CASCADE`);
                } catch (err) {
                    verbose && warn(`Could not truncate ${table}: ${err.message}`);
                }
            }
            
            let successCount = 0;
            
            // Process records with better error handling
            for (const record of data) {
                try {
                    // Fix common data issues
                    const fixedRecord = await fixRecord(table, record, sequelize);
                    
                    if (!fixedRecord) {
                        continue; // Skip invalid records
                    }
                    
                    const columns = Object.keys(fixedRecord);
                    const values = Object.values(fixedRecord);
                    
                    const placeholders = values.map((_, index) => `$${index + 1}`).join(', ');
                    const query = `INSERT INTO "${table}" (${columns.map(c => `"${c}"`).join(', ')}) VALUES (${placeholders})`;
                    
                    await sequelize.query(query, {
                        bind: values,
                        type: sequelize.QueryTypes.INSERT
                    });
                    
                    successCount++;
                    
                } catch (err) {
                    verbose && warn(`Failed to insert record in ${table}: ${err.message}`);
                }
            }
            
            log(`   ✅ ${table}: ${successCount} imported`);
        }

        // Show import summary
        await showImportSummary(sequelize, exportData, importDir);

        // Grant full permissions to all users on all collections
        await grantFullPermissionsToAllUsers(sequelize);

        log('✅ Import completed successfully!');
        
    } catch (error) {
        console.error('❌ Import failed:', error.message);
        process.exit(1);
    } finally {
        await sequelize.close();
    }
}

async function showImportSummary(sequelize, exportData, importDir) {
    console.log('\n📊 Import Summary');
    console.log('==================');
    
    // Show export metadata
    const exportDate = exportData.exportedAt || 'Unknown';
    const exportVersion = exportData.version || 'Unknown';
    console.log(`📅 Export Date: ${exportDate}`);
    console.log(`🏷️  Export Version: ${exportVersion}`);
    
    // Show database statistics
    try {
        const [teams] = await sequelize.query('SELECT COUNT(*) as count FROM teams');
        const [users] = await sequelize.query('SELECT COUNT(*) as count FROM users');
        const [collections] = await sequelize.query('SELECT COUNT(*) as count FROM collections');
        const [documents] = await sequelize.query('SELECT COUNT(*) as count FROM documents');
        
        console.log(`👥 Teams: ${teams[0].count}`);
        console.log(`👤 Users: ${users[0].count}`);
        console.log(`📚 Collections: ${collections[0].count}`);
        console.log(`📄 Documents: ${documents[0].count}`);
    } catch (e) {
        console.log('👥 Teams: 0');
        console.log('👤 Users: 0');
        console.log('📚 Collections: 0');
        console.log('📄 Documents: 0');
    }
    
    // Show file statistics
    try {
        const { execSync } = require('child_process');
        const dataDir = '/var/lib/outline/data';
        
        if (fs.existsSync(dataDir)) {
            const fileCount = execSync(`find "${dataDir}" -type f | wc -l`, { encoding: 'utf8' }).trim();
            const totalSize = execSync(`du -sh "${dataDir}" | cut -f1`, { encoding: 'utf8' }).trim();
            console.log(`📎 Files: ${fileCount} files (${totalSize})`);
        } else {
            console.log('📎 Files: 0 files (0B)');
        }
    } catch (e) {
        console.log('📎 Files: 0 files (0B)');
    }
}

async function createDefaultCollection(sequelize, teamId) {
    const { v4: uuidv4 } = require('uuid');
    const collectionId = uuidv4();
    const now = new Date().toISOString();
    
    const defaultCollection = {
        id: collectionId,
        name: 'Imported Documents',
        description: 'Default collection for imported documents without collections',
        teamId: teamId,
        createdAt: now,
        updatedAt: now,
        deletedAt: null,
        sharing: true,
        sort: JSON.stringify({"field": "title", "direction": "asc"}),
        permission: null,
        maintainerApprovalRequired: false,
        documentStructure: null,
        importId: null
    };
    
    try {
        const columns = Object.keys(defaultCollection);
        const values = Object.values(defaultCollection);
        const placeholders = values.map((_, index) => `$${index + 1}`).join(', ');
        const query = `INSERT INTO "collections" (${columns.map(c => `"${c}"`).join(', ')}) VALUES (${placeholders})`;
        
        await sequelize.query(query, {
            bind: values,
            type: sequelize.QueryTypes.INSERT
        });
        
        log(`   Created default collection: ${collectionId}`);
        return collectionId;
    } catch (error) {
        warn(`Failed to create default collection: ${error.message}`);
        return null;
    }
}

async function fixRecord(table, record, sequelize) {
    if (!record || !record.id) {
        return null;
    }
    
    const fixed = { ...record };
    
    // Ensure timestamps
    const now = new Date().toISOString();
    if (!fixed.createdAt) fixed.createdAt = now;
    if (!fixed.updatedAt) fixed.updatedAt = now;
    
    // Table-specific fixes
    if (table === 'documents') {
        // Handle missing collections
        if (!fixed.collectionId) {
            // Check if any collections exist
            try {
                const [collections] = await sequelize.query('SELECT id FROM collections LIMIT 1');
                if (collections.length > 0) {
                    fixed.collectionId = collections[0].id;
                    verbose && log(`   Assigned document to existing collection: ${collections[0].id}`);
                } else {
                    // Create default collection
                    const teamId = fixed.teamId;
                    if (teamId) {
                        const defaultCollectionId = await createDefaultCollection(sequelize, teamId);
                        if (defaultCollectionId) {
                            fixed.collectionId = defaultCollectionId;
                            verbose && log(`   Assigned document to new default collection: ${defaultCollectionId}`);
                        } else {
                            warn(`Skipping document '${fixed.title || 'Unknown'}' - no valid collection`);
                            return null;
                        }
                    } else {
                        warn(`Skipping document '${fixed.title || 'Unknown'}' - no team ID`);
                        return null;
                    }
                }
            } catch (error) {
                warn(`Error checking collections: ${error.message}`);
                return null;
            }
        }
        
        // Fix content
        if (!fixed.content) {
            if (fixed.text) {
                fixed.content = {
                    type: "doc",
                    content: [{
                        type: "paragraph",
                        content: [{ type: "text", text: fixed.text }]
                    }]
                };
            } else {
                fixed.content = {
                    type: "doc",
                    content: [{ type: "paragraph" }]
                };
            }
        }
        
        if (typeof fixed.content === 'object') {
            fixed.content = JSON.stringify(fixed.content);
        }
        if (!fixed.collaboratorIds) {
            fixed.collaboratorIds = [];
        }
        if (Array.isArray(fixed.collaboratorIds)) {
            fixed.collaboratorIds = JSON.stringify(fixed.collaboratorIds);
        }
    }
    
    return fixed;
}

async function grantFullPermissionsToAllUsers(sequelize) {
    log('🔐 Granting full read-write permissions to all users on all collections...');
    
    try {
        // Get all users
        const [users] = await sequelize.query('SELECT id FROM users');
        const userIds = users.map(user => user.id);
        
        // Get all collections
        const [collections] = await sequelize.query('SELECT id FROM collections');
        const collectionIds = collections.map(collection => collection.id);
        
        if (userIds.length === 0) {
            log('   No users found - skipping permission setup');
            return;
        }
        
        if (collectionIds.length === 0) {
            log('   No collections found - skipping permission setup');
            return;
        }
        
        log(`   Found ${userIds.length} users and ${collectionIds.length} collections`);
        
        let permissionsCreated = 0;
        let permissionsUpdated = 0;
        const { v4: uuidv4 } = require('uuid');
        const now = new Date().toISOString();
        
        // Create user_permissions records for all user-collection combinations
        for (const userId of userIds) {
            for (const collectionId of collectionIds) {
                try {
                    // Check if permission already exists
                    const [existingPermissions] = await sequelize.query(`
                        SELECT id, permission FROM user_permissions 
                        WHERE "userId" = $1 AND "collectionId" = $2
                    `, {
                        bind: [userId, collectionId],
                        type: sequelize.QueryTypes.SELECT
                    });
                    
                    if (existingPermissions.length > 0) {
                        // Update existing permission to read_write if it's not already
                        const existingPermission = existingPermissions[0];
                        if (existingPermission.permission !== 'read_write') {
                            await sequelize.query(`
                                UPDATE user_permissions 
                                SET permission = $1, "updatedAt" = $2 
                                WHERE id = $3
                            `, {
                                bind: ['read_write', now, existingPermission.id],
                                type: sequelize.QueryTypes.UPDATE
                            });
                            permissionsUpdated++;
                        }
                    } else {
                        // Create new permission record
                        const permissionId = uuidv4();
                        
                        await sequelize.query(`
                            INSERT INTO user_permissions (id, "userId", "collectionId", permission, "createdAt", "updatedAt", "createdById") 
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                        `, {
                            bind: [
                                permissionId,
                                userId,
                                collectionId,
                                'read_write',  // Permission level
                                now,           // createdAt
                                now,           // updatedAt
                                userId         // createdById - use the user themselves as creator
                            ],
                            type: sequelize.QueryTypes.INSERT
                        });
                        
                        permissionsCreated++;
                    }
                    
                } catch (error) {
                    verbose && warn(`Failed to process permission for user ${userId}, collection ${collectionId}: ${error.message}`);
                    continue;
                }
            }
        }
        
        log(`✅ Permission setup complete: ${permissionsCreated} created, ${permissionsUpdated} updated`);
        
    } catch (error) {
        warn(`Failed to grant permissions: ${error.message}`);
        // Don't throw - this is a bonus feature, not critical
    }
}

importData(); 
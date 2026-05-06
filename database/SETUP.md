# PostgreSQL Database Setup Guide

## Installation Steps

### 1. Install PostgreSQL

- **Windows**: Download from https://www.postgresql.org/download/windows/
  - Run the installer
  - Set a password for the `postgres` user (remember this!)
  - Accept default settings (port 5432)

- **macOS**:

  ```bash
  brew install postgresql
  brew services start postgresql
  ```

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install postgresql postgresql-contrib
  ```

### 2. Initialize Database Using SQL Files

Run the SQL scripts in order:

```bash
# Connect as postgres superuser
psql -U postgres

# Run setup scripts in order
\i database/01_create_database.sql
\i database/02_create_tables.sql
\i database/03_create_user.sql
```

Or use the command line:

```bash
# Windows (from PowerShell)
psql -U postgres -f database\01_create_database.sql
psql -U postgres -f database\02_create_tables.sql
psql -U postgres -f database\03_create_user.sql

# macOS/Linux
psql -U postgres -f database/01_create_database.sql
psql -U postgres -f database/02_create_tables.sql
psql -U postgres -f database/03_create_user.sql
```

### 3. Configure Connection

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your PostgreSQL credentials:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/signup_db
   SECRET_KEY=your-secret-key-change-in-production
   ```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

## Database Files

- `01_create_database.sql` - Creates the database and enables UUID extension
- `02_create_tables.sql` - Creates tables with proper schema and indexes
- `03_create_user.sql` - Creates database user and grants permissions

## Verify Setup

To verify the database is set up correctly:

```bash
# Connect to PostgreSQL
psql -U user -d signup_db -h localhost

# List tables
\dt

# Query users table
SELECT * FROM users;

# Exit
\q
```

## Troubleshooting

- **Connection refused**: Ensure PostgreSQL service is running
- **Authentication failed**: Check username and password in .env
- **Database does not exist**: Run the CREATE DATABASE command above
- **Permission denied**: Run the GRANT commands above
- **UUID extension not found**: Ensure PostgreSQL 13+ is installed

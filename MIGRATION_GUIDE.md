# Migration Guide

This guide explains how to run the database migration to create the `events` table.

## Method 1: Using Supabase SQL Editor (Recommended - Easiest)

1. **Go to your Supabase Dashboard**
   - Navigate to https://app.supabase.com
   - Select your project

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy and paste the migration script**
   - Open `migrations/create_events_table.sql`
   - Copy all the contents
   - Paste into the SQL Editor

4. **Run the query**
   - Click "Run" or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)
   - You should see a success message

5. **Verify the table was created**
   - Go to "Table Editor" in the left sidebar
   - You should see the `events` table listed

## Method 2: Using psql Command Line

1. **Get your connection string**
   - Go to Supabase Dashboard > Settings > Database
   - Copy the "Connection string" (URI format)
   - It should look like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

2. **Run the migration**
   ```bash
   psql "your_connection_string_here" -f migrations/create_events_table.sql
   ```

   Example:
   ```bash
   psql "postgresql://postgres:mypassword@db.abcdefgh.supabase.co:5432/postgres" -f migrations/create_events_table.sql
   ```

3. **If psql is not installed:**
   - **macOS**: `brew install postgresql`
   - **Ubuntu/Debian**: `sudo apt-get install postgresql-client`
   - **Windows**: Download from https://www.postgresql.org/download/windows/

## Method 3: Using Python Script (Alternative)

You can also create a simple Python script to run the migration:

```python
# run_migration.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def run_migration():
    # Read the migration file
    with open('migrations/create_events_table.sql', 'r') as f:
        sql = f.read()
    
    # Create engine
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(database_url)
    
    # Execute migration
    async with engine.begin() as conn:
        await conn.execute(sql)
    
    print("Migration completed successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
```

Then run:
```bash
python run_migration.py
```

## Method 4: Using Supabase CLI (If you have it installed)

```bash
supabase db push
```

Or if you want to run a specific SQL file:
```bash
supabase db execute -f migrations/create_events_table.sql
```

## Troubleshooting

### Error: "relation 'events' already exists"
- The table already exists. You can either:
  - Drop it first: `DROP TABLE IF EXISTS events CASCADE;`
  - Or skip the migration if the table structure is correct

### Error: "permission denied"
- Make sure you're using the correct connection string with proper credentials
- For Supabase, use the connection string from Settings > Database

### Error: "could not connect to server"
- Check your connection string
- Verify your Supabase project is active
- Check if your IP is allowed (if using connection pooling)

## Verifying the Migration

After running the migration, verify the table was created:

**Using Supabase Dashboard:**
- Go to Table Editor
- Look for the `events` table
- Check that it has the correct columns: `id`, `name`, `description`, `date`, `photo_url`, `meeting_link`, `created_at`, `updated_at`

**Using SQL:**
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'events';
```

## Next Steps

After running the migration:
1. Create the `events` bucket in Supabase Storage (Dashboard > Storage)
2. Set the bucket to Public if you want public access to photos
3. Start your FastAPI server and test the endpoints!


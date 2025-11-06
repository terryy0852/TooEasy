# Supabase Setup Guide for Assignment Management System

This guide will help you migrate from Render's PostgreSQL to Supabase for persistent database storage.

## Why Switch to Supabase?

- **Persistent Storage**: Supabase free tier doesn't delete your database after 90 days of inactivity
- **Better Free Tier**: 500MB database storage, unlimited projects
- **Real-time Features**: Optional real-time subscriptions for future enhancements
- **Better Developer Experience**: Web-based dashboard, easy management

## Step 1: Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub, Google, or email
4. Verify your email address

## Step 2: Create New Project

1. Click "New Project"
2. Fill in project details:
   - **Organization**: (Create new or use existing)
   - **Name**: `too-easy-assignment-system`
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., `US East`)
   - **Pricing Plan**: **Free**
3. Click "Create new project"

## Step 3: Get Connection String

After project creation:

1. Go to **Settings → Database**
2. Find **Connection Info** section
3. Copy the **Connection string** (URI format)
   - It will look like: `postgresql://postgres:[YOUR-PASSWORD]@db.[project-ref].supabase.co:5432/postgres`

## Step 4: Update Render Configuration

1. Edit `render.yaml`:
   - Replace `your-supabase-connection-string-here` with your actual Supabase URI
   - Remove the `databases` section (no longer needed)

2. Example of updated `render.yaml`:
```yaml
envVars:
  - key: SECRET_KEY
    generateValue: true
  - key: DATABASE_URL
    value: "postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres"
  - key: UPLOAD_FOLDER
    value: /opt/render/project/src/uploads
```

## Step 5: Deploy to Render

1. Push changes to GitHub:
```bash
git add render.yaml
git commit -m "Switch to Supabase database"
git push origin main
```

2. Render will automatically deploy with new environment variables

## Step 6: Migrate Existing Data (Optional)

If you have existing data in Render's PostgreSQL:

1. Get your Render database connection string:
   - In Render dashboard, go to your database → Connection → External Connection
   - Copy the PostgreSQL connection string

2. Run migration script:
```powershell
# Set environment variables
$env:RENDER_DATABASE_URL = "your-render-db-connection-string"
$env:SUPABASE_DATABASE_URL = "your-supabase-connection-string"

# Run migration
python migrate_to_supabase.py
```

## Step 7: Verify Setup

1. Check your application is running on Render
2. Login and create a test assignment
3. Verify data is being stored in Supabase:
   - Go to Supabase dashboard → Table Editor
   - You should see data in `user`, `assignment`, `submission` tables

## Troubleshooting

### Connection Issues
- Verify your Supabase connection string is correct
- Check that your Supabase project is running
- Ensure database password is correctly encoded in URI

### Migration Issues
- Make sure both databases are accessible
- Check that tables exist in both databases
- Run migration script with debug output if needed

### Performance Issues
- Supabase free tier has some limitations
- Consider upgrading to Pro ($25/month) for production workloads

## Security Notes

1. **Never commit real database URLs** to version control
2. Use environment variables for all sensitive data
3. Supabase provides free SSL connections
4. Consider setting up row-level security in the future

## Next Steps

1. **Database Backups**: Set up automatic backups in Supabase
2. **Monitoring**: Use Supabase logs and metrics
3. **Scaling**: Upgrade plan when needed
4. **Real-time**: Add real-time features for live updates

## Support

- Supabase Documentation: https://supabase.com/docs
- Render Documentation: https://render.com/docs
- GitHub Issues: Create issues in your repository for help

---

**Note**: This migration will solve the assignment disappearance issue caused by Render's 90-day database deletion policy for free tier users.
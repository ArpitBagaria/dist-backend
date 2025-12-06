# DEPLOYMENT INSTRUCTIONS
## For: C:\Users\dhana\OneDrive\Desktop\dist-backend

---

## 📋 STEP-BY-STEP DEPLOYMENT:

### Step 1: Copy Fixed Files
Copy all the downloaded fixed files to replace the existing files in:
```
C:\Users\dhana\OneDrive\Desktop\dist-backend\
```

**Files to replace:**
- main.py (FIXED)
- models.py (FIXED)
- prm_importer.py (IMPROVED)
- .env (check configuration)

**New file to add:**
- tally_cache.py (NEW - REQUIRED!)

**Files to keep as-is:**
- database.py
- schemas.py
- tally_client.py
- requirements.txt
- start_server.bat
- dist_backend.db (your database)
- prm_imei_sample.xlsx (your data file)

---

### Step 2: Verify Directory Structure
Your folder should now contain:

```
C:\Users\dhana\OneDrive\Desktop\dist-backend\
├── .env
├── .venv\                    (your virtual environment)
├── database.py
├── dist_backend.db           (your database)
├── main.py                   ⭐ FIXED
├── models.py                 ⭐ FIXED
├── prm_imei_sample.xlsx      (your data)
├── prm_importer.py           ⭐ IMPROVED
├── requirements.txt
├── schemas.py
├── start_server.bat
├── tally_cache.py            ⭐ NEW - MUST ADD!
├── tally_client.py
├── FIXES_SUMMARY.md          (documentation)
└── QUICK_START.md            (documentation)
```

---

### Step 3: Activate Virtual Environment
Open Command Prompt in the dist-backend folder:

```cmd
cd C:\Users\dhana\OneDrive\Desktop\dist-backend
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the beginning of your command prompt.

---

### Step 4: Install/Update Dependencies
```cmd
pip install -r requirements.txt
```

This ensures all required packages are installed.

---

### Step 5: Verify .env Configuration
Open `.env` file and verify:

```
DATABASE_URL=sqlite:///./dist_backend.db
TALLY_HOST=http://192.168.31.65:9000
```

**Important:** Make sure the Tally IP address is correct for your network!

---

### Step 6: Test Database Connection
```cmd
python -c "from database import init_db; init_db()"
```

You should see: "Database tables created"

---

### Step 7: Start the Server

**Option A - Using Batch File:**
```cmd
start_server.bat
```

**Option B - Direct Command:**
```cmd
uvicorn main:app --reload --port 8000
```

You should see:
```
============================================================
Distribution Backend Service - Phase 1.5
============================================================
Database tables created
Application ready!
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### Step 8: Test the Fixed Code

Open a new Command Prompt (keep server running) and test:

**1. Health Check:**
```cmd
curl http://localhost:8000/health
```
Expected: `{"status":"ok","timestamp":"..."}`

**2. API Root:**
```cmd
curl http://localhost:8000/
```
Expected: `{"message":"Distribution Backend API - Phase 1.5","version":"1.5.0","status":"running"}`

**3. Test PRM Sync:**
```cmd
curl -X POST http://localhost:8000/run/prm-sync
```
Expected: Success message with import statistics

**4. Check Sync Logs (NEW endpoint):**
```cmd
curl http://localhost:8000/debug/sync-logs
```

**5. Check Cache Status:**
```cmd
curl http://localhost:8000/debug/tally-cache
```

---

### Step 9: Test in Browser
Open your browser and navigate to:

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Debug Logs:** http://localhost:8000/debug/sync-logs

---

## 🔧 TROUBLESHOOTING:

### Issue: "ModuleNotFoundError: No module named 'tally_cache'"
**Solution:** Make sure you copied the NEW `tally_cache.py` file to the directory!

### Issue: "Port 8000 already in use"
**Solution:** 
```cmd
# Stop existing process or use different port:
uvicorn main:app --reload --port 8001
```

### Issue: "Cannot connect to Tally"
**Solution:** 
1. Verify Tally is running
2. Check Tally port: http://192.168.31.65:9000
3. Update `.env` file if IP/port is different

### Issue: "Excel file not found"
**Solution:** Make sure `prm_imei_sample.xlsx` is in the same folder as main.py

### Issue: Database errors after update
**Solution:** 
```cmd
# Backup old database
copy dist_backend.db dist_backend.db.backup

# Delete and recreate
del dist_backend.db
python -c "from database import init_db; init_db()"

# Run sync to repopulate
curl -X POST http://localhost:8000/run/prm-sync
```

---

## ✅ VERIFICATION CHECKLIST:

Before using in production, verify:

- [ ] All files copied to C:\Users\dhana\OneDrive\Desktop\dist-backend\
- [ ] tally_cache.py exists in the folder (NEW file!)
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file configured correctly
- [ ] Server starts without errors
- [ ] Health check returns OK
- [ ] PRM sync works
- [ ] Tally integration works (if Tally is running)
- [ ] Can access API docs at /docs

---

## 🎯 WHAT'S FIXED:

1. ✅ Missing tally_cache.py created
2. ✅ Duplicate app initialization fixed
3. ✅ CORS middleware working
4. ✅ Product-PriceHistory relationship fixed
5. ✅ Better error handling
6. ✅ Excel import validation improved
7. ✅ New debug endpoints added

---

## 📞 IF YOU NEED HELP:

1. Check console output for error messages
2. Review FIXES_SUMMARY.md for detailed documentation
3. Check debug endpoints:
   - /debug/sync-logs
   - /debug/tally-cache
   - /debug/price-history

---

## 🚀 NEXT STEPS:

Once verified working:
1. Test all API endpoints thoroughly
2. Run PRM sync with your actual data
3. Test Tally integration
4. Generate negative report
5. Update product prices

---

**Current Status:** ✅ All fixes applied, ready to deploy!
**Location:** C:\Users\dhana\OneDrive\Desktop\dist-backend\
**Version:** 1.5.0

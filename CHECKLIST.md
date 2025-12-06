# 📝 QUICK CHECKLIST FOR DEPLOYMENT

## ✅ Files to Copy to: C:\Users\dhana\OneDrive\Desktop\dist-backend\

### 🔴 CRITICAL - Must Replace These:
- [ ] main.py (FIXED - duplicate app init)
- [ ] models.py (FIXED - missing relationship)
- [ ] prm_importer.py (IMPROVED - validation)

### 🆕 CRITICAL - Must Add This NEW File:
- [ ] tally_cache.py (NEW - previously missing!)

### ✅ Already in Your Folder (Keep as-is):
- [x] database.py
- [x] schemas.py
- [x] tally_client.py
- [x] requirements.txt
- [x] start_server.bat
- [x] dist_backend.db (your database)
- [x] prm_imei_sample.xlsx (your data)
- [x] .venv\ (your virtual environment)

### 📚 Documentation (Optional):
- [ ] FIXES_SUMMARY.md
- [ ] QUICK_START.md
- [ ] DEPLOYMENT_GUIDE.md
- [ ] CHECKLIST.md (this file)

---

## 🚀 DEPLOYMENT STEPS:

1. [ ] Copy all fixed files to dist-backend folder
2. [ ] Open Command Prompt in that folder
3. [ ] Run: `.venv\Scripts\activate.bat`
4. [ ] Run: `pip install -r requirements.txt`
5. [ ] Run: `start_server.bat` or `uvicorn main:app --reload --port 8000`
6. [ ] Open browser: http://localhost:8000/docs
7. [ ] Test: http://localhost:8000/health
8. [ ] Test PRM sync: http://localhost:8000/docs (click POST /run/prm-sync)

---

## 🧪 QUICK TESTS:

```cmd
# In a NEW Command Prompt (keep server running):

# Test 1: Health check
curl http://localhost:8000/health

# Test 2: API info
curl http://localhost:8000/

# Test 3: PRM sync
curl -X POST http://localhost:8000/run/prm-sync

# Test 4: Sync logs (NEW!)
curl http://localhost:8000/debug/sync-logs
```

---

## ⚠️ MOST IMPORTANT:

**Don't forget to add `tally_cache.py` - it's a NEW file that was missing!**

Without this file, you'll get:
```
ModuleNotFoundError: No module named 'tally_cache'
```

---

## 📍 YOUR SETUP:

**Location:** C:\Users\dhana\OneDrive\Desktop\dist-backend\
**Python:** Should have .venv folder
**Database:** dist_backend.db
**Server:** http://localhost:8000

---

**Status:** Ready to deploy! ✅

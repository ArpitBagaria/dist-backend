# 🚀 GITHUB SETUP & PUSH GUIDE

This guide will help you push your Distribution Backend project to GitHub.

---

## 📋 PREREQUISITES

Before starting, make sure you have:
- [ ] A GitHub account (create one at https://github.com/signup)
- [ ] Git installed on your computer
- [ ] All project files in: `C:\Users\dhana\OneDrive\Desktop\dist-backend\`

---

## 🔧 STEP 1: Install Git (if not already installed)

### Check if Git is installed:
```cmd
git --version
```

If you see a version number, Git is installed. Skip to Step 2.

### If Git is not installed:
1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart Command Prompt
4. Verify: `git --version`

---

## 🌐 STEP 2: Create GitHub Repository

1. **Go to GitHub**: https://github.com
2. **Sign in** to your account
3. **Click** the "+" icon in top-right corner
4. **Select** "New repository"
5. **Fill in details**:
   - Repository name: `dist-backend` (or any name you prefer)
   - Description: "Distribution Backend API with Tally Integration"
   - Visibility: Choose "Public" or "Private"
   - ❌ **DO NOT** check "Initialize with README" (we already have one)
6. **Click** "Create repository"

**Keep this page open** - you'll need the repository URL!

---

## 💻 STEP 3: Initialize Git in Your Project

Open Command Prompt in your project folder:

```cmd
cd C:\Users\dhana\OneDrive\Desktop\dist-backend
```

### Configure Git (first time only):
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Initialize Git repository:
```cmd
git init
```

---

## 📝 STEP 4: Prepare Files for GitHub

### Copy the new files from downloads to your folder:

Make sure these files are in `C:\Users\dhana\OneDrive\Desktop\dist-backend\`:

**New/Updated Files:**
- [ ] `.gitignore` (NEW)
- [ ] `README.md` (NEW)
- [ ] `LICENSE` (NEW)
- [ ] `.env.example` (NEW)
- [ ] All the fixed Python files

### Verify .gitignore is working:
```cmd
# This should NOT show .env or .db files:
git status
```

---

## 📦 STEP 5: Add Files to Git

### Add all files:
```cmd
git add .
```

### Check what will be committed:
```cmd
git status
```

You should see:
- ✅ Python files (.py)
- ✅ Documentation (.md)
- ✅ Configuration (.gitignore, LICENSE, requirements.txt)
- ✅ .env.example
- ❌ NOT .env (sensitive data)
- ❌ NOT .db files (database)
- ❌ NOT .venv (virtual environment)
- ❌ NOT .xlsx files (data)

---

## 💾 STEP 6: Commit Files

```cmd
git commit -m "Initial commit: Distribution Backend API v1.5.0"
```

---

## 🔗 STEP 7: Connect to GitHub

**Replace `YOUR_USERNAME` and `REPO_NAME` with your actual values:**

```cmd
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

**Example:**
```cmd
git remote add origin https://github.com/johndoe/dist-backend.git
```

### Verify the remote:
```cmd
git remote -v
```

---

## 🚀 STEP 8: Push to GitHub

### For the first push:
```cmd
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password!)

### Creating a Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "dist-backend"
4. Select scopes: Check "repo"
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when Git asks

---

## ✅ STEP 9: Verify Upload

1. Go to your GitHub repository page
2. You should see all your files!
3. Check that README.md is displaying properly
4. Verify .env is NOT uploaded (check .gitignore worked)

---

## 🔄 FUTURE UPDATES

After making changes to your code, push updates:

```cmd
# 1. Add changed files
git add .

# 2. Commit with a message
git commit -m "Description of changes"

# 3. Push to GitHub
git push
```

---

## 📝 COMMON COMMANDS

```cmd
# Check status
git status

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes
git pull

# View differences
git diff
```

---

## 🔒 SECURITY CHECKLIST

Before pushing, verify:

- [ ] `.env` file is in `.gitignore` (contains sensitive data)
- [ ] `.db` files are in `.gitignore` (contains data)
- [ ] `.venv` is in `.gitignore` (large, unnecessary)
- [ ] `.env.example` is included (safe template)
- [ ] No API keys or passwords in code
- [ ] `TALLY_HOST` in code is a placeholder or example

---

## 🛠️ TROUBLESHOOTING

### Error: "remote origin already exists"
```cmd
# Remove existing remote and re-add:
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Error: "Updates were rejected"
```cmd
# Pull first, then push:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Error: "Permission denied"
- Make sure you're using a Personal Access Token, not your password
- Check the token has "repo" permissions

### Want to undo last commit (before push):
```cmd
git reset --soft HEAD~1
```

---

## 📖 ADDITIONAL GITHUB FEATURES

### Add a Description:
1. Go to your repository on GitHub
2. Click the ⚙️ icon next to "About"
3. Add description and topics

### Add Topics:
Suggested topics:
- `fastapi`
- `python`
- `tally-integration`
- `inventory-management`
- `distribution-backend`
- `rest-api`

### Enable GitHub Pages (optional):
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main / docs
4. Your docs will be at: `https://yourusername.github.io/dist-backend/`

---

## 🎯 COMPLETE CHECKLIST

- [ ] Git installed
- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Git configured (name and email)
- [ ] Project folder initialized with git
- [ ] .gitignore file added
- [ ] README.md file added
- [ ] LICENSE file added
- [ ] .env.example file added
- [ ] All files committed
- [ ] Remote origin configured
- [ ] Code pushed to GitHub
- [ ] Repository visible on GitHub
- [ ] .env NOT visible on GitHub (security check)
- [ ] README.md displaying properly

---

## 🔗 USEFUL LINKS

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub Desktop** (GUI alternative): https://desktop.github.com/

---

## 🎉 SUCCESS!

Once pushed, your repository will be at:
```
https://github.com/YOUR_USERNAME/dist-backend
```

Share this link with team members or add it to your portfolio!

---

**Questions?** Open an issue on GitHub or check the documentation!

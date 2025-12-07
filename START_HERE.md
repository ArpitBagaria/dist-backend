# How to Start the Application

This guide will help you run both the backend and frontend together.

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- SQLite (included with Python)

## Step 1: Start the Backend API

Open a terminal and run:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

The backend API will start at `http://localhost:8000`

You can test it by visiting: http://localhost:8000/health

## Step 2: Start the Frontend

Open a **NEW terminal** (keep the backend running) and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the frontend
npm run dev
```

The frontend will start at `http://localhost:3000`

## Step 3: Access the Application

Open your browser and go to: **http://localhost:3000**

You'll see the Distribution Management System dashboard.

## Available Features

1. **Dashboard** - View system overview and top OD retailers
2. **Orders** - Test order approval with the auto-approval engine
3. **Retailers** - Browse all retailers in the system
4. **Reports** - Generate negative/OD reports
5. **Sync** - Run PRM data synchronization

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all Python dependencies are installed

### Frontend won't start
- Make sure port 3000 is not in use
- Run `npm install` in the frontend directory
- Check that Node.js is installed: `node --version`

### Frontend can't connect to backend
- Make sure the backend is running on port 8000
- Check the browser console for errors
- Verify the backend is accessible at http://localhost:8000/health

## Need Help?

Check the main README.md for more detailed documentation about the system architecture and API endpoints.

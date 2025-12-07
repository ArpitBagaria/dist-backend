# Distribution Management Frontend

Modern web interface for the Distribution Management System.

## Quick Start

```bash
npm install
npm run dev
```

The frontend will start on `http://localhost:3000`

## Features

- **Dashboard**: View key metrics and top OD retailers
- **Orders**: Check order approval status with auto-approval engine
- **Retailers**: Browse and search all retailers
- **Reports**: Generate negative/OD reports
- **Sync**: Run PRM data synchronization

## Backend Connection

The frontend connects to the backend API at `http://localhost:8000` via proxy.

Make sure the backend is running before starting the frontend:

```bash
cd ..
pip install -r requirements.txt
uvicorn main:app --reload
```

## Technology Stack

- React 18
- TypeScript
- Vite
- React Router
- Recharts (for future charts)

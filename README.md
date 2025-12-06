# Distribution Backend API

A FastAPI-based backend system for managing distribution operations, inventory tracking, retailer management, and Tally ERP integration.

![Version](https://img.shields.io/badge/version-1.5.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-teal)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🚀 Features

- **PRM IMEI Import**: Automated import from Excel files with validation
- **Inventory Management**: Real-time inventory snapshot tracking
- **Retailer Management**: Complete retailer database with activation tracking
- **Tally ERP Integration**: Seamless integration with Tally for ledger balances
- **Smart Caching**: 2-hour cache TTL to minimize Tally API calls
- **Price Management**: Product pricing with complete change history
- **Negative/OD Reports**: Automated calculation of outstanding amounts
- **RESTful API**: Full REST API with automatic documentation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Tally ERP 9 (for Tally integration)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dist-backend.git
   cd dist-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=sqlite:///./dist_backend.db
   TALLY_HOST=http://192.168.31.65:9000
   ```

5. **Initialize database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

## 🚀 Quick Start

### Start the Server

**Option 1: Using uvicorn directly**
```bash
uvicorn main:app --reload --port 8000
```

**Option 2: Using the batch file (Windows)**
```bash
start_server.bat
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/run/prm-sync` | Run PRM IMEI import |
| POST | `/admin/products/prices` | Update product prices |
| GET | `/tally/closing-balance` | Get Tally ledger balance |
| GET | `/reports/negative` | Generate OD report |

### Debug Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/debug/price-history` | View price change history |
| GET | `/debug/tally-cache` | View Tally cache status |
| GET | `/debug/sync-logs` | View PRM sync run logs |

### Example Requests

**Run PRM Sync:**
```bash
curl -X POST http://localhost:8000/run/prm-sync
```

**Update Product Prices:**
```bash
curl -X POST http://localhost:8000/admin/products/prices \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {
        "goods_id": "PROD001",
        "name": "Product Name",
        "category": "Phones",
        "price": 15999.00
      }
    ]
  }'
```

**Get Tally Balance:**
```bash
curl "http://localhost:8000/tally/closing-balance?ledger=RETAILER001"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./dist_backend.db` |
| `TALLY_HOST` | Tally ERP server URL | `http://192.168.31.65:9000` |

### Cache Settings

- **Cache TTL**: 120 minutes (2 hours)
- **Location**: `tally_cache.py`
- Can be modified in `CACHE_TTL_MINUTES` constant

## 🗄️ Database Schema

### Main Tables

- **retailers**: Retailer information and contact details
- **products**: Product catalog with pricing
- **prm_inventory_snapshot**: Current inventory levels per retailer
- **activations**: Device activation records
- **price_history**: Complete price change audit trail
- **tally_ledger_cache**: Cached Tally balance data
- **prm_sync_run_log**: PRM import run history

### Relationships

```
Retailer 1---* PrmInventorySnapshot
Retailer 1---* Activation
Retailer 1---* TallyLedgerCache
Product 1---* PrmInventorySnapshot
Product 1---* Activation
Product 1---* PriceHistory
```

## 📚 Documentation

Detailed documentation available in the repository:

- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Complete list of fixes and improvements
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[CHECKLIST.md](CHECKLIST.md)** - Deployment checklist

## 🔍 Features in Detail

### PRM IMEI Import

- Automated Excel file parsing
- Retailer and product upsert logic
- Inventory snapshot generation
- Activation tracking
- Progress indicators and error logging

### Smart Caching System

- 2-hour cache TTL for Tally balances
- Automatic cache refresh
- Fallback to stale cache if Tally unavailable
- Cache hit/miss logging

### Price Management

- Bulk price updates
- Complete price change history
- Source tracking (admin_api, prm_sync, etc.)
- Timestamp tracking

### OD Report Generation

- Calculates closing balance vs stock value
- Identifies retailers with outstanding amounts
- Sorted by OD amount (highest first)
- Real-time data from Tally

## 🛠️ Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError: No module named 'tally_cache'**
```bash
# Solution: Make sure tally_cache.py exists in the project directory
ls -la tally_cache.py
```

**Issue: Cannot connect to Tally**
```bash
# Solution 1: Verify Tally is running
curl http://192.168.31.65:9000

# Solution 2: Update .env with correct Tally IP
# Edit .env and change TALLY_HOST
```

**Issue: Excel file not found**
```bash
# Solution: Place prm_imei_sample.xlsx in the project root
# Or update the path in the sync endpoint
```

**Issue: Database locked**
```bash
# Solution: Close all connections and restart server
# Delete dist_backend.db and reinitialize if needed
python -c "from database import init_db; init_db()"
```

## 🔒 Security Notes

**For Production Deployment:**

1. ✅ Add API authentication (API keys or OAuth)
2. ✅ Implement rate limiting
3. ✅ Use specific CORS origins (not `*`)
4. ✅ Enable HTTPS/TLS
5. ✅ Add request logging and audit trails
6. ✅ Implement role-based access control
7. ✅ Sanitize all inputs
8. ✅ Use environment variables for secrets

## 📊 Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: SQLAlchemy 2.0.25 with SQLite
- **Server**: Uvicorn 0.27.0
- **Data Processing**: Pandas 2.1.4
- **Excel**: OpenPyXL 3.1.2
- **Validation**: Pydantic 2.5.3
- **HTTP Client**: Requests 2.31.0

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM
- The Python community

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Version**: 1.5.0  
**Status**: ✅ Production Ready (with security enhancements)  
**Last Updated**: December 2024

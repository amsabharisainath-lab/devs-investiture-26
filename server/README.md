# DEVS Investiture - Backend API

A modern FastAPI-based backend for the DEVS Investiture platform.

## Features

- 🚀 **FastAPI** - High-performance async web framework
- 📝 **Pydantic V2** - Data validation and settings management
- 📦 **Redis** - Caching and session management
- ⚡ **Celery** - Asynchronous task processing
- 📊 **Auto-generated API Docs** - Interactive Swagger/ReDoc documentation
- 🛡️ **Security Best Practices** - Password hashing, CORS, rate limiting
- 📝 **Structured Logging** - JSON and text format logging
- 🎯 **Error Handling** - Global exception handling middleware
- ✅ **Type Hints** - Full type annotation coverage

## Project Structure

```
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Authentication endpoints
│   │       │   ├── health.py        # Health check endpoints
│   │       │   └── users.py         # User management endpoints
│   │       └── api.py               # API router configuration
│   ├── core/
│   │   ├── config.py                # Application settings
│   │   ├── logging.py               # Logging configuration
│   │   └── security.py              # Security utilities (JWT, password hashing)
│   ├── db/
│   │   └── session.py               # Database session management
│   ├── middleware/
│   │   ├── error_handler.py         # Global error handling
│   │   └── request_logger.py        # Request logging
│   ├── models/                      # Beanie document models
│   ├── schemas/                     # Pydantic schemas
│   │   ├── auth.py                  # Authentication schemas
│   │   └── user.py                  # User schemas
│   └── services/                    # Business logic layer
├── migrations/                      # Database migrations (if needed)
├── logs/                            # Application logs
├── tests/                           # Test files
├── main.py                          # Application entry point
├── pyproject.toml                   # Python dependencies and project config
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Redis (optional, for caching and Celery)

## Installation

### 1. Clone the repository

```bash
cd server
```

### 2. Install uv (if not already installed)

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Install dependencies

```bash
uv sync
```

This will automatically create a virtual environment and install all dependencies from `pyproject.toml`.

### 4. Set up environment variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update the following key variables:

```env
# Database
DATABASE_URI=mongodb://admin:admin@localhost:27017/db?authSource=admin

# Security (IMPORTANT: Change in production!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Run the application

**Development mode (with auto-reload):**

```bash
uv run main.py
```

Or using uvicorn directly:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Code Formatting

```bash
# Format code with black
uv run black app/

# Sort imports
uv run isort app/

# Lint with flake8
uv run flake8 app/
```

### Database Migrations

**Database Operations:**
Use alembic.

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the project repository.

---

**Built with ❤️ using FastAPI**

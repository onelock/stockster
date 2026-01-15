# Stockster REST API

FastAPI service providing REST endpoints to access Swedish stock market data from PostgreSQL.

## Endpoints

### Health & Info
- `GET /` - API info and available endpoints
- `GET /health` - Health check

### Stock Data
- `GET /stocks` - Get all stocks with latest trading data
  - Query params: `limit` (default: 100), `offset` (default: 0)
- `GET /stocks/latest?limit=50` - Get latest snapshot of all stocks
- `GET /stocks/{name}?days=7` - Get specific stock data over time
- `GET /stocks/{name}/historical?days=30` - Get historical comparison data
- `GET /stocks/{name}/metrics?days=30` - Get key metrics/ratios

### Search & Stats
- `GET /search?q=volvo` - Search stocks by name
- `GET /stats` - Get database statistics

## Example Usage

```bash
# Get API info
curl http://YOUR_API_URL/

# Get latest stocks
curl http://YOUR_API_URL/stocks/latest?limit=10

# Get specific stock (7 days)
curl http://YOUR_API_URL/stocks/Volvo%20B?days=7

# Search stocks
curl http://YOUR_API_URL/search?q=volvo

# Get stats
curl http://YOUR_API_URL/stats
```

## Response Format

All endpoints return JSON with consistent structure:

```json
{
  "name": "Stock Name",
  "count": 10,
  "data": [
    {
      "name": "Volvo B",
      "last_price": 245.50,
      "change_pct": 1.5,
      "timestamp": "2026-01-15T12:00:00",
      ...
    }
  ]
}
```

## Local Development

```bash
# Install dependencies
pip install fastapi uvicorn psycopg2-binary

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=stockster
export POSTGRES_USER=stockster
export POSTGRES_PASSWORD=your_password

# Run locally
uvicorn api.main:app --reload --port 8000

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Docker

```bash
# Build
docker build -f Dockerfile.api -t stockster-api .

# Run
docker run -p 8000:8000 \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PASSWORD=your_password \
  stockster-api
```

## Kubernetes Deployment

The API is deployed as part of the main stockster stack:

```bash
kubectl apply -k k8s/
```

Access via LoadBalancer service:
```bash
kubectl get svc stockster-api -n stockster
```

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://YOUR_API_URL/docs`
- ReDoc: `http://YOUR_API_URL/redoc`

## CORS

CORS is enabled for all origins by default. Update in `api/main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    ...
)
```

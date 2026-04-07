# Dhaka Bus Route Finder API

🚌 A FastAPI application for searching direct and transfer bus routes across Dhaka city. Find routes, fare estimates, and transfer points in real-time.

**Live Demo:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **Direct Routes**: Find single-bus routes between any two stops
- **Transfer Routes**: Identify routes with one transfer point
- **Fuzzy Matching**: Handles misspelled stop names with 70%+ accuracy
- **Fare Calculation**: Automatic fare estimation based on distance
- **Stop Suggestions**: Autocomplete suggestions for bus stops
- **CORS Enabled**: Use the API from any frontend application
- **Beautiful UI**: Dark-themed web interface for route search
- **RESTful API**: JSON API for programmatic access

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd dhaka-bus-route
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
   or
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the application:**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 📁 Project Structure

```
dhaka-bus-route/
├─ app/
│  ├─ data/
│  │  └─ routes.json              # Bus route data (name, stops, fares)
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ schemas.py               # Pydantic models for API validation
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ route_engine.py           # Core route-finding logic
│  ├─ static/
│  │  └─ .gitkeep                 # Static assets directory
│  ├─ templates/
│  │  ├─ base.html                # Base HTML template
│  │  ├─ index.html               # Home page
│  │  ├─ results.html             # Search results page
│  │  └─ all_routes.html          # All routes directory
│  ├─ __init__.py
│  └─ main.py                     # FastAPI app entry point
├─ main.py                        # Wrapper for backward compatibility
├─ requirements.txt               # Python dependencies
└─ README.md                      # This file
```

---

## 🔌 API Endpoints

### 1. Search Routes (POST)
**Endpoint:** `POST /search`

Search for bus routes between two stops.

**Request Body:**
```json
{
  "from_stop": "Dhaka University",
  "to_stop": "Gulshan"
}
```

**Response:**
```json
{
  "from_stop_matched": "Dhaka University",
  "to_stop_matched": "Gulshan",
  "direct_routes": [
    {
      "bus_name": "Blue Bus 5",
      "intermediate_stops": ["Stop A", "Stop B"],
      "stop_count": 3,
      "estimated_fare": 50
    }
  ],
  "indirect_routes": [],
  "has_results": true,
  "message": "Found direct route(s)"
}
```

---

### 2. Get All Stops (GET)
**Endpoint:** `GET /api/stops`

Retrieve a list of all available bus stops.

**Response:**
```json
{
  "stops": ["Stop 1", "Stop 2", ...]
}
```

---

### 3. Suggest Stops (GET)
**Endpoint:** `GET /api/suggest?query=dhaka`

Get autocomplete suggestions for stop names.

**Query Parameters:**
- `query` (string): Search query for stop names
- `limit` (integer, optional): Maximum suggestions (default: 8)

**Response:**
```json
{
  "suggestions": ["Dhaka University", "Dhaka Medical"]
}
```

---

### 4. Get All Routes (GET)
**Endpoint:** `GET /api/routes`

Retrieve all available bus routes.

**Response:**
```json
{
  "routes": [
    {
      "name": "Blue Bus 1",
      "stops": ["Stop 1", "Stop 2"],
      "base_fare": 30,
      "fare_per_stop": 5
    }
  ],
  "total_routes": 42
}
```

---

### 5. API Search (GET)
**Endpoint:** `GET /api/search?from=stop1&to=stop2`

REST alternative to POST /search endpoint.

**Query Parameters:**
- `from` (string): Starting stop name
- `to` (string): Ending stop name

**Response:** Same as POST /search

---

## 💻 Usage Examples

### JavaScript/Frontend

```javascript
// Search for routes
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    from_stop: 'Dhaka University',
    to_stop: 'Gulshan'
  })
});
const data = await response.json();
console.log(data);

// Get stop suggestions
const suggestions = await fetch(
  'http://localhost:8000/api/suggest?query=dhaka&limit=5'
).then(r => r.json());
console.log(suggestions);
```

### Python/Backend

```python
import requests

# Search routes
result = requests.post(
    'http://localhost:8000/search',
    json={
        'from_stop': 'Dhaka University',
        'to_stop': 'Gulshan'
    }
)
print(result.json())

# Get all stops
stops = requests.get('http://localhost:8000/api/stops').json()
print(stops['stops'])
```

### cURL

```bash
# Search for routes
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"from_stop": "Dhaka University", "to_stop": "Gulshan"}'

# Get stop suggestions
curl http://localhost:8000/api/suggest?query=dhaka&limit=5
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Setup Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dhaka-bus-route.git
   cd dhaka-bus-route
   ```

3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Install dependencies (with dev tools):**
   ```bash
   pip install -r requirements.txt
   ```

### Making Changes

1. **Make your improvements:**
   - Add new features in `app/services/`
   - Add data models in `app/models/schemas.py`
   - Update templates in `app/templates/`

2. **Test your changes:**
   ```bash
   uvicorn main:app --reload
   # Visit http://localhost:8000 and test the UI
   # Use http://localhost:8000/docs for API testing
   ```

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: Description of your changes"
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Link to any related issues
   - Screenshots for UI changes

### Areas for Contribution

- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **Features**: Add new route-finding algorithms or improve UI
- 📚 **Documentation**: Improve README, add code comments
- 🧪 **Testing**: Add unit tests and integration tests
- 🎨 **UI/UX**: Enhance the web interface design
- 📊 **Data**: Improve route data accuracy

### Code Style

- Follow PEP 8 guidelines
- Use type hints in function signatures
- Add docstrings to functions and classes
- Keep functions small and focused

### Reporting Issues

If you find a bug:

1. Check if it's already reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For questions or support:
- Check existing GitHub issues
- Create a new issue for bugs or feature requests
- Feel free to reach out to the maintainers

---

## 🌟 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [RapidFuzz](https://rapidfuzz.github.io/) - Fuzzy string matching
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

---

**Happy routing! 🚌✨**

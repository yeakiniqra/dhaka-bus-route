# Dhaka Bus Route Finder

FastAPI app for searching direct and transfer bus routes in Dhaka.

## Project Structure

```
dhaka-bus-route/
├─ app/
│  ├─ data/
│  │  └─ routes.json
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ schemas.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ route_engine.py
│  ├─ static/
│  │  └─ .gitkeep
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ index.html
│  │  ├─ results.html
│  │  └─ all_routes.html
│  ├─ __init__.py
│  └─ main.py
├─ main.py
├─ requirements.txt
└─ pyproject.toml
```

## Run

Use either command:

```bash
uvicorn app.main:app --reload
```

or:

```bash
uvicorn main:app --reload
```

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

from app.models.schemas import RouteSearchResult, AllRoutesResponse
from app.services.route_engine import RouteEngine

app = FastAPI(
    title="Dhaka Bus Route Finder",
    description="Find bus routes across Dhaka city",
    version="1.0.0",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Load and initialize route engine
routes_path = BASE_DIR / "data" / "routes.json"
with open(routes_path, "r", encoding="utf-8") as f:
    raw_routes = json.load(f)

engine = RouteEngine(raw_routes)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    all_stops = engine.get_all_stops()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "all_stops": all_stops,
            "total_routes": len(engine.routes),
            "total_stops": len(all_stops),
        },
    )

@app.get("/routes", response_class=HTMLResponse)
async def all_routes_page(request: Request):
    all_stops = engine.get_all_stops()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "all_stops": all_stops,
            "total_routes": len(engine.routes),
            "total_stops": len(all_stops),
        },
    )





@app.get("/api/search")
async def api_search(from_stop: str, to_stop: str) -> RouteSearchResult:
    return engine.find_routes(from_stop, to_stop)


@app.get("/api/stops")
async def api_stops() -> list[str]:
    return engine.get_all_stops()


@app.get("/api/routes")
async def api_routes() -> AllRoutesResponse:
    return AllRoutesResponse(routes=engine.routes)





@app.get("/api/suggest")
async def suggest_stops(q: str) -> list[str]:
    return engine.suggest_stops(q)
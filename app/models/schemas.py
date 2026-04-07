from pydantic import BaseModel, field_validator


class BusRoute(BaseModel):
    name: str
    stops: list[str]


class BusStop(BaseModel):
    name: str
    routes: list[str]


class DirectRoute(BaseModel):
    bus_name: str
    from_stop: str
    to_stop: str
    intermediate_stops: list[str]
    stop_count: int


class TransferPoint(BaseModel):
    stop_name: str
    first_bus: str
    second_bus: str


class IndirectRoute(BaseModel):
    transfer_point: str
    first_leg: DirectRoute
    second_leg: DirectRoute
    total_stops: int


class RouteSearchResult(BaseModel):
    from_stop: str
    to_stop: str
    from_stop_matched: str
    to_stop_matched: str
    direct_routes: list[DirectRoute]
    indirect_routes: list[IndirectRoute]
    has_results: bool
    message: str


class AllRoutesResponse(BaseModel):
    routes: list[BusRoute]
    total: int = 0

    def model_post_init(self, __context):
        self.total = len(self.routes)


class RouteSearchRequest(BaseModel):
    from_stop: str
    to_stop: str

    @field_validator("from_stop", "to_stop")
    @classmethod
    def stop_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Stop name cannot be empty")
        return v.strip()
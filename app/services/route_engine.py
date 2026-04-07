from rapidfuzz import process, fuzz
from collections import defaultdict
from app.models.schemas import BusRoute, DirectRoute, IndirectRoute, RouteSearchResult

FUZZY_THRESHOLD = 70

def normalize_stop(name: str) -> str:
    """Lowercase and strip for deduplication matching."""
    return name.lower().strip()


class RouteEngine:
    def __init__(self, raw_routes: list[dict]):
        self.routes: list[BusRoute] = self._process_routes(raw_routes)
        self.stop_index: dict[str, list[str]] = self._build_stop_index()
        self.all_stops_canonical: list[str] = sorted(self.stop_index.keys())
        self._stop_norm_map: dict[str, str] = {
            normalize_stop(s): s for s in self.all_stops_canonical
        }

    def _process_routes(self, raw_routes: list[dict]) -> list[BusRoute]:
        """Process routes: normalize stops, deduplicate, add reverse routes."""
        seen_signatures = set()
        processed = []

        for r in raw_routes:
            route = BusRoute(**r)
            # Normalize stops (remove duplicates within a route)
            seen = set()
            clean_stops = []
            for stop in route.stops:
                norm = normalize_stop(stop)
                if norm not in seen:
                    seen.add(norm)
                    clean_stops.append(stop)
            route.stops = clean_stops

            # Create canonical signature for dedup (sorted stops)
            sig = frozenset(normalize_stop(s) for s in route.stops)
            if sig not in seen_signatures:
                seen_signatures.add(sig)
                processed.append(route)

        return processed

    def _build_stop_index(self) -> dict[str, list[str]]:
        """Build {canonical_stop -> [bus_names]} index. Canonical = first seen."""
        norm_to_canonical: dict[str, str] = {}
        index: dict[str, list[str]] = defaultdict(list)

        for route in self.routes:
            for stop in route.stops:
                norm = normalize_stop(stop)
                if norm not in norm_to_canonical:
                    norm_to_canonical[norm] = stop
                canonical = norm_to_canonical[norm]
                if route.name not in index[canonical]:
                    index[canonical].append(route.name)

        return dict(index)

    def get_all_stops(self) -> list[str]:
        return self.all_stops_canonical

    def suggest_stops(self, query: str, limit: int = 8) -> list[str]:
        if not query or len(query) < 2:
            return []
        results = process.extract(
            query,
            self.all_stops_canonical,
            scorer=fuzz.WRatio,
            limit=limit,
            score_cutoff=50,
        )
        return [r[0] for r in results]

    def _fuzzy_match_stop(self, query: str) -> str | None:
        """Return best matching canonical stop name for a query."""
        result = process.extractOne(
            query,
            self.all_stops_canonical,
            scorer=fuzz.WRatio,
            score_cutoff=FUZZY_THRESHOLD,
        )
        return result[0] if result else None

    def _get_route_by_name(self, name: str) -> BusRoute | None:
        for r in self.routes:
            if r.name == name:
                return r
        return None

    def _stops_in_route(self, route: BusRoute) -> dict[str, int]:
        """Return {normalized_stop: index} for a route."""
        return {normalize_stop(s): i for i, s in enumerate(route.stops)}

    def _find_canonical(self, stop_name: str) -> str | None:
        """Given any stop name variant, find the canonical version."""
        norm = normalize_stop(stop_name)
        return self._stop_norm_map.get(norm)

    def _build_direct_route(
        self,
        route: BusRoute,
        from_canonical: str,
        to_canonical: str,
        from_idx: int,
        to_idx: int,
    ) -> DirectRoute:
        if from_idx <= to_idx:
            segment = route.stops[from_idx : to_idx + 1]
        else:
            segment = route.stops[to_idx : from_idx + 1][::-1]

        stop_count = abs(to_idx - from_idx)

        return DirectRoute(
            bus_name=route.name,
            from_stop=from_canonical,
            to_stop=to_canonical,
            intermediate_stops=segment[1:-1],
            stop_count=stop_count,
        )

    def find_routes(self, from_query: str, to_query: str) -> RouteSearchResult:
        from_matched = self._fuzzy_match_stop(from_query)
        to_matched = self._fuzzy_match_stop(to_query)

        if not from_matched:
            return RouteSearchResult(
                from_stop=from_query,
                to_stop=to_query,
                from_stop_matched=from_query,
                to_stop_matched=to_query or "",
                direct_routes=[],
                indirect_routes=[],
                has_results=False,
                message=f"Could not find any stop matching '{from_query}'. Please check spelling.",
            )

        if not to_matched:
            return RouteSearchResult(
                from_stop=from_query,
                to_stop=to_query,
                from_stop_matched=from_matched,
                to_stop_matched=to_query,
                direct_routes=[],
                indirect_routes=[],
                has_results=False,
                message=f"Could not find any stop matching '{to_query}'. Please check spelling.",
            )

        if normalize_stop(from_matched) == normalize_stop(to_matched):
            return RouteSearchResult(
                from_stop=from_query,
                to_stop=to_query,
                from_stop_matched=from_matched,
                to_stop_matched=to_matched,
                direct_routes=[],
                indirect_routes=[],
                has_results=False,
                message="Source and destination are the same stop!",
            )

        direct_routes = self._find_direct(from_matched, to_matched)
        indirect_routes = []

        if not direct_routes:
            indirect_routes = self._find_indirect(from_matched, to_matched)

        has_results = bool(direct_routes or indirect_routes)
        if direct_routes:
            msg = f"Found {len(direct_routes)} direct route(s) from {from_matched} to {to_matched}."
        elif indirect_routes:
            msg = f"No direct route found. Found {len(indirect_routes)} route(s) with 1 transfer."
        else:
            msg = f"Sorry, no bus routes found between {from_matched} and {to_matched}."

        return RouteSearchResult(
            from_stop=from_query,
            to_stop=to_query,
            from_stop_matched=from_matched,
            to_stop_matched=to_matched,
            direct_routes=direct_routes,
            indirect_routes=indirect_routes,
            has_results=has_results,
            message=msg,
        )

    def _find_direct(self, from_stop: str, to_stop: str) -> list[DirectRoute]:
        from_norm = normalize_stop(from_stop)
        to_norm = normalize_stop(to_stop)
        results = []

        for route in self.routes:
            stop_map = self._stops_in_route(route)
            if from_norm in stop_map and to_norm in stop_map:
                from_idx = stop_map[from_norm]
                to_idx = stop_map[to_norm]
                dr = self._build_direct_route(
                    route, from_stop, to_stop, from_idx, to_idx
                )
                results.append(dr)

        # Sort by stop count (fewer stops = better)
        results.sort(key=lambda x: x.stop_count)
        return results

    def _find_indirect(self, from_stop: str, to_stop: str) -> list[IndirectRoute]:
        from_norm = normalize_stop(from_stop)
        to_norm = normalize_stop(to_stop)

        # Routes that contain the source
        routes_with_from: list[tuple[BusRoute, int]] = []
        for route in self.routes:
            stop_map = self._stops_in_route(route)
            if from_norm in stop_map:
                routes_with_from.append((route, stop_map[from_norm]))

        # Routes that contain the destination
        routes_with_to: list[tuple[BusRoute, int]] = []
        for route in self.routes:
            stop_map = self._stops_in_route(route)
            if to_norm in stop_map:
                routes_with_to.append((route, stop_map[to_norm]))

        indirect_results = []
        seen_transfers = set()

        for route_a, from_idx in routes_with_from:
            stops_a = {normalize_stop(s): (i, s) for i, s in enumerate(route_a.stops)}

            for route_b, to_idx in routes_with_to:
                if route_a.name == route_b.name:
                    continue

                stops_b = {
                    normalize_stop(s): (i, s) for i, s in enumerate(route_b.stops)
                }

                # Find common stops (transfer points)
                common = set(stops_a.keys()) & set(stops_b.keys())
                common.discard(from_norm)
                common.discard(to_norm)

                for transfer_norm in common:
                    transfer_idx_a, transfer_canonical = stops_a[transfer_norm]
                    transfer_idx_b, _ = stops_b[transfer_norm]

                    sig = (route_a.name, route_b.name, transfer_norm)
                    if sig in seen_transfers:
                        continue
                    seen_transfers.add(sig)

                    leg1 = self._build_direct_route(
                        route_a, from_stop, transfer_canonical, from_idx, transfer_idx_a
                    )
                    leg2 = self._build_direct_route(
                        route_b, transfer_canonical, to_stop, transfer_idx_b, to_idx
                    )

                    indirect_results.append(
                        IndirectRoute(
                            transfer_point=transfer_canonical,
                            first_leg=leg1,
                            second_leg=leg2,
                            total_stops=leg1.stop_count + leg2.stop_count,
                        )
                    )

        indirect_results.sort(key=lambda x: x.total_stops)
        return indirect_results[:5]  # top 5
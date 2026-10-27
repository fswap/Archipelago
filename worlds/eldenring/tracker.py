from argparse import ArgumentParser
from dataclasses import asdict, dataclass, replace
import json
import os
import pkgutil
from typing import Any, Dict, Set, List, Iterable, Optional, Union, Tuple

tracker_zip_has_json = False
"""Whether tracker data files are included in the image zip or not.

This should be False for release builds."""

image_zip_md5s = ["2f456c33a943eff836cca6f0e11262e4"]
"""Image zip hashes compatible with the current version of the apworld.

New images are required when bounds.json changes."""


@dataclass
class MapBounds:
    name: str
    """Display name of the map."""

    regions: List[int]
    """Play regions which indicate presence in this map."""

    layer: int
    """Which base map the coordinates are found in."""

    layer_height: int
    """Height of the image, used to invert y coordinate from game coordinates."""

    min_x: int
    max_x: int
    min_y: int
    max_y: int


_cached_map_bounds: Optional[List[MapBounds]] = None
_bounds_index_by_region: Dict[int, int] = {}


def _get_map_bounds() -> List[MapBounds]:
    """Returns map bounds corresponding to the tracker maps list, reading it the first time."""
    global _cached_map_bounds, _bounds_index_by_region
    if _cached_map_bounds is None:
        bounds_json = json.loads(pkgutil.get_data(MapBounds.__module__, "tracker/bounds.json").decode("utf-8-sig")) or []
        _cached_map_bounds = [MapBounds(**bounds) for bounds in bounds_json]
        _bounds_index_by_region = {region: index for (index, bounds) in enumerate(_cached_map_bounds) for region in bounds.regions}
    return _cached_map_bounds


def map_page_index(data: Any) -> int:
    """Returns map index for tracker."""
    map_bounds = _get_map_bounds()
    if not map_bounds or not isinstance(data, list) or len(data) != 4:
        # This should only happen when data not yet received, so just show first map
        return 0
    [region, _layer, _x, _z] = data
    index = _bounds_index_by_region.get(region)
    if index is None:
        index = _bounds_index_by_region.get(region // 1000)
    return -1 if index is None else index


def location_icon_coords(index: Optional[int], data: Any) -> Optional[Tuple[int, int, str]]:
    """Returns player coordinates for tracker."""
    map_bounds = _get_map_bounds()
    if not map_bounds or not isinstance(data, list) or len(data) != 4:
        return None
    if index is None or index < 0 or index >= len(map_bounds):
        return None
    [_region, layer, x, z] = data
    bounds = map_bounds[index]
    if layer != bounds.layer:
        return None
    y = bounds.layer_height - z
    if bounds.min_x <= x < bounds.max_x and bounds.min_y <= y < bounds.max_y:
        return (x - bounds.min_x, y - bounds.min_y, "player.png")


"""
Test cases for Voronoi Diagram creation.

Overall, I'm trying less to test the correctness of the result
and more to cover input cases and behavior, making sure
that we return a sane result without error or raise a useful one.
"""

import numpy as np
import pytest

from shapely.geos import geos_version
from shapely.geometry import MultiPoint
from shapely.wkt import loads as load_wkt

from shapely.ops import voronoi_diagram

requires_geos_35 = pytest.mark.skipif(geos_version < (3, 5, 0), reason='GEOS >= 3.5.0 is required.')


@requires_geos_35
def test_no_regions():
    mp = MultiPoint(points=[(0.5, 0.5)])
    with np.errstate(invalid="ignore"):
        regions = voronoi_diagram(mp)

    assert len(regions.geoms) == 0


@requires_geos_35
def test_two_regions():
    mp = MultiPoint(points=[(0.5, 0.5), (1.0, 1.0)])
    regions = voronoi_diagram(mp)

    assert len(regions.geoms) == 2


@requires_geos_35
def test_edges():
    mp = MultiPoint(points=[(0.5, 0.5), (1.0, 1.0)])
    regions = voronoi_diagram(mp, edges=True)

    assert len(regions.geoms) == 1
    assert all(r.type == 'LineString' for r in regions.geoms)


@requires_geos_35
def test_smaller_envelope():
    mp = MultiPoint(points=[(0.5, 0.5), (1.0, 1.0)])
    poly = load_wkt('POLYGON ((0 0, 0.5 0, 0.5 0.5, 0 0.5, 0 0))')

    regions = voronoi_diagram(mp, envelope=poly)

    assert len(regions.geoms) == 2
    assert sum(r.area for r in regions.geoms) > poly.area


@requires_geos_35
def test_larger_envelope():
    """When the envelope we specify is larger than the
    area of the input feature, the created regions should
    expand to fill that area."""
    mp = MultiPoint(points=[(0.5, 0.5), (1.0, 1.0)])
    poly = load_wkt('POLYGON ((0 0, 2 0, 2 2, 0 2, 0 0))')

    regions = voronoi_diagram(mp, envelope=poly)

    assert len(regions.geoms) == 2
    assert sum(r.area for r in regions.geoms) == poly.area


@requires_geos_35
def test_from_polygon():
    poly = load_wkt('POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))')
    regions = voronoi_diagram(poly)

    assert len(regions.geoms) == 4


@requires_geos_35
def test_from_polygon_with_enough_tolerance():
    poly = load_wkt('POLYGON ((0 0, 0.5 0, 0.5 0.5, 0 0.5, 0 0))')
    regions = voronoi_diagram(poly, tolerance=1.0)

    assert len(regions.geoms) == 2


@requires_geos_35
def test_from_polygon_without_enough_tolerance():
    poly = load_wkt('POLYGON ((0 0, 0.5 0, 0.5 0.5, 0 0.5, 0 0))')
    with pytest.raises(ValueError) as exc:
        voronoi_diagram(poly, tolerance=0.6)

    assert "Could not create Voronoi Diagram with the specified inputs" in str(exc.value)
    assert "Try running again with default tolerance value." in str(exc.value)


@requires_geos_35
def test_from_polygon_without_floating_point_coordinates():
    poly = load_wkt('POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))')
    with pytest.raises(ValueError) as exc:
        voronoi_diagram(poly, tolerance=0.1)

    assert "Could not create Voronoi Diagram with the specified inputs" in str(exc.value)
    assert "Try running again with default tolerance value." in str(exc.value)


@requires_geos_35
def test_from_multipoint_without_floating_point_coordinates():
    """A Multipoint with the same "shape" as the above Polygon raises the same error..."""
    mp = load_wkt('MULTIPOINT (0 0, 1 0, 1 1, 0 1)')

    with pytest.raises(ValueError) as exc:
        voronoi_diagram(mp, tolerance=0.1)

    assert "Could not create Voronoi Diagram with the specified inputs" in str(exc.value)
    assert "Try running again with default tolerance value." in str(exc.value)


@requires_geos_35
def test_from_multipoint_with_tolerace_without_floating_point_coordinates():
    """This multipoint will not work with a tolerance value."""
    mp = load_wkt('MULTIPOINT (0 0, 1 0, 1 2, 0 1)')
    with pytest.raises(ValueError) as exc:
        voronoi_diagram(mp, tolerance=0.1)

    assert "Could not create Voronoi Diagram with the specified inputs" in str(exc.value)
    assert "Try running again with default tolerance value." in str(exc.value)


@requires_geos_35
def test_from_multipoint_without_tolerace_without_floating_point_coordinates():
    """But it's fine without it."""
    mp = load_wkt('MULTIPOINT (0 0, 1 0, 1 2, 0 1)')
    regions = voronoi_diagram(mp)
    assert len(regions.geoms) == 4


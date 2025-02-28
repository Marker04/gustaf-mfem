from gustaf import _version
from gustaf import settings
from gustaf import vertices
from gustaf import edges
from gustaf import faces
from gustaf import volumes
from gustaf import show
from gustaf import utils
from gustaf import create
from gustaf import io
from gustaf import helpers
from gustaf.vertices import Vertices
from gustaf.edges import Edges
from gustaf.faces import Faces
from gustaf.volumes import Volumes

has_spline = False
try:
    from gustaf import spline
    from gustaf.spline.base import BSpline, NURBS, Bezier, RationalBezier
    from gustaf.spline.ffd import FFD
    has_spline = True
except ImportError:
    spline = "cannot import spline modules"

# import try/catch for triangle and gustaf-tetgen

__version__ = _version.version

__all__ = [
        "__version__",
        "settings",
        "vertices",
        "edges",
        "faces",
        "volumes",
        "show",
        "utils",
        "create",
        "io",
        "helpers",
        "Vertices",
        "Edges",
        "Faces",
        "Volumes",
        "spline",
        "has_spline",
        "BSpline",
        "NURBS",
        "Bezier",
        "RationalBezier",
        "FFD",
]

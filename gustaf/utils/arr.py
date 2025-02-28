"""gustaf/gustaf/utils/arr.py.

Useful functions for array / point operations. Named `arr`, since
`array` is python library and it sounds funny.
"""

import numpy as np

from gustaf import settings


def make_c_contiguous(array, dtype=None):
    """Make given array like object a c contiguous np.ndarray. dtype is
    optional. If None is given, just returns None.

    Parameters
    -----------
    array: array-like
    dtype: type or str
      (Optional) `numpy` interpretable type or str, describing type.

    Returns
    --------
    c_contiguous_array: np.ndarray
    """
    if array is None:
        return None

    if isinstance(array, np.ndarray):
        if array.flags.c_contiguous:
            if dtype is not None and array.dtype != dtype:
                return array.astype(dtype)

            return array

    if dtype:
        return np.ascontiguousarray(array, dtype=dtype)

    else:
        return np.ascontiguousarray(array)


def unique_rows(
        in_arr,
        return_index=True,
        return_inverse=True,
        return_counts=True,
        dtype_name=None,
):
    """
    Find unique rows using np.unique, but apply tricks. Adapted from
    `skimage.util.unique_rows`.
    url: github.com/scikit-image/scikit-image/blob/main/skimage/util/unique.py/
    Suitable for int types.

    Parameters
    -----------
    in_arr: (n, m) 2D array-like
    return_index: bool
    return_inverse: bool
    return_counts: bool
    dtype_name: str

    Returns
    --------
    unique_arr: (p, q) np.ndarray
    unique_ind: (w,) np.ndarray
    unique_inv: (t,) np.ndarray
    """
    if dtype_name is None:
        dtype_name = settings.INT_DTYPE

    in_arr = make_c_contiguous(in_arr, dtype_name)

    if len(in_arr.shape) != 2:
        raise ValueError("unique_rows can be only applied for 2D arrays")

    in_arr_row_view = in_arr.view(f"|S{in_arr.itemsize * in_arr.shape[1]}")

    unique_stuff = np.unique(
            in_arr_row_view,
            return_index=True,
            return_inverse=return_inverse,
            return_counts=return_counts,
    )
    unique_stuff = list(unique_stuff)  # list, to allow item assignment

    # switch view to original
    unique_stuff[0] = in_arr[unique_stuff[1]]
    if not return_index:
        # pop return index
        unique_stuff.pop(1)

    return unique_stuff


def close_rows(arr, tolerance=None):
    """Similar to unique_rows, but if data type is floats, use this one.
    Performs radius search using KDTree. Currently uses
    `scipy.spatial.cKDTree`.

    Parameters
    -----------
    arr: (n, d) array-like

    Returns
    --------
    close_stuff: tuple
      unique_arrays: (n, d) np.ndarray
      unique_ids: (m) np.ndarray
      inverse: (n) np.ndarray
      overlapping: list(list)
        id of neighbors within the tolerance.
    """
    from scipy.spatial import cKDTree as KDTree

    if tolerance is None:
        tolerance = settings.TOLERANCE

    # Build kdtree
    kdt = KDTree(arr)

    # Ball point query, taking tolerance as radius
    neighbors = kdt.query_ball_point(
            arr,
            tolerance,
            # workers=workers,
            # return_sorted=True # new in 1.6, but default is True, so pass.
    )

    # inverse based on original vertices.
    o_inverse = np.array(
            [n[0] for n in neighbors],
            dtype=settings.INT_DTYPE,
    )

    # unique of o_inverse, and inverse based on that
    (_, uniq_id, inv) = np.unique(
            o_inverse,
            return_index=True,
            return_inverse=True,
    )

    return (arr[uniq_id], uniq_id, inv, neighbors)


def bounds(arr):
    """Return bounds.

    Parameters
    -----------
    arr: (n, d) array-like

    Returns
    --------
    bounds: (2, d) np.ndarray
    """
    return np.vstack(
            (
                    np.min(arr, axis=0).ravel(),
                    np.max(arr, axis=0).ravel(),
            )
    )


def bounds_diagonal(arr):
    """Returns diagonal vector of the bounds.

    bounds[1] - bounds[0]

    Parameters
    -----------
    arr: (n, d) array-like

    Returns
    --------
    bounds_diagonal: (n,) np.ndarray
    """
    b = bounds(arr)
    return b[1] - b[0]


def bounds_norm(arr):
    """Returns norm of the bounds.

    Parameters
    -----------
    arr: (n, d) array-like

    Returns
    --------
    bounds_norm: float
    """
    return np.linalg.norm(bounds_diagonal(arr))


def bounds_mean(arr):
    """Returns mean of the bounds.

    Parameters
    -----------
    arr: (n, d) array-like

    Returns
    --------
    bounds_mean: (n,) array-like
    """
    return np.mean(bounds(arr), axis=0)


def select_with_ranges(arr, ranges):
    """Select array with ranges of each column. Always parsed as:

    [[greater_than, less_than], [....], ...]

    Parameters
    -----------
    ranges: (d, 2) array-like
      Takes None.

    Returns
    --------
    ids: (n,) np.ndarray
    """
    masks = []
    for i, r in enumerate(ranges):
        if r is None:
            continue

        else:
            lower = arr[:, i] > r[0]
            upper = arr[:, i] < r[1]
            if r[1] > r[0]:
                masks.append(np.logical_and(lower, upper))
            else:
                masks.append(np.logical_or(lower, upper))

    if len(masks) > 1:
        mask = np.zeros(arr.shape[0], dtype=bool)
        for i, m in enumerate(masks):
            if i == 0:
                mask = np.logical_or(mask, m)
            else:
                mask = np.logical_and(mask, m)

    else:
        mask = masks[0]

    return np.arange(arr.shape[0])[mask]


def rotation_matrix(rotation, degree=True):
    """Compute rotation matrix. Works for both 2D and 3D point sets. In 2D, it
    can rotate along the (virtual) z-axis. In 3D, it can rotate along [x, y,
    z]-axis. Uses `scipy.spatial.transform.Rotation`.

    Parameters
    -----------
    rotation: list or float
      Amount of rotation along [x,y,z] axis. Default is in degrees.
      In 2D, it can be float.
    degree: bool
      (Optional) rotation given in degrees.
      Default is `True`. If `False`, in radian.

    Returns
    --------
    rotation_matrix: np.ndarray (3,3)
    """
    from scipy.spatial.transform import Rotation as R

    rotation = np.asarray(rotation).flatten()

    if degree:
        rotation = np.radians(rotation)

    # 2D
    if len(rotation) == 1:
        return R.from_rotvec([0, 0, rotation]).as_matrix()[:2, :2]

    # 3D
    elif len(rotation) == 3:
        return R.from_rotvec(rotation).as_matrix()


def rotate(arr, rotation, rotation_axis=None, degree=True):
    """Rotates given arrays. Arrays shape[1] should equal to either 2 or 3 For
    more information, see `rotation_matrix()`.

    Parameters
    -----------
    arr: (n, (2 or 3)) list-like
    rotation: list or float
      angle of rotation (around each axis)
    rotation_axis: (n, (2 or 3)) or (2 or 3) list-like
      center of rotation

    Returns
    --------
    rotated_points: (n, d) np.ndarray
    """
    arr = make_c_contiguous(arr, settings.FLOAT_DTYPE)
    if rotation_axis is not None:
        rotation_axis = make_c_contiguous(rotation_axis,
                                          settings.FLOAT_DTYPE).ravel()

    if rotation_axis is None:
        return np.matmul(arr, rotation_matrix(rotation, degree))

    else:
        rarr = arr - rotation_axis
        rarr = np.matmul(rarr, rotation_matrix(rotation, degree))
        rarr += rotation_axis

        return rarr


def rotation_matrix_around_axis(axis=None, rotation=None, degree=True):
    """Compute rotation matrix given the axis of rotation. Works for both 2D
    and 3D Uses Rodrigues' formula.

    If axis is not specified, 2D rotation matrix is assumed.

    Parameters
    -----------
    axis: list or np.ndarray
      Axis of rotation in 3D
    rotation: float
      angle of rotation in either radiant or degrees
    degree: bool
      (Optional) rotation given in degrees.
      Default is `True`. If `False`, in radian.

    Returns
    --------
    rotation_matrix: np.ndarray (3,3) of np.ndarray (2,2)
    """
    # Assure angle is specified
    if rotation is None:
        raise ValueError("No rotation angle specified.")
    else:
        if degree:
            rotation = np.radians(rotation)

    # Check Problem dimensions
    if axis is None:
        problem_dimension = 2
    else:
        axis = np.asarray(axis).ravel()
        if axis.shape[0] != 3:
            raise ValueError("Axis dimension must be 3D")
        problem_dimension = 3

    # Assemble rotation matrix
    if problem_dimension == 2:
        rotation_matrix = np.array(
                [
                        [np.cos(rotation), -np.sin(rotation)],
                        [np.sin(rotation), np.cos(rotation)]
                ]
        )
    else:
        # See Rodrigues' formula
        rotation_matrix = np.array(
                [
                        [0, -axis[2], axis[1]], [axis[2], 0, -axis[0]],
                        [axis[1], axis[0], 0]
                ]
        )
        rotation_matrix = (
                np.eye(3) + np.sin(rotation) * rotation_matrix + (
                        (1 - np.cos(rotation))
                        * np.matmul(rotation_matrix, rotation_matrix)
                )
        )

    return rotation_matrix


def is_shape(arr, shape, strict=False):
    """Checks if arr matches given shape. shape can have negative numbers.

    Parameters
    -----------
    arr: np.ndarray
    shape: tuple
    strict: bool
      raises ValueError if shapes do not match

    Returns
    --------
    matches: bool
    """
    arr = np.asanyarray(arr)

    if arr.ndim != len(shape):
        if strict:
            raise ValueError(f"array should be {arr.ndim}D")
        return False

    for i, (a, s) in enumerate(zip(arr.shape, shape)):
        if s < 0:
            continue
        if a != s:
            if strict:
                raise ValueError(f"array should have {s} shape in {i}-D")
            return False

    return True


def is_one_of_shapes(arr, shapes, strict=False):
    """Tuple/list of given shapes, iterates and checks with is_shape. Useful if
    you have multiple acceptable shapes.

    Parameters
    -----------
    arr: np.ndarray
    shapes: tuple or list
      tuple/list of tuple/list
    strict: bool

    Returns
    --------
    matches: bool
    """
    arr = np.asanyarray(arr)
    matches = False
    for s in shapes:
        m = is_shape(arr, s, strict=False)
        if m:
            matches = True

    if not matches:
        if strict:
            raise ValueError(
                    f"array's shape {arr.shape} is not one of f{shapes}"
            )
        return False

    return True

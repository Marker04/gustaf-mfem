"""gustaf/gustaf/helpers/data.py.

Helps helpee to manage data. Some useful data structures.
"""

import abc
from functools import wraps
from collections import namedtuple

import numpy as np


class TrackedArray(np.ndarray):
    """Taken from nice implementations of `trimesh` (see LICENSE.txt).
    `https://github.com/mikedh/trimesh/blob/main/trimesh/caching.py`. Minor
    adaption, since we don't have hashing functionalities.

    All the inplace functions will set modified flag and if some operations
    has potential to cause un-trackable behavior, writeable flags will be set
    to False.

    Note, if you really really want, it is possible to change the tracked
    array without setting modified flag.
    """

    __slots__ = ("_modified", "_source")

    def __array_finalize__(self, obj):
        """Sets default flags for any arrays that maybe generated based on
        tracked array."""
        self._modified = True
        self._source = int(0)

        if isinstance(obj, type(self)):
            if isinstance(obj._source, int):
                self._source = obj
            else:
                self._source = obj._source

    @property
    def mutable(self):
        return self.flags['WRITEABLE']

    @mutable.setter
    def mutable(self, value):
        self.flags.writeable = value

    def _set_modified(self):
        """set modified flags to itself and to the source."""
        self._modified = True
        if isinstance(self._source, type(self)):
            self._source._modified = True

    def copy(self, *args, **kwargs):
        """copy gives np.ndarray.

        no more tracking.
        """
        return np.array(self, copy=True)

    def view(self, *args, **kwargs):
        """Set writeable flags to False for the view."""
        v = super(self.__class__, self).view(*args, **kwargs)
        v.flags.writeable = False
        return v

    def __iadd__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__iadd__(*args, **kwargs)

    def __isub__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__isub__(*args, **kwargs)

    def __imul__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__imul__(*args, **kwargs)

    def __idiv__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__idiv__(*args, **kwargs)

    def __itruediv__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__itruediv__(*args, **kwargs)

    def __imatmul__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__imatmul__(*args, **kwargs)

    def __ipow__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__ipow__(*args, **kwargs)

    def __imod__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__imod__(*args, **kwargs)

    def __ifloordiv__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__ifloordiv__(*args, **kwargs)

    def __ilshift__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__ilshift__(*args, **kwargs)

    def __irshift__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__irshift__(*args, **kwargs)

    def __iand__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__iand__(*args, **kwargs)

    def __ixor__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__ixor__(*args, **kwargs)

    def __ior__(self, *args, **kwargs):
        self._set_modified()
        return super(self.__class__, self).__ior__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self._set_modified()
        super(self.__class__, self).__setitem__(*args, **kwargs)

    def __setslice__(self, *args, **kwargs):
        self._set_modified()
        super(self.__class__, self).__setslice__(*args, **kwargs)

    def __getslice__(self, *args, **kwargs):
        self._set_modified()
        """
        return slices I am pretty sure np.ndarray does not have __*slice__
        """
        slices = super(self.__class__, self).__getitem__(*args, **kwargs)
        if isinstance(slices, np.ndarray):
            slices.flags.writeable = False
        return slices


def make_tracked_array(array, dtype=None, copy=True):
    """Taken from nice implementations of `trimesh` (see LICENSE.txt).
    `https://github.com/mikedh/trimesh/blob/main/trimesh/caching.py`.

    ``Properly subclass a numpy ndarray to track changes.
    Avoids some pitfalls of subclassing by forcing contiguous
    arrays and does a view into a TrackedArray.``

    Factory-like wrapper function for TrackedArray.

    Parameters
    ------------
    array: array- like object
      To be turned into a TrackedArray
    dtype: np.dtype
      Which dtype to use for the array
    copy: bool
      Default is True. copy if True.

    Returns
    ------------
    tracked : TrackedArray
      Contains input array data
    """
    # if someone passed us None, just create an empty array
    if array is None:
        array = []
    # make sure it is contiguous then view it as our subclass
    tracked = np.ascontiguousarray(array, dtype=dtype)
    if copy:
        tracked = tracked.copy().view(TrackedArray)

    # should always be contiguous here
    assert tracked.flags['C_CONTIGUOUS']

    return tracked


class DataHolder(abc.ABC):
    __slots__ = [
            "_helpee",
            "_saved",
    ]

    def __init__(self, helpee):
        """Base class for any data holder. Behaves similar to dict.

        Attributes
        -----------
        None

        Parameters
        -----------
        helpee: object
          GustafBase objects would probably make the most sense here.
        """
        self._helpee = helpee
        self._saved = dict()

    def __setitem__(self, key, value):
        """Raise Error to disable direct value setting.

        Parameters
        -----------
        key: str
        value: object

        Returns
        --------
        None
        """
        raise NotImplementedError(
                "Sorry, you can't set items directly for "
                f"{type(self).__qualname__}"
        )

    def __getitem__(self, key):
        """Returns stored item if the key exists.

        Parameters
        -----------
        key: str

        Returns
        --------
        value: object
        """
        if key in self._saved.keys():
            return self._saved[key]

        else:
            raise KeyError(f"`{key}` is not stored for {type(self._helpee)}")

    def get(self, key, default_values=None):
        """Returns stored item if the key exists. Else, given default value. If
        the key exist, default value always exists, since it is initialized
        that way.

        Parameters
        -----------
        key: str
        default_values: object

        Returns
        --------
        value: np.ndarray
        """
        if key in self._saved.keys():
            return self._saved[key]
        else:
            return default_values

    def keys(self):
        """Returns keys of data holding dict.

        Parameters
        -----------
        None

        Returns
        --------
        keys: dict_keys
        """
        return self._saved.keys()

    def values(self):
        """Returns values of data holding dict.

        Parameters
        -----------
        None

        Returns
        --------
        values: dict_values
        """
        return self._saved.values()

    def items(self):
        """Returns items of data holding dict.

        Parameters
        -----------
        None

        Returns
        --------
        values: dict_values
        """
        return self._saved.items()


class ComputedData(DataHolder):
    _depends = None
    _inv_depends = None

    ___slots___ = []

    def __init__(self, helpee, **kwrags):
        """Stores last computed values. Keys are expected to be the same as
        helpee's function that computes the value.

        Attributes
        -----------
        None

        Parameters
        -----------
        helpee: GustafBase
        kwrags: **kwrags
          keys and str of attributes, on which this array depends
        """
        super().__init__(helpee)

    @classmethod
    def depends_on(cls, var_names, make_property=False):
        """Decorator as classmethod.

        checks if the key should be computed. Two cases, where the answer is
        yes:
        1. there's modification on arrays that the key depend on.
          -> erases all other
        2. is corresponding value None?
        Supports multi-dependency

        Parameters
        -----------
        var_name: list
        make_property:
        """

        def inner(func):
            # followings are done once while modules are loaded
            # just subclass this class to make a special helper
            # for each helpee class.
            assert isinstance(var_names, list), "var_names should be a list"
            # initialize property
            # _depends is dict(str: list)
            if cls._depends is None:
                cls._depends = dict()
            if cls._depends.get(func.__name__, None) is None:
                cls._depends[func.__name__] = list()
            # add dependency info
            cls._depends[func.__name__].extend(var_names)

            # _inv_depends is dict(str: list)
            if cls._inv_depends is None:
                cls._inv_depends = dict()
            # add inverse dependency
            for vn in var_names:
                if cls._inv_depends.get(vn, None) is None:
                    cls._inv_depends[vn] = list()

                cls._inv_depends[vn].append(func.__name__)

            @wraps(func)
            def compute_or_return_saved(*args, **kwargs):
                """Check if the key should be computed,"""
                # extract some related info
                self = args[0]  # the helpee itself
                recompute = kwargs.get("recompute", False)
                return_saved = kwargs.get("return_saved", False)

                # if return_saved, try to escape as soon as possible
                if return_saved:
                    saved = self._computed._saved.get(func.__name__, None)
                    if saved is not None and not recompute:
                        return saved

                # computed arrays are called _computed.
                # loop over dependees and check if they are modified
                for dependee_str in cls._depends[func.__name__]:
                    dependee = getattr(self, dependee_str)
                    # is modified?
                    if dependee._modified:
                        for inv in cls._inv_depends[dependee_str]:
                            self._computed._saved[inv] = None

                # is saved / want to recompute?
                # recompute is added for computed values that accepts params.
                saved = self._computed._saved.get(func.__name__, None)
                if saved is not None and not recompute:
                    return saved

                # we've reached this point because we have to compute this
                computed = func(*args, **kwargs)
                if isinstance(computed, np.ndarray):
                    computed.flags.writeable = False  # configurable?
                self._computed._saved[func.__name__] = computed

                # so, all fresh. we can press NOT-modified  button
                for dependee_str in cls._depends[func.__name__]:
                    dependee = getattr(self, dependee_str)
                    dependee._modified = False

                return computed

            if make_property:
                return property(compute_or_return_saved)
            else:
                return compute_or_return_saved

        return inner


Unique2DFloats = namedtuple(
        "Unique2DFloats", ["values", "ids", "inverse", "intersection"]
)
"""
namedtuple to hold unique information of float type arrays.
Note that for float types, "close enough" might be a better name than unique.
This way, all tracked arrays, as long as they are 2D, have a dot separated
syntax to acces unique info. For example, `mesh.unique_vertices.ids`.

Attributes
-----------
values: (n, d) np.ndarray
ids: (n) np.ndarray
inverse: (m) np.ndarray
intersection: (m) list of list
  given original array's index, returns overlapping arrays, including itself.
"""

Unique2DIntegers = namedtuple(
        "Unique2DIntegers", ["values", "ids", "inverse", "counts"]
)
"""
namedtuple to hold unique information of integer type arrays.
Similar approach to Unique2DFloats.

Attributes
-----------
values: (n, d) np.ndarray
ids: (n) np.ndarray
inverse: (m) np.ndarray
counts: (n) np.ndarray
"""


class ComputedMeshData(ComputedData):
    """A class to hold computed-mesh-data.

    Subclassed to keep its own dependency info.
    """
    pass

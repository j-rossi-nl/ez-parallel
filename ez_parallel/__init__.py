# type: ignore[attr-defined]
"""Easy Parallel Multiprocessing"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from .misc import (
    batch_iterator,
    batch_iterator_from_iterable,
    batch_iterator_from_sliceable,
    list_iterator,
)
from .multiprocess import multiprocess, multithread, queue_worker

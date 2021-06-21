from typing import Any, Callable, Iterable, Iterator, List, Tuple

import logging


def list_iterator(items: List[Any]) -> Tuple[Callable[[], Iterator[Any]], int]:
    def _iterator():
        yield from items

    return _iterator, len(items)


def batch_iterator_from_sliceable(
    items: Any, batch_size: int
) -> Callable[[], Iterator[Any]]:
    def _iterator():
        batch_id = 0
        while True:
            logging.info("Get one batch")
            batch = items[batch_id * batch_size : (batch_id + 1) * batch_size]
            if len(batch) > 0:
                yield batch
                if len(batch) < batch_size:
                    break
            batch_id += 1

    return _iterator


def batch_iterator_from_iterable(
    items: Iterable[Any], batch_size: int
) -> Callable[[], Iterator[Any]]:
    def _iterator():
        while True:
            logging.info("Get one batch")
            batch = [x for _, x in zip(range(batch_size), items)]
            yield batch
            if len(batch) < batch_size:
                break

    return _iterator


def batch_iterator(
    items: List[Any], batch_size: int
) -> Tuple[Callable[[], Iterator[Any]], int]:
    list_iter_fn, _ = list_iterator(items)
    list_iter = list_iter_fn()

    def _iterator():
        while True:
            batch = [x for _, x in zip(range(batch_size), list_iter)]
            yield batch
            if len(batch) < batch_size:
                break

    return _iterator, len(items)

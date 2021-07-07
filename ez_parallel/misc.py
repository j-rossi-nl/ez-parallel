from typing import Any, Callable, Iterable, Iterator, List, Tuple

import logging


def list_iterator(items: List[Any]) -> Tuple[Callable[[], Iterator[Any]], int]:
    """
    Build a generator from a list.
    The created iterator will yield the items of the list one by one.

    :param items: list of items to process
    :return: Tuple generator, number of items
    """

    def _iterator():
        yield from items

    return _iterator, len(items)


def batch_iterator_from_sliceable(
    items: Any, batch_size: int
) -> Callable[[], Iterator[Any]]:
    """
    Build a generator of batches from any object that can be sliced.
    The created iterator will yield the items of the list by batches.
    Each call to next() will return a batch, i.e. a list of batch_size items.
    The last batch might contain less than batch_size items.

    :param items: list of items
    :param batch_size: number of items in a batch
    :return: generator
    """

    def _iterator():
        batch_id = 0
        while True:
            batch = items[batch_id * batch_size : (batch_id + 1) * batch_size]
            if len(batch) > 0:
                logging.info("Get one batch")
                yield batch
                if len(batch) < batch_size:
                    logging.info("Last batch")
                    break
            batch_id += 1

    return _iterator


def batch_iterator_from_iterable(
    items: Iterable[Any], batch_size: int
) -> Callable[[], Iterator[Any]]:
    """
    Build a generator of batches from an iterable.
    The created iterator will yield the items of the list by batches.
    Each call to next() will return a batch, i.e. a list of items.
    The last batch might contain less than batch_size items.

    :param items: iterable yielding items
    :param batch_size: number of items in a batch
    :return: generator
    """

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
    """
    Build a generator of batches from a list of items.
    The created iterator will yield the items of the list by batches.
    Each call to next() will return a batch, i.e. a list of items.
    The last batch might contain less than batch_size items.

    :param items: list of items
    :param batch_size: number of items in a batch
    :return: Tuple generator, number of items (NOT number of batches)
    """
    list_iter_fn, _ = list_iterator(items)
    list_iter = list_iter_fn()

    def _iterator():
        while True:
            batch = [x for _, x in zip(range(batch_size), list_iter)]
            yield batch
            if len(batch) < batch_size:
                break

    return _iterator, len(items)


try:
    from elasticsearch_dsl import Search

    def elasticsearch_iterator(
        s: Search,
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        """
        Build a generator items retrieved from ElasticSearch from a Search object.
        The created iterator will yield the results of the search one by one
        When the Search object is incorrect (no connection, no index, ...), exceptions will be raised, and execution
        will stop.

        :param s: Search object
        :return: Tuple generator, number of items
        """
        count = s.count()

        def _iterator():
            scan = s.scan()
            yield from scan

        return _iterator, count

    def elasticsearch_batch_iterator(
        s: Search, batch_size: int
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        """
        Build a generator of items retrieved from ElasticSearch from a Search object.
        The created iterator will yield the results of the search in batches.
        Each call to next() will return a batch, i.e. a list of items.
        The last batch might contain less than batch_size items.
        When the Search object is incorrect (no connection, no index, ...), exceptions will be raised, and execution
        will stop.

        :param s: Search object
        :param batch_size: number of items per batch
        :return: Tuple generator, number of items
        """
        generator, count = elasticsearch_iterator(s)
        iterable = generator()

        batch_generator = batch_iterator_from_iterable(iterable, batch_size)

        return batch_generator, count


except ImportError:
    elasticsearch_dsl = None
    Search = Any

    def elasticsearch_iterator(
        s: Search,
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        raise NotImplementedError(
            "Install elasticsearch_dsl in order to use the function elasticsearch_iterator"
        )

    def elasticsearch_batch_iterator(
        s: Search, batch_size: int
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        raise NotImplementedError(
            "Install elasticsearch_dsl in order to use the function elasticsearch_batch_iterator"
        )


try:
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.parquet as pq
    from pyarrow.dataset import FileSystemDataset

    def parquet_dataset_batch_iterator(
        dataset: FileSystemDataset, batch_size: int
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        """
        Build a generator of items retrieved from a Parquet Dataset.
        The created iterator will yield the items in batches.
        Each call to next() will return a batch, i.e. an object pyarrow.RecordBatch.
        Batches will not all have the same size.

        :rtype: object
        :param dataset: a Parquet Dataset object
        :param batch_size: number of items per batch
        :return: Tuple generator, number of items (NOT number of batches)
        """

        def _iterator():
            if pa.__version__ < "4.0.0":
                # noinspection PyArgumentList
                for scan_task in dataset.scan(batch_size=batch_size):
                    yield from scan_task.execute()
            else:
                yield from dataset.to_batches(batch_size=batch_size)

        nb_rows = sum(pq.read_metadata(f).num_rows for f in dataset.files)
        return _iterator, nb_rows


except ImportError:
    pa, ds, pq = None, None, None
    FileSystemDataset = Any

    def parquet_dataset_batch_iterator(
        dataset: FileSystemDataset, batch_size: int
    ) -> Tuple[Callable[[], Iterator[Any]], int]:
        raise NotImplementedError(
            "Install pyarrow in order to use the function parquet_dataset_batch_iterator"
        )

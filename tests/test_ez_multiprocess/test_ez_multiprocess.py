from typing import Any

import random
import tempfile
import time
from functools import reduce

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
from ez_parallel import (
    batch_iterator,
    batch_iterator_from_iterable,
    batch_iterator_from_sliceable,
    list_iterator,
    multiprocess,
    multithread,
    parquet_dataset_batch_iterator,
    queue_worker,
)


def test_batch_iterator():
    num_items = random.randint(1000, 1500)
    batch_size = random.randint(64, 128)

    data = [random.random() for _ in range(num_items)]
    gen, count = batch_iterator(data, batch_size)

    assert count == num_items

    iterable = gen()
    batch = next(iterable)

    assert isinstance(batch, list)
    assert len(batch) == batch_size

    gen, count = batch_iterator(data, batch_size)
    iterable = gen()
    batches = list(iterable)
    out_data = reduce(lambda a, b: a + b, batches)

    assert len(out_data) == num_items


def test_batch_iterator_from_iterable():
    num_items = random.randint(1000, 1500)
    batch_size = random.randint(64, 128)

    data = (random.random() for _ in range(num_items))
    gen = batch_iterator_from_iterable(data, batch_size)
    iterable = gen()
    batch = next(iterable)

    assert isinstance(batch, list)
    assert len(batch) == batch_size

    data = (random.random() for _ in range(num_items))
    gen = batch_iterator_from_iterable(data, batch_size)
    iterable = gen()
    batches = list(iterable)
    out_data = reduce(lambda a, b: a + b, batches)

    assert len(out_data) == num_items


def test_batch_iterator_from_sliceable():
    num_items = random.randint(1000, 1500)
    batch_size = random.randint(64, 128)

    data = [random.random() for _ in range(num_items)]
    gen = batch_iterator_from_sliceable(data, batch_size)

    iterable = gen()
    batch = next(iterable)

    assert isinstance(batch, list)
    assert len(batch) == batch_size

    gen = batch_iterator_from_sliceable(data, batch_size)
    iterable = gen()
    batches = list(iterable)
    out_data = reduce(lambda a, b: a + b, batches)

    assert len(out_data) == num_items


def test_elasticsearch_iterator():
    """
    No automatic test. Tried and working.
    :return:
    """
    pass


def test_elasticsearch_batch_iterator():
    """
    No automatic test. Tried and working.
    :return:
    """
    pass


def test_list_iterator():
    num_items = random.randint(1000, 1500)

    data = [random.random() for _ in range(num_items)]
    gen, count = list_iterator(data)

    assert count == num_items

    iterable = gen()
    item = next(iterable)

    assert isinstance(item, float)


def test_parquet_dataset():
    num_rows = 1000
    batch_size = 64

    data = [
        {"a": random.random(), "b": random.randint(1, 20)}
        for _ in range(num_rows)
    ]

    with tempfile.NamedTemporaryFile("w") as tmp:
        pd.DataFrame(data).to_parquet(tmp.name, engine="pyarrow")
        dataset: Any = ds.dataset(tmp.name)
        dataset_cast: ds.FileSystemDataset = dataset
        gen, count = parquet_dataset_batch_iterator(dataset_cast, batch_size)

        assert count == num_rows

        iterable = gen()
        batch = next(iterable)

        assert isinstance(batch, pa.RecordBatch)
        assert batch.num_rows == batch_size


def test_parallel():
    """Test parallel processing"""

    @queue_worker
    def square(x: float):
        _ = x ** 2
        time.sleep(0.1)
        return 1

    num_rows = 1000
    data = [random.random() for _ in range(num_rows)]

    gen, count = list_iterator(data)
    multiprocess(
        worker_fn=square,
        input_iterator_fn=gen,
        total=count,
        nb_workers=8,
        description="Compute Squares",
    )


def test_multithread():
    @queue_worker
    def square(x: float):
        _ = x ** 2
        time.sleep(0.1)
        return 1

    num_rows = 1000
    data = [random.random() for _ in range(num_rows)]

    gen, count = list_iterator(data)
    multithread(
        worker_fn=square,
        input_iterator_fn=gen,
        total=count,
        nb_workers=8,
        description="Compute Squares",
    )

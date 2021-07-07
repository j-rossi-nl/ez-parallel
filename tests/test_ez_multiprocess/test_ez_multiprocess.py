from typing import Any

import random
import tempfile

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
from ez_parallel import (
    batch_iterator,
    batch_iterator_from_iterable,
    batch_iterator_from_sliceable,
    elasticsearch_batch_iterator,
    elasticsearch_iterator,
    list_iterator,
    parquet_dataset_batch_iterator,
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


def test_batch_iterator_from_iterable():
    num_items = random.randint(1000, 1500)
    batch_size = random.randint(64, 128)

    data = (random.random() for _ in range(num_items))
    gen = batch_iterator_from_iterable(data, batch_size)

    iterable = gen()
    batch = next(iterable)

    assert isinstance(batch, list)
    assert len(batch) == batch_size


def test_batch_iterator_from_sliceable():
    num_items = random.randint(1000, 1500)
    batch_size = random.randint(64, 128)

    data = [random.random() for _ in range(num_items)]
    gen = batch_iterator_from_sliceable(data, batch_size)

    iterable = gen()
    batch = next(iterable)

    assert isinstance(batch, list)
    assert len(batch) == batch_size


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
        dataset: ds.FileSystemDataset
        gen, count = parquet_dataset_batch_iterator(dataset, batch_size)

        assert count == num_rows

        iterable = gen()
        batch = next(iterable)

        assert isinstance(batch, pa.RecordBatch)
        assert batch.num_rows == batch_size


def test_pass():
    """Sorry no test for the moment"""
    assert True

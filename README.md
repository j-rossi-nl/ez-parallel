# ez-parallel

<div align="center">

[![Build status](https://github.com/j-rossi-nl/ez-parallel/workflows/build/badge.svg?branch=master&event=push)](https://github.com/j-rossi-nl/ez-parallel/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/ez-parallel.svg)](https://pypi.org/project/ez-parallel/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/j-rossi-nl/ez-parallel/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/j-rossi-nl/ez-parallel/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/j-rossi-nl/ez-parallel/releases)
[![License](https://img.shields.io/github/license/j-rossi-nl/ez-parallel)](https://github.com/j-rossi-nl/ez-parallel/blob/master/LICENSE)

Easy Parallel Multiprocessing

</div>

## Installation

With `pip` or `pip3`:
```bash
pip install -U ez-parallel
```
or
```bash
pip install ez-parallel
```

With `Poetry`:
```bash
poetry add ez-parallel
```

## Usage

* Process a list of items by using parallel workers
  * Define what a worker does
  * Define how to iterate through the data
  * Just run
* Display a global progress bar
* Does the same for multithread


### Multithread vs Multiprocessing

In multiprocessing, new processes will be launched, they won't share memory. The user should implement a way 
to store the results of a worker and gather these results when `multiprocess()` returns.

With multithreading, new threads will be launched, they all share the memory of the parent process. This 
also restricts the runtime to a single CPU-core, as threads from a process do not get allocated to different 
cores. There will be no performance improvement when the distributed work is CPU-bound. 

How to choose? (guidelines)
* CPU-heavy (data transformation, data preprocessing): multiprocessing. 
* IO-heavy (DB requests, File I/O): multithreading.  

## Examples

### How to process a list? 

```python
import time

from ez_parallel import list_iterator, queue_worker, multiprocess

@queue_worker
def work_one_thing(x: int) -> int:
  # do something
  a = x + 2
  time.sleep(0.1)
  
  # Worked on ONE thing = return 1
  return 1

# Data
things_to_process = list(range(1000000))

# Create the iterator over the things to process
iter_fn, nb_things = list_iterator(things_to_process)

# Process all the things in parallel with 20 processes
multiprocess(
  worker_fn=work_one_thing,
  input_iterator_fn=iter_fn,
  total=nb_things,
  nb_workers=20,
  description='Process the things'
)

```

### How to Process a list by batch?

```python
import time
from typing import List

from ez_parallel import batch_iterator_from_sliceable, queue_worker, multiprocess


@queue_worker
def work_one_thing(x: List[int]) -> int:
  # do something
  a = [y + 2 for y in x]
  time.sleep(0.1)
  
  # Worked on ONE thing = return 1
  return len(x)

# Data
things_to_process = list(range(1000000))

# Create the iterator over the things to process
# This will yield batches of 128 things
iter_fn = batch_iterator_from_sliceable(items=things_to_process, batch_size=128)
nb_things = len(things_to_process)

# Process all the things in parallel with 20 processes
multiprocess(
  worker_fn=work_one_thing,
  input_iterator_fn=iter_fn,
  total=nb_things,
  nb_workers=20,
  description='Process the things'
)

```

### How to Process a list by batch in multithread?

```python
import time
from typing import List

from ez_parallel import batch_iterator_from_sliceable, queue_worker, multithread


@queue_worker
def work_one_thing(x: List[int]) -> int:
  # do something
  a = [y + 2 for y in x]
  time.sleep(0.1)
  
  # Worked on ONE thing = return 1
  return len(x)

# Data
things_to_process = list(range(1000000))

# Create the iterator over the things to process
# This will yield batches of 128 things
iter_fn = batch_iterator_from_sliceable(items=things_to_process, batch_size=128)
nb_things = len(things_to_process)

# Process all the things in parallel with 20 processes
multithread(
  worker_fn=work_one_thing,
  input_iterator_fn=iter_fn,
  total=nb_things,
  nb_workers=20,
  description='Process the things'
)

```

### How to collect results in multiprocessing?

(Suggestion using temporary files)
In this scenario, results are recorded as JSONL files, the final result is the concatenation of all files.

```python
import glob
import json
import os
import random
import shutil
import string
import tempfile
from typing import List

from ez_parallel import batch_iterator_from_sliceable, queue_worker, multithread


def random_file_name() -> str:
  return ''.join(random.choices(string.ascii_letters, k=32))  


# All processes write in the same file
# The OS will deal with concurrent access
tmp_file = os.path.join(tempfile.gettempdir(), random_file_name())

@queue_worker
def work_one_thing(x: List[int]) -> int:
  # This call is blocking until the file can be written
  with open(tmp_file, 'a') as out:
    for number in x:
      out.write(json.dumps({"number": number, "square": number ** 2}) + '\n')
  
  # Worked on ONE thing = return 1
  return len(x)

# Data
things_to_process = list(range(1000000))

# Create the iterator over the things to process
# This will yield batches of 128 things
iter_fn = batch_iterator_from_sliceable(items=things_to_process, batch_size=128)
nb_things = len(things_to_process)

# Process all the things in parallel with 20 processes
multithread(
  worker_fn=work_one_thing,
  input_iterator_fn=iter_fn,
  total=nb_things,
  nb_workers=20,
  description='Process the things'
)

# Collect all the data
with open(tmp_file, 'r') as src:
  data = [json.loads(line) for line in src] 

# Delete temporary file
os.remove(tmp_file)      

```

### How to collect results in multithreading

A lot easier and straightforward, because all the threads share the same memory.

```python
from typing import List

from ez_parallel import batch_iterator, queue_worker, multithread

# List are threadsafe in Python
results = []

@queue_worker
def work_one_thing(x: List[int]) -> int:
  # do something
  results.extend({"number": y, "square": y ** 2} for y in x)
  
  # Worked on ONE thing = return 1
  return len(x)

# Data
things_to_process = list(range(1000000))

# Create the iterator over the things to process
# This will yield batches of 128 things
iter_fn, nb_things = batch_iterator(items=things_to_process, batch_size=128)

# Process all the things in parallel with 20 processes
multithread(
  worker_fn=work_one_thing,
  input_iterator_fn=iter_fn,
  total=nb_things,
  nb_workers=20,
  description='Process the things'
)

print(len(results))

```




## 🛡 License

[![License](https://img.shields.io/github/license/j-rossi-nl/ez-parallel)](https://github.com/j-rossi-nl/ez-parallel/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/j-rossi-nl/ez-parallel/blob/master/LICENSE) for more details.

## 📃 Citation

```
@misc{ez-parallel,
  author = {Julien Rossi},
  title = {Easy Parallel Multiprocessing},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/j-rossi-nl/ez-parallel}}
}
```

## Credits

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).

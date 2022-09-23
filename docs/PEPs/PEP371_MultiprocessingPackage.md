# PEP 371 - Addition of the multiprocessing package to the standard library

## Abstract

The `processing` package mimics the standard library `threading` module functionality to provide a process-based approach to threaded programming allowing end-users to dispatch multiple tasks that effectively side-step the global interpreter lock.

The package also provides server and client functionality (`processing.Manager`) to provide remote sharing and management of objects and tasks so that applications may not only leverage multiple cores on the local machine, but also distribute objects and tasks across a cluster of networked machines.

While the distributed capabilities of the package are beneficial, the primary focus on this PEP is the core threading-like API and capabilities of the package.

## Rationale

The current CPython interpreter implements the Global Interpreter Lock (GIL) and GIL will remain as-is within the CPython interpreter for the foreseeable future. While the GIL itself enables clean and easy to maintain C code for the interpreter and the extension base, it may cause performance problems in multi-core machines.

The GIL itself prevents more than a single thread from running within the interpreter at any given point in time, effectively removing Python's ability to take advantage of multi-processing systems.

This package offers a method to side-step the GIL allowing applications within CPython to take advantage of multi-core architectures without asking users to completely change their programming paradigm (i.e. dropping threaded programming for another "concurrent" approach). 

This package offers CPython a "known API" which mirrors albeit in PEP-8 compliant manner, that of the threading  API, with known semantics and easy scalability.

Even if in the future CPython interpreter enables "true" threading, for some applications forking an OS process may be more desirable in specific situations than using lightweight threads especially on those platforms where process creation is fast and optimized.

For example a simple threaded application:

```python
from threading import Thread as worker

def afunc(number):
    print (number * 3)

t = worker(target=afunc, args=(4,))
t.start()
t.join()
```

This package mirrors the API as well, that with a simple change of the import this becomes:

```python
from processing import process as worker
```

The code would now execute through the `processing.process` class. This type of compatibility means that with a minor (in most cases) change in code, the users apps will be able to leverage all cores and processors on a given machine for parallel execution. In many cases this package is even faster than the normal threading approach for I/O bound programs. This takes into account that this package is in optimized C code, while the threading module is not. 

The "Distributed" Problem

The "distributed" problem is large and varied. The acceptance of this package does not preclude or recommend that programmers working on the "distributed" problem not examine other solutions for their problem domain. The intent of this package is to provide entry-level capabilities for local concurrency and the basic support to spread that concurrency across a network of machines - although the two are not tightly coupled, this could be used in conjuction with other distributed
programming packages such as OpenMPI or grpc. 

If necessary it is possible to completely decouple the local concurrency capabilities of the package from the networking/shared aspects fo the package. 



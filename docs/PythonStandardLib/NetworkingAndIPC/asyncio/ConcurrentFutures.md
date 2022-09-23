# `concurrent.futures` - Launching parallel tasks

src: [lib/concurrent/futures/thread.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/thread.py) and [lib/concurrent/futures/process.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/process.py)

The `cuncurrent.futures` module provides a high-level interface for asynchronously executing callables.

The asynchronous execution can be performed with threads, using `ThreadPoolExecutor`, or separate processes using `ProcessPoolExecutor`. Both implement the same interface which is defined by the abstract `Executor` class. 

## Executor Objects

_class_ `concurrent.futures`.**Executor**

An abstract class that provides methods to execute calls asynchronously. It should not be used directly but through its concerete subclasses.

```python
submit(fn, /, *args, **kwargs)
```

Schedules the callable, _fn_, to be executed as `fn(*args, **kwargs)` and returns a `Future` object representing the execution of the callable.


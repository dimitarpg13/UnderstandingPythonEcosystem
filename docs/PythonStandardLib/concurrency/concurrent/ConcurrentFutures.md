# `concurrent.futures` - Launching parallel tasks

src: [lib/concurrent/futures/thread.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/thread.py) and [lib/concurrent/futures/process.py](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/process.py)

The `cuncurrent.futures` module provides a high-level interface for asynchronously executing callables.

The asynchronous execution can be performed with threads, using `ThreadPoolExecutor`, or separate processes using `ProcessPoolExecutor`. Both implement the same interface which is defined by the abstract `Executor` class. 

## Executor Objects

### _class_ `concurrent.futures`.**Executor**

An abstract class that provides methods to execute calls asynchronously. It should not be used directly but through its concerete subclasses.

  ```python
  submit(fn, /, *args, **kwargs)
  ```

  Schedules the callable, _fn_, to be executed as `fn(*args, **kwargs)` and returns a `Future` object representing the execution of the callable.
  ```python
  with ThreadPoolExecutor(max_workers=1) as executor:
      future = executor.submit(pow, 323, 1235)
      print(future.result())
  ```

  ```python
  map(func, *iterables, timeout=None, chinksize=1) 
  ```

  Similar to `map(func, *iterables)` except:

  * the _iterables_ are collected immediatelly rather than lazily;
  * _func_ is executed asynchronously and several calls to _func_ may be made concurrently.

  The returned iterator raises a `concurrent.futures.TimeoutError` if `__next__()` is called and the result isn't available after _timeout_ seconds from the original call to `Executor.map()`. _timeout_ can be an `int` or a `float`. If _timeout_ is not specified, there is no limit to the wait time.

If a _func_ call raises an exception, then that exception will be raised when its value is retrieved from the iterator.

When using _ProcessPoolExecutor_, this method chops _iterables_ into a number of chunks which it submits to the pool as separate tasks. The (approximate) size of these chunks can be specified by setting _chunksize_ to a positive integer. For a very long iterables, using a large value for _chunksize_ can significantly improve performance compared to the default size of 1. With `ThreadPoolExecutor`, _chunksize_ has no effect.

  ```python
  shutdown(wait=True, *, cancel_futures=False)

  ```

  Signal the executor that it should free any resources that it is using when the currently pending futures are done executing. Calls to `Executor.submit()` and `Executor.map()` made after shutdown will raise `RuntimeError`.
  If _wait_ is `True` then this method will not return until all the pending futures are done executing and the resources associated with the executor have been freed. If _wait_ is `False` then this method will return immediately and the resources associated with the executor will be freed when all pending futures are done executing. Regardless of the value of _wait_, the entire Python program will not exit until all pending futures are done executing.

  If _cancel_futures_ is `True`, this method will cancel all pending futures that the executor has not started running. Any futures that are completed or running won't be cancelled, regardless of the value of _cancel_futures_. 
  If both _cancel_futures_ and _wait_ are `True`, all futures that the executor has started running will be completed prior to this method returning. The remaining futures are cancelled.

  You can avoid haivng to call this method explicitly if you use the `with` statement, which will shutdown the `Executor`  (waiting as if `Executor.shutdown()` were called with _wait_ set to `True`):

  ```python
  import shutil
  with ThreadPoolExecutor(max_workers=4) as e:
      e.submit(shutil.copy, 'src1.txt', 'dest1.txt')
      e.submit(shutil.copy, 'src2.txt', 'dest2.txt')
      e.submit(shutil.copy, 'src3.txt', 'dest3.txt')
      e.submit(shutil.copy, 'src4.txt', 'dest4.txt')
  ```

## `ThreadPoolExecutor`

`ThreadPoolExecutor` is an `Executor` subclass that uses a pool of threads to execute calls asynchronously.

Deadlocks can occur when the callable associated with a `Future` waits on the results of another `Future`


### _class_ `concurrent.futures`.**ThreadPoolExecutor**(_max_workers=None_, _thread_name_prefix=''_, _initializer=None_, _initargs=()_)

  An [`Executor`](#class-concurrentfuturesExecutor) subclass that uses a pool of at most _max_workers_ threads to execute calls asynchronously.

  All threads enqueued to `ThreadPoolExecutor` will be joined before the interpreter can exit. Note that the exit handler which does this is executed _before_ any exit handlers added using _atexit_. This means exceptions in the main thread must be caught and handled in order to signal threads to exit gracefully.  For this reason, it is recommended that `ThreadPoolExecutor` not be used for long-running tasks.

  _initializer_ is an optional callable that is called at the start of each worker thread; _initargs_ is a tuple of arguments passed to the initializer. Should _initializer_ raise an exception, all currently pending jobs will raise a `BrokenThreadPool`, as well as any atempt to submit more jobs to the pool.

  _Changed in ver 3.8_: Default value of _max_workers_ is changed to `min(32, os.cpu_count() + 4)`. This default value preserves at least 5 workers for I/O bound tasks. It utilizes at most 32 CPU cores for CPU bound tasks which release the GIL.  


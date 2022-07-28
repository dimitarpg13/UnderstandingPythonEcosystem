# Coroutines and Tasks

## Coroutines

Coroutines declared with the async/await syntax is the preferred way of writing asyncio apps. 
For example, the following snippet of code prints "hello", waits for 1 second, and then prints "world":

```python
import asyncio

async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(main())

```

Note that simply calling a coroutine will not schedule it to be executed:

```
>>> main()
<coroutine object main at 0x1053bb7c8>
```

To actually run a coroutine, asyncio provides three main mechanisms:

* the `asyncio.run()` function to run the top-level entry point `main()` function

* awaiting on a coroutine. The following snippet of code will print "hello" after waiting for 1 second, 
and then print "world" after waiting for _another_ 2 seconds:

```python
import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"started at {time.strftime('%X')}")

    await say_after(1, 'hello')
    await say_after(2, 'world')

    print(f"finished at {time.strftime{'%X'}}")

asyncio.run(main())
```

Expected output:
```
started at 17:13:52
hello
world
finished at 17:13:55
```

* The `asyncio.create_task()` function to run coroutines concurrently as asyncio Tasks.

Let's modify the above example and run two `say_after` coroutines _concurrently_:

```python
async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # wait until both tasks are completed (should take around 2 seconds)
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")
```

```
started at 17:14:32
hello
world
finished at 17:14:34
```

## Awaitables

We say that an object is an *awaitable* object if it can be used in an await expression. 
Many asyncio APIs are designed to accept awaitables.

There are three main types of _awaitable_ objects: *coroutines*, *Tasks*, and *Futures*.

### Coroutines

Python coroutines are _awaitables_ and therefore can be awaited from other coroutines:

```python
import asyncio

async def nested():
    return 42

async def main():
    # Nothing happens if we just call "nested()".
    # A coroutine object is created but not awaited,
    # so it *won't run at all*.
    nexted()

    # Let's do it differently now and await it:
    print(await nested())

asyncio.run(main())
```

*_Note_*: in this document the term "coroutine" is used for two closely related concepts:

* a _coroutine function_: an `async def` function;

* a _coroutine object_: an object returned by calling a _coroutine function_.
asyncio also supports legacy [generator-based coroutines](#Generator-based-Coroutines).

### Tasks

_Tasks_ are used to schedule coroutines _concurrently_.
When a coroutine is wrapped into a _Task_ with functions like `asyncio.create_task()` the coroutine is automatically 
scheduled to run soon:

```python
import asyncio

async def nested():
    return 42

async def main():
    # Schedule nested() to run soon concurrently
    # with main()
    task = asyncio.create_task(nested())

    # "task" can now be used to cancel "nested()", or 
    # can simply be awaited to wait until it is completee:
    await task

asyncio.run(main())
```

### Futures

A Future is a special *low-level* awaitable object that represents an *eventual result* of an asynchronous operation.

When a Future object is _awaited_ it means that the coroutine will wait until the Future is resolved in some other place.

Future objects in asyncio are needed to allow callback-based code to be used with async/await.

Normally *there is no need* to create Future objects at the application level code. 

Future objects, sometimes exposed by libraries and some asyncio APIs, can be awaited:

```python
async def main():
    await function_that_returns_a_future_object()

    # this is also valid:
    await asyncio.gather(
        function_that_returns_a_future_object(),
        some_python_coroutine()
    )
```

A good example of low-level function that returns a Future object is [loop.run_in_executor()](#loop-run-in-executor)

## Miscelaneous

### Generator-based Coroutines

*_Note_*: Support for generator-based coroutines is *deprecated* since Python 3.8 and is removed in Python 3.11

Generator-based coroutines predate async/await syntax. They are Python generators that use `yield from` expressions to
await on Futures and other coroutines.

Generator-based coroutines should be decorated with `@asyncio.coroutine`, although this is not enforced.
This decorator enables legacy generator-based coroutines to be compatible with async/await code:

```python
@asyncio.coroutine
def old_style_coroutine():
    yield from asyncio.sleep(1)

async def main():
    await old_style_coroutine()

```

`asyncio.iscoroutine(obj)`
    Return `True` if _obj_ is a coroutine object
    This method is different from `inspect.iscoroutine()` because it returns `True` for generator-based coroutines.

`asyncio.iscoroutinefunction(func)`
    Return `True` if _func_ is a coroutine function.
    This method is different from `inspect.iscoroutinefunction()` because it returns `True` for generator-based 
    coroutine functions decorated with `@coroutine`.


### loop run in executor

Syntax:
_awaitable_ `loop.run_in_executor(executor, func, *args)`

  Arrange for _func_ to be called in the specified executor.

  The _executor_ argument should be an `concurrent.futures.Executor` instance. The default executor is used if _executor_ is `None`.

  Example:

  ```python
  import asyncio
  import concurrent.futures

  def blocking_io():
      # File operations (such as logging) can block the
      # event loop: run them in a thread pool.
      with open('/dev/urandom', 'rb') as f:
          return f.read(100)

  def cpu_bound():
      # CPU-bound operations will block the event loop:
      # in general it is preferrable to run them in a
      # process  pool.
      return sum(i * i for i in range(10 ** 7))

  async def main():
      loop = asyncio.get_running_loop()

      ## Options:

      # 1. Run in the default loop's executor:
      result = await loop.run_in_executor(
          None, blocking_io)
      print('default thread pool', result)

      # 2. Run in a custom thread pool:
      with concurrent.futures.ThreadPoolExecutor() as pool:
          result = await loop.run_in_executor(pool, blocking_io)
          print('custom thread pool', result)

      # 3. Run in a custom process pool:
      with concurrent.futures.ProcessPoolExecutor() as pool:
          result = await loop.run_in_executor(pool, cpu_bound)
          print('custom process pool', result)

  asyncio.run(main())
  ```

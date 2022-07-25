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
asyncio also supports legacy [generator-based coroutines](##Generator-based-Coroutines).


## Generator-based Coroutines

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
    coroutine functions decorated with `@coroutine``.


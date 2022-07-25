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



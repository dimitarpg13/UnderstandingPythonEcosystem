# AsyncIO Event Loop

source code: [Lib/asyncio/events.py](https://github.com/python/cpython/blob/3.10/Lib/asyncio/events.py), [Lib/asyncio/base_events.py](https://github.com/python/cpython/blob/3.10/Lib/asyncio/base_events.py)

## Preface

The event loop is the core of every asyncio application. Event loops run asynchronous tasks and callbacks, perform network IO 
operations, and run subprocesses. 

Application developers should typically use high-level asyncio functions, such as `asyncio.run()`, and should rarely need to 
reference the loop object or call its methods. This section is intended mostly for the maintainers of lower-level code, libraries,
and frameworks, who need finer control over the event loop behavior.

## Obtaining the  Event Loop

The following low-level functions can be used to get, set, or create an event loop:

`asyncio.get_running_loop()`
    Return the running event loop in the current OS thread.



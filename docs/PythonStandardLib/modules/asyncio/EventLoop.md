# AsyncIO Event Loop

source code: [Lib/asyncio/events.py](https://github.com/python/cpython/blob/3.10/Lib/asyncio/events.py), [Lib/asyncio/base_events.py](https://github.com/python/cpython/blob/3.10/Lib/asyncio/base_events.py)

## Preface

The event loop is the core of every asyncio application. Event loops run asynchronous tasks and callbacks, perform network IO 
operations, and run subprocesses. 

Application developers should typically use high-level asyncio functions, such as ``



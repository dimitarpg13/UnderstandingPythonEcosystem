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
```
<font color="grey"><coroutine object main at 0x1053bb7c8></font>


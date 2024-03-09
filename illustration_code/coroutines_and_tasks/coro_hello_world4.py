import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

# concurrent execution of coroutines using TaskGroup 
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            say_after(1, 'hello'))
          
        task2 = tg.create_task(
            say_after(2, 'world'))

        print(f"started at {time.strftime('%X')}")

# the await is implicit when the context manager exits
print(f"finished at {time.strftime('%X')}")
        

asyncio.run(main())

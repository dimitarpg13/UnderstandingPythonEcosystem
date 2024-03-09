import asyncio

# call external coroutine using await
async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(main())

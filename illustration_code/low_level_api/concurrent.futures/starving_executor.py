from concurrent.futures import ThreadPoolExecutor

def wait_on_future():
    f = executor.submit(pow, 5, 2)
    # This will never complete because there is only one worker thread
    # and it is executing this function
    print(f.result())

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(wait_on_future)

# this line will be executed but the program will never exit because a lock will never be acquired
print(f"Done!")

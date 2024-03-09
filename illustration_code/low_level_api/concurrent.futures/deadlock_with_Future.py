from concurrent.futures import ThreadPoolExecutor
import time

def wait_on_b():
    time.sleep(5)
    print(b.result()) # b ill never complete because it is waiting on a.
    return 5

def wait_on_a():
    time.sleep(5)
    print(a.result()) # a will never complete because it is waiting on b.
    return 6

executor = ThreadPoolExecutor(max_workers=2)

# the `executor.submit` invocation returns a Future object which must be waited on
a = executor.submit(wait_on_b)
b = executor.submit(wait_on_a)

# this line of code will be executed!
print(f"Done!")

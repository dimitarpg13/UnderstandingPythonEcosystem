

Deadlock with `Future` object - `deadlock_with_Future.py`
```python
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

# this line of code will be executed but the program will never exit!
print(f"Done!")
```


Starving `ThreadPoolExecutor` object - `starving_executor.py`
```python
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
```

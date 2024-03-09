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

# after hitting Ctrl-C we are going to get the following exception due to the fact that lock was not acquired
#
# Exception ignored in: <module 'threading' from '/Users/dimitargueorguiev/.pyenv/versions/3.12.1/lib/python3.12/threading.py'>
# Traceback (most recent call last):
#  File ".../.pyenv/versions/3.12.1/lib/python3.12/threading.py", line 1593, in _shutdown
#    atexit_call()
#  File ".../.pyenv/versions/3.12.1/lib/python3.12/concurrent/futures/thread.py", line 31, in _python_exit
#    t.join()
#  File ".../.pyenv/versions/3.12.1/lib/python3.12/threading.py", line 1147, in join
#    self._wait_for_tstate_lock()
#  File ".../.pyenv/versions/3.12.1/lib/python3.12/threading.py", line 1167, in _wait_for_tstate_lock
#    if lock.acquire(block, timeout):
#       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

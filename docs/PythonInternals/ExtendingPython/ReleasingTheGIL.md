# Releasing the GIL

The GIL is a lock held by the Python interpreter process whenever bytecode is being executed _unless_ it is explicitly released. The design of the cpython interpreter is to assume that everything  occuring in the cpython process between the bytecodes is dangerous and not thread-safe unless told otherwise by the programmer. This means that the lock is enabled by default and that it is periodically released as opposed to the paradigm often seen in many multi-threaded programs where locks are generally not held except when specifically required in so called "critical sections" (parts of code which are not thread safe).

Instead of making any critisisms of or taking any positions on the design of cpython, this article goes through an example of writing a C-extension module and using it to release the cpython GIL. The extension module itself will be about as simple as possibly while still retaining enough complexity to demonstrate both th eneed for and the difficulties of writing `C` extensions that release the GIL.

## A simple `C` extension

## A `C` extension module

Relevant links for writing `C` extensions and building those are [here](https://docs.python.org/3/extending/extending.html) and [here](https://docs.python.org/3/extending/building.html). 


We show how to write a simple `C` extension module. After reading the documents above one can glean that a _minimal_ module is something like this:

`spammodule.c`

```cpp
#include <Python.h>

static struct PyModuleDef spammodule = {
   PyModuleDef_HEAD_INIT,
   "spam", /* name of the module */
};

PyMODINIT_FUNC
PyInit_spam(void) {
   PyObject* m = PyModule_Create(&spammodule);
   if (m == NULL) {
      return NULL;
   }
   return m;
}
```

Next we need to actually _build_ this module in way that python can import. This is most easily done using the `setuptools` module. The following is a  pretty minimal build script:

`setup.py`

```cpp
import os
from setuptools import setup, Extension

module = Extension('spam', sources=['spammodule.c'])

setup(name='spam', ext_modules = [module])
```

If you have both `spammodule.c` and `setup.py` in the current directory the following should build the software:

```python
$ python3 setup.py build
$ python3 setup.py install
```

Test that everything worked by importing your module:

```python
>>> import spam
>>>
```

### Sabotaging our module




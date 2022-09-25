# Extending Python with C or C++

Extension modules can be developed by third parties and can do two things that can't be done in Python: they can implement new built-in object types and they can call C library functions and system calls.

To support extensions, the Python API defines a set of functions, macros and variables that provide access to most apsects of the Python run-time system. The Python API is incorporated in a C source file by including the header "Python.h".

The compilation of an extension module depends on its intended use as well as on your system setup; details are given in later chapters.

**Note**:  The C extension interface is specific to CPython, and extension modules do not work on other Python implementations. In many cases, it is possible to avoid writing C extensions and preserve portability to other implementations. For example, if your use case is calling C library functions or system calls, you should consider using the [ctypes](https://docs.python.org/3/library/ctypes.html#module-ctypes) module or the [cffi](https://cffi.readthedocs.io/en/latest/overview.html) library rather than writing custom C code. These modules let us write Python code to interface with C code and are more portable between implementations of Python than writing and compiling a C extension module. 

## A Simple Example

Let us create an extension module called `spam` and let us say we want to create a Python interface to the C library function `system()`.  This function take a null-terminated character string as argument and returns an integer. We want this function to be callable from Python as follows:

```python
>>> import spam
>>> status = spam.system("ls -l")
```

Begin by creating a file `spammodule.c` (Historically, if a module is called `spam`, the C file containing its implementation is called `spammodule.c`; if the module name is very long, like `spamimify`, the module name can be just `spammify.c` )

The first two lines of the module file are:

```cpp
#define PY_SIZE_T_CLEAN
#include <Python.h>
```

which pullls in the Python API.

**Note**: Since Python may define some pre-processor definitions which affect the standard headers on some systems, you _must_ include `Python.h` before standard headers are included.

It is recommended to always define `PY_SSIZE_T_CLEAN` before including `Python.h`.

All user-visible symbols defined in `Python.h` have a prefix of `Py` or `PY`, except those defined in standard header files. For convenience, and since they are used extensively by the Python interpreter, `"Python.h"` includes a few standard header files: `<stdio.h>`, `<string.h>`, and `<stdlib.h>`. If the latter header file does not exist on your system, it declares the functions `malloc()`, `free()`, and `realloc()` directly.

The next thing we add to our module file is the C function that will be called when the Python expression `spam.system(string)` is evaluated:

```cpp
static PyObject *
spam_system(PyObject *self, PyObject *args)
{
   const char *command;
   int sts;

   if (!PyArg_ParseTuple(args, "s", &command))
      return NULL;
   sts = system(command);
   return PyLong_FromLong(sts);
}
```

There is a straightforward translation from the argument list in Python (for example `"ls -l"`) to the arguments passed to the `C` function. The `C` function always has two arguments, conventionally named _self_ and _args_.

The _self_ argument points to the module object for module-level functions; for a method it would point to the object instance.

The _args_ argument will be a pointer to a Python tuple object containing the arguments. Each item of the tuple corresponds to an argument in the call's argument list. The arguments are Python objects - in order to do anything with them in our `C` function we have to convert them to `C` values. The function 
```cpp
PyArg_ParseTuple(PyObject *args, const char *format, va_list vargs)
```
parses the parameters of a function that takes only positional parameters into local variables. It returns true on success; on failure, it returns `false` and raises an appropriate exception. It checks the argument types and converts them to `C` values. It uses a template string to determine the required types of the arguments as well as the types of the C variables into which to store the converted values. 

`PyArg_ParseTuple()` returns true (nonzero) if all arguments have the right type and its components have been stored in the variables whose addresses are passed. It returns false (zero) if an invalid argument list was passed. In the latter case it also raises an appropriate exception so the calling function can return `NULL` immediately.

## Errors and Exceptions

An important convention throughout the Python interpreter is the following: when a function fails, it should set an exception condition and return an error value (usually `-1` or `NULL` pointer). Exception information is stored in three members of the interpreter's thread state. These are `NULL` if there is no exception. Otherwise, they are the C equivalents of the members of the Python tuple returned by `sys.exc_info()`. These are the exception type, exception instance, and a
traceback object. It is important to know about them to understand how errors are passed around.

The Python API defines a number of functions to set various types of exceptions.

The most common one is `PyErr_SetString()`. Its arguments are an exception objct and a `C` string. The exception object is usually a predefined object like `PyExc_ZeroDivisionError`. The `C` string indicates the cause of the error and is converted to a Python string object and stored as the "associated value" of the exception.

Another useful function is `PyObject *PyError_SetFromErrno(PyObject *type)`, which only takes an exception argument and constructs the associated value by inspection of the global variable `errno`. The most general function is `PyErr_SetObject()`, which takes two object arguments, the exception and its associated value. You don't need to `Py_INCREF()` the objects passed to any of these functions.

One can test non-destructively whether an exception has been set with `PyErr_Occurred()`. This returns the current exception object, or `NULL` if no exception has occurred. You normally don't need to call `PyErr_Occurred()` to see whether an error occurred in a fucntion call, since you should be able to tell from the return value.

When a fucntion _f_ that calls another function _g_ detects that the latter falls, _f_ should itself return an error value (usually `NULL` or `-1`). It should _not_ call one of the `PyErr_`* functions - one has already been called by _g_. _f_'s caller is then supposed to also return an error indication to _its_ caller, again _without_ calling `PyErr_`*, and so on - the most detailed cause of the error was already reported by the function that first detected it. Once the error reaches
the Pthon interpreter's main loop, this aborts the curently executing Python code and tries to find an exception handler by the Python programmer.

To ignore an exception set by a function call that failed, the exception condition must be cleared explicitly by calling `PyErr_Clear()`. The only time `C` code should call `PyErr_clear()` is if it does not want to pass the error on to the interpreter but wants to handle it completely by itself (possibly by trying something else, or pretending nothing went wrong).

Every failing `malloc()` call must be turned into an exception - the direct call of `malloc()` (or `realloc()`) must call `PyErr_FromLong()`) already do this, so this note is only relevant to those who call `malloc()` directly.

Also note that, with the important exception of `PyArg_ParseTuple()` and firends, functions that return an integer status usually return a positive value or zero for success and `-1` for failure like Unix system calls.

FInally, be careful to clean up garbage (by making `Py_XDECREF()` or `Py_DECREF()` calls for objects you have already created) when you return an error indicator.

The choice of which exception to raise is entirely yours. There are predeclared `C` objects corresponding to all built-in Python exceptions, such as `PyExc_ZeroDivisionError`, which you can use directly. Of course exception should be chosen carefully - do not use `PyExc_TypeError` to mean that a file could not be opened (that should probably be `PyExc_IOError`). 

If something is wrong with the argument list, the `PyArg_ParseTuple()` function usually raises `PyExc_TypeError`. IF you have an argument whose value must be in a particular range or must satisify other conditions, `PyExc_ValueError` is appropriate.

You can also define a new exception that is unique to your module. For this, you usually declare a static object variable at the beginning of your file:

```cpp
static PyObject *SpamError;
```

and initialize it in your module's init function (`PyInit_spam()`) with an exception object:

```cpp
PyMODINIT_FUNC
PyInit_spam(void)
{
   PyObject *m;

   m = PyModule_Create(&spammodule);
   if (m == NULL)
      return NULL;

   SpamError = PyErr_NewException("spam.error", NULL, NULL);
   Py_XINCREF(SpamError);
   if (PyModule_AddObject(m, "error", SpamError) < 0) {
      Py_XDECREF(SpamError);
      Py_CLEAR(SpamError);
      Py_DECREF(m);
      return NULL;
   }

   return m;
}
```

Note that the Python name for the exception object is `spam.error`. The `PyErr_NewException()` function may create a class with the base class being `Exception` (unless another class is passed in instead of `NULL`)


_Details on_ `PyErr_NewException`:
```cpp
PyObject *PyErr_NewException(const char* name, PyObject *base, PyObject *dict)
```
return value: new reference
This utility function creates and returns a new exception class. The _name_ argument must be the name of the new exception, a `C` string of the form `module.classname`. The _base_ and _dict_ arguments are normally `NULL`. This creates a class object derived from `Exception` (accessible in `C` as `PyExc_Exception`).

The `__module__` attribute of the new class is set to the first part (up to the last dot) of the _name_ argument, and the class name is set to the last part (after the last dot). The _base_ argument can be used to specify alternate base classes; it can either be only one class or a tuple of classes. The _dict_ argument can be used to specify a dictionary of class variables and methods.

Note also that the `SpamError` variable retains a reference to the newly created exception class; this is intentional! Since the exception could be removed from the module by external code, an owned reference to the class is needed to ensure that it will not be discarded, causing `SpamError` to become a dangling pointer. 
Should it become a dangling pointer, `C` code which raises the exception could cause a core dump or other unintended side effects.

We discuss the use of `PyMODINIT_FUNC` as a function return type later in this sample.

The `spam.error` exception can be raised in your extension module using a call to `PyErr_SetString()` as shown below:

```cpp
static PyObject *
spam_system(PyObject *self, PyObject *args)
{
   const char *command;
   int sts;

   if (!PyArg_ParseTuple(args, "s", &command))
      return NULL;
   sts = system(command);
   if (sts < 0) {
      PyErr_SetString(SpamError, "System command failed");
      return NULL;
   }
   return PyLong_FromLong(sts);
}
```

## Back to the Example

Going back to our example function:

```cpp
if (!PyArg_ParseTuple(args, "s", &command))
   return NULL;
```

It returns `NULL` (the error indicator for functions returning object pointers) if an error is detected in the argument list, relying on the exception set by `PyArg_ParseTuple()`. Otherwise the string value of the argument has been copied to the local variable `command`. 

The next statement is a call to the Unix function `system()`, passing it the string we just got from `PyArg_ParseTuple()`:

```cpp
sts = system(command);
```

Our `spam.system()` function musty return the value of `sts` as a Python obejct. This is done using the function `PyLong_FromLong()`. 
```cpp
return PyLong_FromLong(sts);
```
In this case, it will return an integer object. If you have a `C` function that returns no useful argument (a function returning `void`), the corresponding Python function must return `None`. You need this idiom to do so (which is implemented by the `Py_RETURN_NONE` macro):

```cpp
Py_INCREF(Py_NONE);
return Py_None;
```

`Py_None` is the `C` name for the special Python object `None`. It is a genuine Python object rather than a `NULL` pointer, which means "error" in most contexts, as we have seen.

## The Module's Method Table and Initialization Function

We would like to understand how `spam_system()` is called from Python programs. First, we need to list its name and address in a "method table":

```cpp
static PyMethodDef SpamMethods[] = {
   ...
   {"system", spam_system, METH_VARARGS,
    "Execute a shell command."},
    ...
    {NULL, NULL, 0, NULL}  /* Sentinel */
};
```

Note the third entry (`METH_VARARGS`). This is a flag telling the interpreter the calling convention to be used for the `C` function. It should normally always be `METH_VARARGS` or `METH_VARARGS | METH_KEYWORDS`; a value of `0` means that an obsolete variant of `PyArg_ParseTuple()` is used.

When using only `METH_VARARGS`, the function should expect the Python-level parameters to be passed in as a tuple acceptable for passing via `PyArg_ParseTuple()`; more information on this function is provided below.

The `METH_KEYWORDS` bit may be set in the third field if keyword arguments should be passed to the function. In this case, the `C` function should accept a third `PyObject *` parameter which will be a dictionary of keywords. Use `PyArg_ParseTupleAndKeywords()` to parse the arguments to such a function.

The method table must be referenced in the module definition structure:

```cpp
static struct PyModuleDef spammodule = {
   PyModuleDef_HEAD_INIT,
   "spam",   /* name of the module */
   spam_doc, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the mdodule keeps state in global variables. */
   SpamMethods
};
```

This structure, in turn, must be passed to the interpreter in the module's initialization function. The initialization function must be named `PyInit_name()`, where _name_ is the 
